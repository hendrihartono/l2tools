import csv, base64, io, os, re, tempfile, zipfile
from datetime import datetime

csv.field_size_limit(10**7)

def _fix_base64_padding(b64: str) -> str:
    b64 = b64.strip()
    b64 = re.sub(r"\s+", "", b64)
    b64 = re.sub(r"[^A-Za-z0-9+/=_-]", "", b64)
    if len(b64) % 4:
        b64 += "=" * (4 - len(b64) % 4)
    return b64

def _decode_base64_hard(b64: str) -> bytes:
    b64 = _fix_base64_padding(b64)
    try:
        return base64.b64decode(b64, validate=True)
    except Exception:
        pass
    try:
        return base64.urlsafe_b64decode(b64)
    except Exception:
        pass
    for i in range(1,5):
        try:
            return base64.b64decode(b64[:-i], validate=False)
        except Exception:
            continue
    raise ValueError("Base64 decoding failed")

def process_daily_fds_csv(file_stream) -> io.BytesIO:
    # Buat folder sementara
    tmpdir = tempfile.mkdtemp(prefix="daily_fds_")

    # Buat KTP dan FR langsung di root folder sementara
    out_ktp = os.path.join(tmpdir, "KTP")
    out_fr  = os.path.join(tmpdir, "FR")
    os.makedirs(out_ktp, exist_ok=True)
    os.makedirs(out_fr,  exist_ok=True)

    reader = csv.reader(io.TextIOWrapper(file_stream, encoding="utf-8"), delimiter="|")
    rows = list(reader)
    if not rows:
        raise ValueError("CSV kosong")

    for row in rows[1:]:
        if len(row) < 3 or not row[2].strip():
            continue
        nik = row[2].strip()
        for key, col in zip(["KTP", "FR"], [row[0], row[1]]):
            if not col:
                continue
            try:
                img_bytes = _decode_base64_hard(col)
                out_path = os.path.join(out_ktp if key=="KTP" else out_fr,
                                        f"{nik}_{key}.jpg")
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
            except Exception:
                continue

    # Bungkus semua hasil ke ZIP in-memory
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(tmpdir):
            for fn in files:
                zf.write(os.path.join(root, fn),
                         arcname=os.path.relpath(os.path.join(root, fn), tmpdir))
    zip_bytes.seek(0)
    return zip_bytes
