import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog
import os

def select_file(filetypes, title):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title=title,
        filetypes=filetypes
    )

def convert_csv_to_excel(csv_path):
    if not csv_path.lower().endswith(".csv"):
        print("❌ Bukan file CSV.")
        return

    try:
        df = pd.read_csv(csv_path, delimiter='|')
        
        # Menentukan path folder untuk menyimpan file yang telah dikonversi
        folder_path = os.path.dirname(csv_path)  # Folder asal file
        converted_folder = os.path.join(folder_path, 'converted_file')

        # Memeriksa apakah folder 'converted_file' sudah ada
        if not os.path.exists(converted_folder):
            print(f"❌ Folder 'converted_file' tidak ditemukan di {folder_path}.")
            return

        # Menentukan path untuk file Excel yang sudah dikonversi
        excel_path = os.path.join(converted_folder, os.path.basename(csv_path).replace('.csv', '.xlsx'))
        
        df.to_excel(excel_path, index=False)
        print(f"✅ Berhasil mengonversi ke Excel:\n{excel_path}")
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat membaca/menulis file:\n{e}")

def convert_excel_to_csv(excel_path):
    if not excel_path.lower().endswith((".xls", ".xlsx")):
        print("❌ Bukan file Excel.")
        return

    try:
        df = pd.read_excel(excel_path)

        # Menentukan path folder untuk menyimpan file yang telah dikonversi
        folder_path = os.path.dirname(excel_path)  # Folder asal file
        converted_folder = os.path.join(folder_path, 'converted_file')

        # Memeriksa apakah folder 'converted_file' sudah ada
        if not os.path.exists(converted_folder):
            print(f"❌ Folder 'converted_file' tidak ditemukan di {folder_path}.")
            return

        # Menentukan path untuk file CSV yang sudah dikonversi
        csv_path = os.path.join(converted_folder, os.path.basename(excel_path).replace('.xlsx', '.csv').replace('.xls', '.csv'))

        df.to_csv(csv_path, sep='|', index=False)
        print(f"✅ Berhasil mengonversi ke CSV:\n{csv_path}")
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat membaca/menulis file:\n{e}")

def run():
    print("🔄 Pilih jenis konversi:")
    print("1. CSV ➜ Excel")
    print("2. Excel ➜ CSV")
    choice = input("Masukkan pilihan (1/2): ")

    if choice == "1":
        print("📂 Pilih file CSV untuk dikonversi ke Excel...")
        csv_path = select_file([("CSV files", "*.csv")], "Pilih file CSV")
        if csv_path:
            convert_csv_to_excel(csv_path)
        else:
            print("🚫 Tidak ada file yang dipilih.")
    elif choice == "2":
        print("📂 Pilih file Excel untuk dikonversi ke CSV...")
        excel_path = select_file([("Excel files", "*.xlsx;*.xls")], "Pilih file Excel")
        if excel_path:
            convert_excel_to_csv(excel_path)
        else:
            print("🚫 Tidak ada file yang dipilih.")
    else:
        print("❌ Pilihan tidak valid. Harap masukkan 1 atau 2.")

if __name__ == "__main__":
    run()