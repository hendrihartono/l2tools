# app.py
from flask import (
    Flask, render_template, request,
    send_file, redirect, url_for, flash
)
import io
import re
import base64

from services.base64_service import decode_base64_to_bytes
from services.csv_service   import auto_convert
from services.sql_service   import format_sql
from services.daily_fds_service import process_daily_fds_csv

app = Flask(__name__)
# Ganti dengan secret yang panjang/acak untuk produksi
app.secret_key = "ganti_dengan_secret_yang_aman"


# ======================================================
#   MENU UTAMA
# ======================================================
@app.route("/")
def index():
    return render_template("index.html")


# ======================================================
#   BASE64 → IMAGE
# ======================================================
@app.route("/base64", methods=["GET", "POST"])
def base64_page():
    if request.method == "POST":
        text = request.form.get("b64text", "").strip()
        action = request.form.get("action", "show")  # default action

        if not text:
            flash("Masukkan Base64 text dulu", "danger")
            return redirect(url_for("base64_page"))

        try:
            img_bytes = decode_base64_to_bytes(text)

            if action == "download":
                # Download image sebagai file png
                return send_file(
                    io.BytesIO(img_bytes),
                    mimetype="image/png",
                    as_attachment=True,
                    download_name="decoded.png"
                )
            else:
                # Tampilkan langsung di halaman dalam tag <img>
                b64_str = base64.b64encode(img_bytes).decode("utf-8")
                return render_template("base64.html", decoded_image=b64_str, b64text=text)

        except Exception as e:
            flash(f"Gagal decode: {e}", "danger")
            return redirect(url_for("base64_page"))

    # GET method: render halaman kosong
    return render_template("base64.html")


# ======================================================
#   CSV ⇄ EXCEL  (Auto Detect)
# ======================================================
@app.route("/csv-excel", methods=["GET", "POST"])
def csv_excel_page():
    if request.method == "POST":
        f = request.files.get("file")
        if not f:
            flash("Upload satu file dulu", "danger")
            return redirect(url_for("csv_excel_page"))
        try:
            out_io, out_name, mimetype = auto_convert(f.stream, f.filename)
            return send_file(
                out_io,
                as_attachment=True,
                download_name=out_name,
                mimetype=mimetype
            )
        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for("csv_excel_page"))
    return render_template("csv_excel.html")


# ======================================================
#   SQL FORMATTER
# ======================================================
@app.route("/sql-formatter", methods=["GET", "POST"])
def sql_formatter_page():
    """
    Hanya butuh template (A/B) dan raw_input.
    """
    result = None
    if request.method == "POST":
        template = request.form.get("template")
        raw      = request.form.get("raw_input", "")
        try:
            result = format_sql(template, raw)
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("sql_formatter.html", result=result)


# ======================================================
#   DAILY FDS  (CSV -> Images ZIP)
# ======================================================
@app.route("/daily-fds", methods=["GET", "POST"])
def daily_fds_page():
    """
    User mengunggah CSV dengan kolom:
      KTP_base64 | FR_base64 | NIK
    Semua gambar akan di-decode dan di-zip.
    """
    if request.method == "POST":
        f = request.files.get("file")
        zip_name = request.form.get("zip_name", "").strip()

        if not f:
            flash("Upload ketiga.csv dulu", "danger")
            return redirect(url_for("daily_fds_page"))

        # Jika user tidak isi nama, pakai default
        if not zip_name:
            zip_name = "daily fds images"

        # Izinkan huruf, angka, spasi, dash, underscore dan titik
        # Spasi dipertahankan
        safe_name = re.sub(r"[^A-Za-z0-9 _\-.]", "", zip_name).strip() + ".zip"

        try:
            zip_bytes = process_daily_fds_csv(f.stream)
            return send_file(
                zip_bytes,
                as_attachment=True,
                download_name=safe_name,
                mimetype="application/zip"
            )
        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for("daily_fds_page"))

    return render_template("daily_fds.html")


# ======================================================
#   ENTRY POINT
# ======================================================
if __name__ == "__main__":
    # Gunakan host='0.0.0.0' agar bisa diakses dari jaringan lokal
    app.run(debug=True)
