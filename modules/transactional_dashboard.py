import os
import sys
import threading
import time
import subprocess
import pandas as pd
import glob
import re
import difflib
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

AUTO_USE_BANK_CODE = True

manual_key_mapping = {
    'Transactional - Multi Transfer Intrabank Dashboard': 'mtint',
    'Transactional - Multi Transfer BI-Fast Dashboard': 'mtbi',
    'Transactional - Mutual Fund Redemption': 'mf',
    'Transactional - Bill Payment Dashboard': 'bp',
    'Transactional - Qris MPM Dashboard': 'qrmpm',
    'Transactional - Qris CPM Dashboard': 'qrcpm',
    'Transactional - ShopeePay Dashboard': 'sp',
    'Transactional - Gopay Dashboard': 'gopay',
    'Transactional - OVO Dashboard': 'ovo',
    'Transactional - Dana Dashboard': 'dana',
    'Transactional - Remittance Dashboard': 'remit',
    'Transactional - RTOL Dashboard': 'rtol',
    'Transactional - Link Aja Dashboard': 'la',
    'Transactional - Tapcash Dashboard': 'tc',
    'Transactional - Schedule Transfer Dashboard': 'sctrf',
    'Transactional - Virtual Account Dashboard': 'va',
    'Transactional - BI-Fast Dashboard': 'bf',
    'Transactional - Intrabank Dashboard': 'int',
    'Transactional - Time Deposit Creation Dashboard': 'tdc',
    'Transactional - Time Deposit Disbursement Dashboard': 'tdd',
    'Transactional - MultiCurrency Account Creation': 'mca',
    'Multicurency Transaction': 'mct',
    'Transactional - Isaku Dashboard': 'isaku'
}

def normalize(text):
    return re.sub(r'\s+', ' ', str(text).strip().lower())

def percentage_to_double(percentage_string):
    return float(str(percentage_string).replace('%', '').strip()) / 100

def add_pivotTable(pivot_data_table: pd.DataFrame) -> pd.DataFrame:
    pivot_table = pd.pivot_table(
        pivot_data_table,
        values=[pivot_data_table.columns[2], pivot_data_table.columns[3]],
        index=[pivot_data_table.columns[4], pivot_data_table.columns[0], pivot_data_table.columns[5]],
        aggfunc='sum',
        margins=True,
        margins_name='Grand Total',
        fill_value=0
    )

    pivot_df = pivot_table.reset_index()
    pivot_df[pivot_data_table.columns[3]] = (pivot_df[pivot_data_table.columns[3]] * 100).astype(str) + '%'
    pivot_df.rename(columns={pivot_data_table.columns[3]: 'Percent (%)'}, inplace=True)

    final_df = pd.DataFrame(columns=pivot_df.columns)
    for error_type in pivot_df[pivot_data_table.columns[4]].unique():
        section = pivot_df[pivot_df[pivot_data_table.columns[4]] == error_type]
        final_df = pd.concat([final_df, section], ignore_index=True)

    empty_row = pd.DataFrame([[''] * len(pivot_df.columns)], columns=pivot_df.columns)
    for _ in range(5):
        final_df = pd.concat([final_df, empty_row])
    
    return final_df

def find_error_and_analysis(key, code, message):
    if not message or str(message).strip() == '(empty)':
        message = "Success"
    
    result = bank_code[(bank_code['key'] == key) & (bank_code['code'] == code)]
    if not result.empty:
        return result['analysis'].values[0], result['error type'].values[0], False
    else:
        print(f"\n🆕 Ditemukan error baru untuk key: '{key}' dan code: '{code}'")
        print(f"📝 Message: {message}")
        analysis = input("Masukkan analysis untuk error ini: ").strip()
        error_type_input = input("Apakah ini technical error? (Y/N): ").strip().lower()
        error_type = "Technical Error" if error_type_input == "y" else "Business Error"
        return analysis, error_type, True

def loading_spinner(duration_sec):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        print(f"Loading... {spinner[idx % len(spinner)]}", end='\r')
        idx += 1
        time.sleep(0.1)
    print(" " * 30, end='\r')

def install_packages():
    packages = [
        "pandas",
        "openpyxl",
        "tabulate",
        "matplotlib",
        "sqlparse",
        "requests"
    ]

    print("\nInstalling required packages...\n")
    for pkg in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install: {pkg}")
        else:
            print(f"✅ Installed: {pkg}")

    print("\nAll packages attempted.")
    print("Press [m] to return to menu or [e] to exit...")

    while True:
        key = get_single_key()
        if key == 'm':
            return
        elif key == 'e':
            print("\nGoodbye!")
            sys.exit()
        else:
            print("\rInvalid key. Press [m] or [e]: ", end='')

