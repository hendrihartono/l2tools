    __  ______ _       __   __________     __  _______ ______
   / / / / __ \ |     / /  /_  __/ __ \   / / / / ___// ____/
  / /_/ / / / / | /| / /    / / / / / /  / / / /\__ \/ __/   
 / __  / /_/ /| |/ |/ /    / / / /_/ /  / /_/ /___/ / /___   
/_/ /_/\____/ |__/|__/    /_/  \____/   \____//____/_____/   
                                                             

FILE STRUCTURE -

L2ToolsV2/
│
├── main.py
├── package.bat
├── start_app.bat
├── daily_fds/
│   ├── (you need to put ketiga.csv file here to run daily_fds)
├── decoded_image/
│   ├── decoded image from Base64 to Image will saved to this folder
├── modules/
│   ├── transactional_dashboard.py
│   ├── base64_image_converter.py
│   ├── sql_query_formatter.py
│   ├── gtm_report.py
│   ├── csv_to_excel.py
│   ├── multiple_query_generator.py
│   ├── prod_issue.py
│   └── daily_fds.py
├── Transactional Dashboard/
│   ├── (you need to put Bank Code Daily file here to run Recap Transactional Dashboard)


PYTHON CLI DASHBOARD UTILITY
============================

This is a Python-based Command Line Interface (CLI) application that provides several tools such as:

- Transactional Dashboard
- Base64 to Image Converter
- SQL Query Formatter
- GTM Report
- CSV to Excel / Excel to CSV Converter
- Multiple Query Generator
- Prod Issue Tool
- Daily FDS Processor

-----------------------------------------
HOW TO USE
-----------------------------------------

There are two ways to run this application:

1. RECOMMENDED (Windows only):
   --------------------------------
   Run the file: packages.bat

   This will:
   - Install all required Python packages

   Just double-click packages.bat or run it from CMD:
   > start packages.bat

2. MANUAL METHOD (If packages are already installed):
   ---------------------------------------------------
   Open CMD or Terminal and run:
   > python main.py

-----------------------------------------
REQUIREMENTS
-----------------------------------------

- Python 3.8 or higher must be installed
- Works best on Windows
- Required packages:
  pandas, openpyxl, tabulate, matplotlib, pillow,
  sqlparse, requests, rich, prompt_toolkit

If you haven't installed them, run:
> package.bat
or use pip:
> pip install pandas openpyxl tabulate matplotlib pillow sqlparse requests rich prompt_toolkit

-----------------------------------------
MENU OPTIONS (AFTER RUNNING main.py)
-----------------------------------------

1 - Recap Transactional Dashboard
2 - Base64 to Image
3 - SQL Query Formatter GET NIK / ZOLOZ , FR + KTP
4 - GTM Report
5 - CSV to Excel Converter / Excel to CSV
6 - Multiple Query Generator
7 - Prod Issue
8 - Daily FDS
99 - Install/Update Required Packages
0 - Exit

-----------------------------------------
NOTES
-----------------------------------------

- The logic for each tool is inside the "modules" folder.
- You can add more tools by creating new Python scripts inside that folder and referencing them in main.py.
- Use Ctrl + C anytime to exit the program.

Enjoy!
