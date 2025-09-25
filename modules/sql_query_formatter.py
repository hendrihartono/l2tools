import tkinter as tk
from tkinter import messagebox
import re

class SQLQueryFormatterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SQL Query Formatter")
        
        self.template_var = tk.StringVar()
        
        self._build_ui()
        
    def _build_ui(self):
        instructions_label = tk.Label(self.root, text="Select Query Template and Paste Raw Data:")
        instructions_label.pack(padx=10, pady=5)
        
        template_a_radio = tk.Radiobutton(self.root, text="Get NIK + Identification Number", variable=self.template_var, value="A")
        template_a_radio.pack(padx=10, pady=5)
        
        template_b_radio = tk.Radiobutton(self.root, text="Zoloz, FR & KTP Image", variable=self.template_var, value="B")
        template_b_radio.pack(padx=10, pady=5)
        
        value_label = tk.Label(self.root, text="Paste values (one row of raw data):")
        value_label.pack(padx=10, pady=5)
        
        self.value_text = tk.Text(self.root, height=10, width=70)
        self.value_text.pack(padx=10, pady=5)
        
        format_button = tk.Button(self.root, text="Format Query", command=self.on_format_button_click)
        format_button.pack(padx=10, pady=10)
        
        output_label = tk.Label(self.root, text="Formatted SQL Query:")
        output_label.pack(padx=10, pady=5)
        
        self.output_text = tk.Text(self.root, height=25, width=100)
        self.output_text.pack(padx=10, pady=5)

    def format_list_for_sql(self, values, chunk_size=10):
        chunks = [values[i:i+chunk_size] for i in range(0, len(values), chunk_size)]
        formatted = ",\n    ".join([", ".join([f"'{v.strip()}'" for v in chunk]) for chunk in chunks])
        return formatted

    def on_format_button_click(self):
        template_choice = self.template_var.get()
        raw_input = self.value_text.get("1.0", tk.END).strip()
        
        if not raw_input:
            messagebox.showwarning("Input Error", "Please paste the raw data.")
            return
        
        all_values = re.split(r'\s+', raw_input)

        nik_values = [v for v in all_values if len(v.strip()) == 16 and v.strip().isdigit()]
        id_values = [v for v in all_values if len(v.strip()) != 16 or not v.strip().isdigit()]
        
        if not nik_values and not id_values:
            messagebox.showwarning("Filter Result", "Input tidak valid. Harus berisi NIK (16 digit) atau nomor paspor.")
            return

        if template_choice == "A":
            query_template = (
                "SELECT NIK, IDENTIFICATION_NUMBER, CIF, FIRST_NAME, MIDDLE_NAME, LAST_NAME\n"
                "FROM MAV_PROFILE.PROFILE p\n"
                "WHERE p.CIF IN (\n    {values}\n)"
            )
            combined = nik_values + id_values
            formatted_values = self.format_list_for_sql(combined)
            final_query = query_template.format(values=formatted_values)

        elif template_choice == "B":
            query_parts = []

            if nik_values:
                nik_in_clause = self.format_list_for_sql(nik_values)
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
                id_in_clause = self.format_list_for_sql(id_values)
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
                ON t1.IDENTIFICATION_NUMBER = t2.IDENTIFICATION_NUMBER AND t1.updated_time = t2.max_updated_time
                """
                query_parts.append(query_id.strip())

            final_query = "\nUNION ALL\n".join(query_parts)

        else:
            messagebox.showwarning("Template Error", "Please select a query template.")
            return
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, final_query)

    def run(self):
        self.root.mainloop()

# Jalankan aplikasi
if __name__ == "__main__":
    app = SQLQueryFormatterApp()
    app.run()