def get_single_key():
    try:
        import msvcrt
        return msvcrt.getch().decode('utf-8').lower()
    except ImportError:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def menu():
    print("""
=== Main Menu ===

1. Recap Transactional Dashboard
2. Base64 to Image
3. SQL Query Formatter
4. GTM Report
5. CSV to Excel Converter / Excel to CSV
99. Install Required Packages
0. Exit
""")

def main():
    loading_spinner(3)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    input_folder = os.path.join(base_dir, 'Transactional Dashboard')

    csv_files = glob.glob(os.path.join(input_folder, '*.csv'))
    date_str = datetime.now().strftime("%m%d%Y")
    excel_file = os.path.join(input_folder, f'daily-recap-{date_str}.xlsx')
    new_bank_code_file = os.path.join(input_folder, f'New Bank Code-{date_str}.xlsx')

    new_bc_df = pd.DataFrame(columns=['key', 'code', 'analysis', 'error type'])
    isBankCodeFound = False

    bank_code_candidates = glob.glob(os.path.join(input_folder, '*Bank Code*.xlsx'))
    if AUTO_USE_BANK_CODE and bank_code_candidates:
        bank_code_path = bank_code_candidates[0]
        global bank_code
        bank_code = pd.read_excel(bank_code_path, sheet_name='Bank Code', converters={1: str})
        key_data = pd.read_excel(bank_code_path, sheet_name='Key')
        bank_code.columns = bank_code.columns.str.strip().str.lower()
        key_data['normalized_name'] = key_data['name'].apply(normalize)
        isBankCodeFound = True
        print(f"✅ Bank Code file ditemukan: '{os.path.basename(bank_code_path)}'")

    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        for csv_file in csv_files:
            df = pd.read_csv(csv_file, delimiter='|', converters={1: str})
            sheet_name = os.path.splitext(os.path.basename(csv_file))[0].strip()
            normalized_sheet = normalize(sheet_name)

            df['Error Type'] = ""
            df['Analysis'] = ""

            key = None
            if isBankCodeFound:
                matched_row = key_data[key_data['normalized_name'] == normalized_sheet]
                if not matched_row.empty:
                    key = matched_row['key'].values[0]
                else:
                    closest = difflib.get_close_matches(normalized_sheet, key_data['normalized_name'], n=1, cutoff=0.6)
                    if closest:
                        match_val = closest[0]
                        matched_row = key_data[key_data['normalized_name'] == match_val]
                        key = matched_row['key'].values[0]
                        print(f"🔎 Matched '{sheet_name}' → '{matched_row['name'].values[0]}'")
                    else:
                        # Perbaikan di sini
                        normalized_manual_keys = {normalize(k): v for k, v in manual_key_mapping.items()}
                        if normalized_sheet in normalized_manual_keys:
                            key = normalized_manual_keys[normalized_sheet]
                            print(f"🔑 Manual matched '{sheet_name}' → '{key}'")
                        else:
                            print(f"⚠️ No matching key for '{sheet_name}'. Skipping.")
                            continue

            for index, row in df.iterrows():
                try:
                    df.at[index, df.columns[3]] = percentage_to_double(row[df.columns[3]])
                    count_val = row[df.columns[2]]
                    if isinstance(count_val, str):
                        df.at[index, df.columns[2]] = int(count_val.replace(",", ""))
                    elif not isinstance(count_val, (int, float)):
                        df.at[index, df.columns[2]] = 0
                except Exception as e:
                    print(f"⚠️ Failed processing row {index} in {csv_file}: {e}")
                    continue

                if key is not None:
                    message = row[df.columns[0]]
                    code = row[df.columns[1]]
                    analysis, error_type, is_new = find_error_and_analysis(key, code, message)
                    df.at[index, 'Analysis'] = analysis
                    df.at[index, 'Error Type'] = error_type

                    if is_new:
                        new_bc_df = pd.concat([new_bc_df, pd.DataFrame([[key, code, analysis, error_type]], columns=new_bc_df.columns)])

            df.to_excel(writer, sheet_name=sheet_name, index=False)
        new_bc_df.to_excel(writer, sheet_name="New Bank Code", index=False)

    return excel_file

def run():
    excel_file = main()

    print(f"\n✅ Selesai! Semua file diproses ke '{excel_file}'")

    while True:
        choice = input("\nBack to main menu? (Y/N): ").strip().lower()
        if choice == 'y':
            return
        elif choice == 'n':
            print("Goodbye motherfucker!")
            exit()
        else:
            print("Selection not valid. Type 'Y' for main menu and 'N' to Exit.")

if __name__ == "__main__":
    while True:
        menu()
        try:
            choice = int(input("\nPilih menu (0 untuk keluar): ").strip())
            if choice == 1:
                run()
            elif choice == 99:
                install_packages()
            elif choice == 0:
                print("Goodbye motherfucker!")
                exit()
            else:
                print("Selection not valid.")
        except ValueError:
            print("Selection not valid, Choose only numbers on the menu.")
