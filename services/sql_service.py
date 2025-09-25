# services/sql_service.py
import re

def format_list_for_sql(values, chunk_size=10):
    """
    Membuat string daftar nilai yang diformat untuk SQL,
    dipisah per baris setiap chunk_size elemen.
    """
    chunks = [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
    return ",\n    ".join(
        [", ".join([f"'{v.strip()}'" for v in chunk]) for chunk in chunks]
    )


def format_sql(template_choice: str, raw_input: str) -> str:
    """
    Memformat daftar NIK/ID menjadi query SQL sesuai template A/B
    (mengacu pada versi Tkinter lama).
    
    Parameters
    ----------
    template_choice : 'A' atau 'B'
    raw_input : string berisi NIK / ID (dipisah spasi atau newline)
    """
    if not raw_input:
        return ""

    all_values = re.split(r"\s+", raw_input.strip())
    nik_values = [v for v in all_values if len(v.strip()) == 16 and v.strip().isdigit()]
    id_values = [v for v in all_values if v not in nik_values]

    if template_choice == "A":
        # Sama seperti versi lama: gabungkan semua ke kolom CIF
        combined = nik_values + id_values
        formatted_values = format_list_for_sql(combined)
        final_query = (
            "SELECT NIK, IDENTIFICATION_NUMBER, CIF, FIRST_NAME, MIDDLE_NAME, LAST_NAME\n"
            "FROM MAV_PROFILE.PROFILE p\n"
            "WHERE p.CIF IN (\n    {values}\n)"
        ).format(values=formatted_values)

    elif template_choice == "B":
        # Versi lama: dua bagian UNION ALL untuk NIK & Identification Number
        query_parts = []

        if nik_values:
            nik_in_clause = format_list_for_sql(nik_values)
            query_nik = f"""
            SELECT t1.KTP_IMAGE, t1.ZOLOZ_IMAGE, t1.NIK
            FROM MAV_PROVISIONING.USER_DOCUMENTUM t1
            JOIN (
                SELECT NIK, MAX(UPDATED_TIME) AS max_updated_time
                FROM MAV_PROVISIONING.USER_DOCUMENTUM ud2
                WHERE NIK IN (
                    {nik_in_clause}
                )
                GROUP BY NIK
            ) t2
            ON t1.NIK = t2.NIK AND t1.updated_time = t2.max_updated_time
            """
            query_parts.append(query_nik.strip())

        if id_values:
            id_in_clause = format_list_for_sql(id_values)
            query_id = f"""
            SELECT t1.KTP_IMAGE, t1.ZOLOZ_IMAGE, t1.IDENTIFICATION_NUMBER AS NIK
            FROM MAV_PROVISIONING.USER_DOCUMENTUM t1
            JOIN (
                SELECT IDENTIFICATION_NUMBER, MAX(UPDATED_TIME) AS max_updated_time
                FROM MAV_PROVISIONING.USER_DOCUMENTUM ud2
                WHERE IDENTIFICATION_NUMBER IN (
                    {id_in_clause}
                )
                GROUP BY IDENTIFICATION_NUMBER
            ) t2
            ON t1.IDENTIFICATION_NUMBER = t2.IDENTIFICATION_NUMBER
               AND t1.updated_time = t2.max_updated_time
            """
            query_parts.append(query_id.strip())

        final_query = "\nUNION ALL\n".join(query_parts)

    else:
        final_query = ""

    return final_query
