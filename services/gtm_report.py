import pandas as pd
import json
from datetime import datetime, date
import os


base_path = "./data/"


def safe_parse_json(json_str):
    try:
        return json.loads(json_str) if json_str else {}
    except json.JSONDecodeError:
        return {}


def load_csv_file(prompt_name, filename_suffix):
    filename = input(f"Please input {prompt_name} filename (without .csv): ")
    try:
        df = pd.read_csv(base_path + filename + ".csv", sep='|', encoding='utf-8')
        return filename, df
    except FileNotFoundError:
        print(f"❌ File not found for {prompt_name}: {filename}")
        return ask_to_retry()


def ask_to_retry():
    while True:
        retry = input("File not found. Do you want to try again? (y/n): ").strip().lower()
        if retry == 'y':
            return None, None  # Will cause the program to ask again
        elif retry == 'n':
            print("Exiting program.")
            exit()
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def process_wlf(wlf_df):
    wlf_df['isAML'] = ""
    for index, row in wlf_df.iterrows():
        raw_json = str(row["response.body"]).replace('\n', ' ')
        try:
            blob = json.loads(raw_json)
            wlf_df.at[index, 'isAML'] = blob['result']
        except (TypeError, json.JSONDecodeError, KeyError):
            pass
    return wlf_df


def process_ocr(ocr_df):
    ocr_df['error_code'] = ""
    ocr_df['error_desc'] = ""
    for idx, row in ocr_df.iterrows():
        raw_json = str(row["response.body"]).replace('\n', ' ')
        try:
            blob = json.loads(raw_json)
            ocr_df.at[idx, 'error_desc'] = blob.get('errorDesc', '')
            ocr_df.at[idx, 'error_code'] = blob.get('errorCode', '')
        except (TypeError, json.JSONDecodeError, KeyError):
            pass
    ocr_df.drop('response.body', axis=1, inplace=True)
    return ocr_df


def process_isl(isl_df):
    isl_df['response.body'] = isl_df['response.body'].apply(safe_parse_json)
    expanded = pd.json_normalize(isl_df['response.body'])
    result = isl_df.join(expanded)
    drop_cols = [
        'response.body', '@timestamp', 'response.status_code', 'request.uri',
        'app_name', 'context.client_version', 'request.http_method', 'context.client_platform'
    ]
    result.drop(columns=[col for col in drop_cols if col in result.columns], inplace=True)
    return result


def process_zoloz(zoloz_df):
    zoloz_df['@timestamp'] = pd.to_datetime(zoloz_df['@timestamp'], errors='coerce')
    zoloz_df['response.body'] = zoloz_df['response.body'].apply(safe_parse_json)
    response_expanded = pd.json_normalize(zoloz_df['response.body'])
    merged = zoloz_df.join(response_expanded)

    zoloz_df['request.body'] = zoloz_df['request.body'].apply(safe_parse_json)
    request_expanded = pd.json_normalize(zoloz_df['request.body'])
    if 'bizId' in request_expanded:
        merged = merged.join(request_expanded[['bizId']])
    return merged


def process_face_verif(face_df, zoloz_data):
    scenario_df = pd.json_normalize(face_df['response.body'].apply(safe_parse_json))
    scenario_df = scenario_df.rename(columns={'data.scenario': 'scenario'})['scenario']
    face_df = face_df.join(scenario_df)
    face_df.drop(['response.body', 'request.body'], axis=1, inplace=True, errors='ignore')

    merged = pd.merge(face_df, zoloz_data, on='trace_id', how='left')

    scenario_map = {
        'ERROR_PHONE_NOT_MATCH_CORE': 'NIK ditemukan pada CORE, tetapi phone number tidak sesuai',
        'ERROR_PHONE_NOT_MATCH_CARDLINK': 'NIK ditemukan pada Cardlink, tetapi phone number tidak sesuai',
        'ERROR_PHONE_NOT_MATCH_CORE_MBANK': 'NIK ditemukan pada CORE & MBANK, tetapi phone number tidak sesuai',
        'CANNOT_ONBOARD': 'Block by FDS, block by Back Office',
        # Add the rest if needed
    }

    excluded_map = {
        'ETB_FALLBACK_CARD': True,
        'ETB_REACTIVATION': True,
        'ETB_REGISTRATION': True,
    }

    merged['scenario'] = merged.apply(
        lambda row: row['scenario'] if row['scenario'] not in excluded_map else '',
        axis=1
    )

    merged['errorCodeCombined'] = merged.apply(
        lambda row: row['errorCode'] if row.get('errorCode', '') else row['scenario'],
        axis=1
    )

    merged['errorMessageCombined'] = merged.apply(
        lambda row: row['errorMessage'] if row.get('errorCode', '') else scenario_map.get(row['scenario'], ''),
        axis=1
    )

    return merged


def save_outputs(wlf_df, ocr_isl_df, face_df, original_kibana_df, face_verif_filename):
    timestamp = str(datetime.now()).replace(':', '').replace('.', '')
    os.makedirs('./excel/', exist_ok=True)

    with pd.ExcelWriter(f'./excel/kibana_{timestamp}_main.xlsx') as writer:
        wlf_df.to_excel(writer, index=False, sheet_name="kibana" + str(date.today()))
        original_kibana_df.to_excel(writer, index=False, sheet_name="raw")

    with pd.ExcelWriter(f'./excel/ocr_{timestamp}_main.xlsx') as writer:
        ocr_isl_df.to_excel(writer, index=False, sheet_name='OCR')

    with pd.ExcelWriter(f'./excel/{face_verif_filename}_extracted_{timestamp}_main.xlsx') as writer:
        face_df.to_excel(writer, index=False, sheet_name=face_verif_filename)

    print("✅ All reports saved to /excel directory.")


def run():
    print('🔄 Loading and processing, please wait...')

    kibana_file, kibana_df = load_csv_file("Kibana", "")
    if kibana_df is None: return  # If no file, return to main menu

    wlf_file, wlf_df = load_csv_file("WLF", "")
    ocr_file, ocr_df = load_csv_file("Citizenship OCR", "")
    isl_file, isl_df = load_csv_file("ISL/OCR", "")
    zoloz_file, zoloz_df = load_csv_file("Zoloz", "")
    face_file, face_df = load_csv_file("Face Verification", "")

    processed_wlf = process_wlf(wlf_df)
    merged_wlf = pd.merge(kibana_df, processed_wlf[['trace_id', 'isAML']], on='trace_id', how='left')
    merged_wlf.drop(columns=['request.body', 'response.body'], inplace=True, errors='ignore')

    processed_ocr = process_ocr(ocr_df)
    processed_isl = process_isl(isl_df)
    merged_ocr_isl = pd.merge(processed_ocr, processed_isl, on='trace_id', how='left')

    zoloz_data = process_zoloz(zoloz_df)
    face_data = process_face_verif(face_df, zoloz_data)

    save_outputs(merged_wlf, merged_ocr_isl, face_data, kibana_df, face_file)

    print("🎉 GTM Report process completed.")
    input("Press Enter to continue to the main menu...")


def main_menu():
    while True:
        print("\n===== Main Menu =====")
        print("1. Generate GTM Report")
        print("0. Exit")

        choice = input("Please choose an option (1 or 0): ").strip()

        if choice == '1':
            run()
        elif choice == '0':
            print("Goodbye motherfucker!")
            exit()
        else:
            print("Invalid choice! Please choose 1 or 0.")


if __name__ == "__main__":
    main_menu()
