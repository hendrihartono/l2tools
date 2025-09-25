import tkinter as tk
from tkinter import ttk

def apply_custom_format(data):
    delimiter = "\n"
    item_prefix_suffix = "'"
    result_prefix = "("
    result_suffix = ")"
    
    items = [item.strip() for item in data.split(delimiter) if item.strip()]
    formatted_items = [f"{item_prefix_suffix}{item}{item_prefix_suffix}" for item in items]
    result = f"{result_prefix}{','.join(formatted_items)}{result_suffix}"
    return result

def format_data(event=None):
    data = data_text.get("1.0", tk.END).strip()
    query_template = query_text.get("1.0", tk.END).strip()

    formatted_result = apply_custom_format(data)
    
    if "<FORMATTED_RESULT>" in query_template:
        final_query = query_template.replace("<FORMATTED_RESULT>", formatted_result)
    elif query_template:
        final_query = query_template + "\n" + formatted_result
    else:
        final_query = formatted_result

    if orderby_var.get():
        order = orderby_option.get()
        column_name = orderby_column_entry.get().strip()
        if column_name:
            final_query = final_query.rstrip()
            final_query += f"\nORDER BY {column_name} {order}"

    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, final_query)

root = tk.Tk()
root.title("Custom Formatter")

# Query Template input
ttk.Label(root, text="Enter the Query Template:").grid(row=0, column=0, sticky="ne", padx=5, pady=5)
query_text = tk.Text(root, width=60, height=5)
query_text.grid(row=0, column=1, padx=5, pady=5)
query_text.bind("<KeyRelease>", format_data)

# Query Data input
ttk.Label(root, text="Enter the Query Data:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
data_text = tk.Text(root, width=40, height=5)
data_text.grid(row=1, column=1, padx=5, pady=5)
data_text.bind("<KeyRelease>", format_data)

# ORDER BY checkbox and options
orderby_var = tk.BooleanVar()
orderby_check = ttk.Checkbutton(root, text="Add ORDER BY clause", variable=orderby_var, command=format_data)
orderby_check.grid(row=2, column=0, sticky="w", padx=5, pady=5)

orderby_option = ttk.Combobox(root, values=["DESC", "ASC"], width=5, state="readonly")
orderby_option.current(0)
orderby_option.grid(row=2, column=1, sticky="w", padx=5, pady=5)
orderby_option.bind("<<ComboboxSelected>>", format_data)

ttk.Label(root, text="ORDER BY Column:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
orderby_column_entry = ttk.Entry(root, width=20)
orderby_column_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
orderby_column_entry.bind("<KeyRelease>", format_data)
orderby_column_entry.bind("<FocusOut>", format_data)

# Final formatted query output
ttk.Label(root, text="Final Query with Formatted Result:").grid(row=4, column=0, sticky="ne", padx=5, pady=5)
result_text = tk.Text(root, width=60, height=8)
result_text.grid(row=4, column=1, padx=5, pady=5)

root.mainloop()
