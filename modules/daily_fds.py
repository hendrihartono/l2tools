import csv
import base64
import os
import re
import sys
import traceback

# Set max field size (10 MB)
csv.field_size_limit(10**7)

# Direktori output
output_dir_ktp = "daily_fds/images_output_ketiga/KTP"
output_dir_fr = "daily_fds/images_output_ketiga/FR"
os.makedirs(output_dir_ktp, exist_ok=True)
os.makedirs(output_dir_fr, exist_ok=True)

# Path ke file CSV dan log
csv_file_path = "daily_fds/ketiga.csv"
error_log_path = "daily_fds/error_log.txt"
failed_base64_dump = "daily_fds/failed_base64_samples.txt"

# Helper untuk cleaning & padding base64 (lebih agresif)
def fix_base64_padding(b64_string: str) -> str:
    # Hilangkan semua whitespace dan karakter non-base64
    b64 = b64_string.strip()
    b64 = re.sub(r'\s+', '', b64)  # hapus semua whitespace (termasuk tab, newline)
    # hanya biarkan karakter base64 valid, termasuk urlsafe -_
    b64 = re.sub(r'[^A-Za-z0-9+/=_-]', '', b64)
    # Tambahkan padding '=' jika kurang
    missing_padding = len(b64) % 4
    if missing_padding != 0:
        b64 += '=' * (4 - missing_padding)
    return b64

# Hard decode dengan fallback berkali-kali
def decode_base64_hard(b64: str) -> bytes:
    b64 = fix_base64_padding(b64)

    # 1. Try standard decode with validation
    try:
        return base64.b64decode(b64, validate=True)
    except Exception:
        pass

    # 2. Try urlsafe decode
    try:
        return base64.urlsafe_b64decode(b64)
    except Exception:
        pass

    # 3. Try strip trailing chars that may break decode
    for i in range(1,5):
        try_b64 = b64[:-i]
        try:
            return base64.b64decode(try_b64, validate=False)
        except Exception:
            continue

    # 4. If all fail, raise error
    raise ValueError("Base64 decoding failed after multiple attempts")

def save_image(base64_str: str, path: str) -> bool:
    try:
        if not base64_str or not isinstance(base64_str, str):
            raise ValueError("Invalid base64 input (empty or non-string).")

        image = decode_base64_hard(base64_str)

        # Pastikan folder ada (redundant tapi aman)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as f:
            f.write(image)

        print(f"✅ Saved: {path}")
        return True

    except Exception as e:
        print(f"❌ Failed saving {path}: {e}")
        # Print traceback untuk debugging lanjut (bisa di-comment kalau terlalu panjang)
        # traceback.print_exc()
        return False

# Tahap 1: coba simpan, log kegagalan
def process_initial():
    open(error_log_path, 'w').close()
    open(failed_base64_dump, 'w').close()
    with open(csv_file_path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f, delimiter='|'))
    header, rows = reader[0], reader[1:]

    total, success = 0, 0
    with open(error_log_path, 'a', encoding='utf-8') as log, \
         open(failed_base64_dump, 'a', encoding='utf-8') as dump:
        for idx, row in enumerate(rows, start=2):
            if len(row) < 3 or not row[2].strip(): 
                continue
            nik = row[2].strip()
            paths = {
                'KTP': os.path.join(output_dir_ktp, f"{nik}_KTP.jpg"),
                'FR': os.path.join(output_dir_fr, f"{nik}_FR.jpg"),
            }
            for key, col in zip(['KTP','FR'], [row[0], row[1]]):
                if save_image(col, paths[key]):
                    success += 1
                else:
                    log.write(f"{idx}|{key}|{nik}\n")
                    snippet = col[:200] + '...' if len(col) > 200 else col
                    dump.write(f"Row {idx}, {key}, NIK {nik}: {snippet}\n\n")
            total += 1

    print(f"\nInitial done. Processed: {total}, Successful saves: {success}")
    print(f"Errors logged to: {error_log_path}")
    print(f"Sample base64 disimpan di: {failed_base64_dump}")

# Tahap 2: retry yang gagal
def retry_failed():
    if not os.path.exists(error_log_path): 
        return
    with open(error_log_path, 'r', encoding='utf-8') as log:
        entries = [line.strip().split('|') for line in log if line.strip()]
    if not entries: 
        return

    with open(csv_file_path, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter='|'))

    retry_success = 0
    with open(error_log_path, 'w', encoding='utf-8') as log_cleaned:
        for idx_str, key, nik in entries:
            row_idx = int(idx_str) - 2  # adjust index for rows
            row = rows[row_idx + 1]
            base64_str = row[0] if key == 'KTP' else row[1]
            path = os.path.join(
                output_dir_ktp if key == 'KTP' else output_dir_fr,
                f"{nik}_{key}.jpg"
            )
            print(f"↻ Retrying {key} for row {idx_str}, NIK {nik}...")
            if save_image(base64_str, path):
                retry_success += 1
            else:
                log_cleaned.write(f"{idx_str}|{key}|{nik}\n")

    print(f"\nRetry done. New successes: {retry_success}")
    print(f"Remaining failures re-logged in: {error_log_path}")

if __name__ == "__main__":
    process_initial()
    retry_failed()

def daily_fds_function():
    process_initial()
    retry_failed()
