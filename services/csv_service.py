# services/csv_service.py
import pandas as pd
import io
import os
from datetime import datetime
from typing import Tuple, BinaryIO

def _timestamp() -> str:
    """Buat string timestamp misal 20250919_1430"""
    return datetime.now().strftime("%Y%m%d_%H%M")

def csv_to_excel_bytes(file_stream: BinaryIO, original_filename: str) -> Tuple[io.BytesIO, str]:
    """
    Konversi CSV menjadi Excel (xlsx), output nama = <nama_asli>_YYYYMMDD_HHMM.xlsx
    """
    import csv
    text = file_stream.read().decode("utf-8", errors="ignore")
    file_stream.seek(0)
    try:
        dialect = csv.Sniffer().sniff(text.splitlines()[0])
        sep = dialect.delimiter
    except Exception:
        sep = ","

    df = pd.read_csv(file_stream, sep=sep, engine="python", quotechar='"', on_bad_lines="skip")
    out_io = io.BytesIO()
    with pd.ExcelWriter(out_io, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    out_io.seek(0)

    base = os.path.splitext(os.path.basename(original_filename))[0]
    out_name = f"{base}_{_timestamp()}.xlsx"
    return out_io, out_name


def excel_to_csv_bytes(file_stream: BinaryIO, original_filename: str, delimiter: str = ",") -> Tuple[io.BytesIO, str]:
    """
    Konversi Excel (xls/xlsx) menjadi CSV, output nama = <nama_asli>_YYYYMMDD_HHMM.csv
    """
    df = pd.read_excel(file_stream, engine="openpyxl")
    out_io = io.BytesIO()
    df.to_csv(out_io, index=False, sep=delimiter)
    out_io.seek(0)

    base = os.path.splitext(os.path.basename(original_filename))[0]
    out_name = f"{base}_{_timestamp()}.csv"
    return out_io, out_name


def auto_convert(file_stream: BinaryIO, filename: str) -> Tuple[io.BytesIO, str, str]:
    """
    Deteksi otomatis: jika filename .csv => ke Excel,
    jika .xls/.xlsx => ke CSV.
    """
    lower = filename.lower()
    if lower.endswith(".csv"):
        out_io, out_name = csv_to_excel_bytes(file_stream, filename)
        return out_io, out_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif lower.endswith((".xlsx", ".xls")):
        out_io, out_name = excel_to_csv_bytes(file_stream, filename)
        return out_io, out_name, "text/csv"
    else:
        raise ValueError("File harus berekstensi .csv, .xls, atau .xlsx")
