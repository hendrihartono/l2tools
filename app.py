# app.py
from flask import (
    Flask, render_template, request,
    send_file, redirect, url_for, flash
)
import io
import re
import base64

from services.base64_service import decode_base64_to_bytes
from services.csv_service import auto_convert
from services.sql_service import format_sql
from services.daily_fds_service import process_daily_fds_csv

app = Flask(__name__)
# Ganti dengan secret key yang panjang/acak di produksi
app.secret_key = "ganti_dengan_secret_yang_aman"


# ======================================================
#   MENU UTAMA
# ======================================================
@app.route("/")
def index():
    """Halaman menu utama."""
    return render_template("index.html")


# ======================================================
#   BASE64 → IMAGE
# ======================================================
@app.route("/base64", methods=["GET", "POST"])
def base64_page():
    """
    Dapat menerima input berupa:
      • string base64 langsung
      • atau JSON {"image":"..."} yang berisi field 'image'
    Tombol:
      • Decode & Tampilkan  → menampilkan gambar pada halaman
      • Decode & Download   → mengunduh hasil decode sebagai PNG
    """
    decoded_image = None
    b64text = ""

    if request.method == "POST":
        action = request.form.get("action", "show")
        b64text = request.form.get("b64text", "").strip()

        if not b64text:
            flash("Masukkan Base64 text atau JSON dulu", "danger")
            return redirect(url_for("base64_page"))

        try:
            # Jika input berupa JSON {"image":"..."} ekstrak field image
            if b64text.startswith("{") and "image" in b64text:
                import json
                try:
                    parsed = json.loads(b64text)
                    if isinstance(parsed, dict) and "image" in parsed:
                        b64text = str(parsed["image"])
                except Exception:
                    pass  # Jika gagal parse JSON, gunakan teks apa adanya

            img_bytes = decode_base64_to_bytes(b64text)

            if action == "download":
                return send_file(
                    io.BytesIO(img_bytes),
                    mimetype="image/png",
                    as_attachment=True,
                    download_name="decoded.png"
                )
            else:
                # Encode ulang untuk <img src="data:...">
                decoded_image = base64.b64encode(img_bytes).decode("utf-8")

        except Exception as e:
            flash(f"Gagal decode: {e}", "danger")

    return render_template("base64.html", decoded_image=decoded_image, b64text=b64text)


# ======================================================
#   CSV ⇄ EXCEL  (Auto Detect)
# ======================================================
@app.route("/csv-excel", methods=["GET", "POST"])
def csv_excel_page():
    """Upload file CSV atau Excel, otomatis konversi ke format lawannya."""
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
    Menghasilkan query SQL dari template (A/B) dan daftar input.
    """
    result = None
    if request.method == "POST":
        template = request.form.get("template")
        raw = request.form.get("raw_input", "")
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

        # Hanya izinkan huruf/angka/spasi/underscore/dash/titik
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
    # host='0.0.0.0' agar dapat diakses dari jaringan lokal
    # port bisa diubah sesuai kebutuhan, default 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
