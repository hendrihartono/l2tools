import sys
import os
import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.align import Align
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style

console = Console()

def install_packages():
    packages = [
        "pandas", "openpyxl", "tabulate", "matplotlib", "pillow",
        "sqlparse", "requests", "rich", "prompt_toolkit", "setuptools"
    ]
    console.print("\n[bold yellow]Installing or updating required packages to the latest version...[/bold yellow]\n")
    for pkg in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", pkg])
            console.print(f"[green]✅ Installed/Updated:[/green] {pkg}")
        except subprocess.CalledProcessError:
            console.print(f"[red]❌ Failed to install/update:[/red] {pkg}")
    console.print("\n[bold green]✅ Package installation/update complete.[/bold green]")
    time.sleep(1.5)

def show_menu():
    menu_text = """

░▒▓█▓▒░      ░▒▓███████▓▒░               ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓███████▓▒░░▒▓███████▓▒░░▒▓███████▓▒░  
 ░▒▓█▓▒░             ░▒▓█▓▒░              ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
 ░▒▓█▓▒░             ░▒▓█▓▒░              ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░       ░▒▓██████▓▒░     █████     ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░  
 ░▒▓█▓▒░      ░▒▓█▓▒░                     ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
 ░▒▓█▓▒░      ░▒▓█▓▒░                     ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
 ░▒▓████████▓▒░▒▓████████▓▒░               ░▒▓█████████████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░ 

=== Main Menu ===

1. Recap Transactional Dashboard
2. Base64 to Image
3. SQL Query Formatter GET NIK / ZOLOZ , FR + KTP
4. GTM Report
5. CSV to Excel Converter / Excel to CSV
6. Multiple Query Generator
7. Prod Issue
8. Daily FDS (put ketiga.csv into daily_fds folder)
9. Launch DBeaver
99. Install/Update Required Packages
0. Exit
"""
    console.print(Panel(menu_text, style="cyan"), justify="center")

def run_module(module_path, class_name=None, method="run"):
    try:
        module = __import__(module_path, fromlist=[''])
        if class_name:
            obj = getattr(module, class_name)()
            getattr(obj, method)()
        else:
            getattr(module, method)()
    except Exception:
        console.print(f"\n[red]❌ Error in {module_path}:[/red]")
        console.print_exception()
        return False
    return True

def loading_spinner_behind(message="Loading", duration=3):
    spinner = Spinner("dots", style="green")
    start = time.time()

    with Live(console=console, refresh_per_second=12) as live:
        while time.time() - start < duration:
            elapsed = time.time()
            spinner_text = spinner.render(elapsed)
            loading_text = Text(message + " ", style="bold green")
            loading_text.append(spinner_text)
            live.update(Align(loading_text, align="left"))
            time.sleep(0.1)

    os.system("cls" if os.name == "nt" else "clear")
    console.clear()

def get_user_choice():
    choices = [str(i) for i in range(0, 10)] + ['99']

    style = Style.from_dict({
        '': '#5bb450 bold',
    })

    prompt_text = "Select an option (0–9 or 99): "

    while True:
        choice = prompt(prompt_text, style=style).strip()

        if choice in choices:
            return choice

        console.print("[red bold]⚠️ Invalid choice. only choose 0–9 or 99.[/red bold]")

def main():
    loading_spinner_behind("Loading", 3)
    while True:
        try:
            console.clear()
            show_menu()
            choice = get_user_choice()
            success = False

            if choice == '99':
                install_packages()
                success = True

            elif choice == '1':
                success = run_module("modules.transactional_dashboard")

            elif choice == '2':
                success = run_module("modules.base64_image_converter", "Base64ImageConverterApp")

            elif choice == '3':
                success = run_module("modules.sql_query_formatter", "SQLQueryFormatterApp")

            elif choice == '4':
                success = run_module("modules.gtm_report")

            elif choice == '5':
                success = run_module("modules.csv_to_excel")

            elif choice == '6':
                try:
                    from modules import query_gen
                    query_gen.run()
                    success = True
                except Exception:
                    console.print("\n[red]❌ Error running query_gen module:[/red]")
                    console.print_exception()

            elif choice == '7':
                try:
                    from modules.prod_issue import ProdIssue
                    prod_issue = ProdIssue()
                    prod_issue.run()
                    success = True
                except Exception:
                    console.print("\n[red]❌ Error in modules.prod_issue:[/red]")
                    console.print_exception()

            elif choice == '8':
                success = run_module("modules.daily_fds", method="daily_fds_function")

            elif choice == '9':
                try:
                    dbeaver_path = r"C:\Users\900803\AppData\Local\DBeaver\dbeaver.exe"
                    subprocess.Popen([dbeaver_path])
                    console.print("[green]🚀 DBeaver launched successfully.[/green]")
                    success = True
                except Exception:
                    console.print("\n[red]❌ Failed to launch DBeaver:[/red]")
                    console.print_exception()

            elif choice == '0':
                console.print("[bold red]👋 Goodbye![/bold red]")
                sys.exit()

            if success:
                time.sleep(1)
                console.clear()

        except KeyboardInterrupt:
            console.print("\n[bold red]👋 Exiting... Goodbye![/bold red]")
            sys.exit()
        except Exception:
            console.print("\n[red]❌ Unexpected error occurred:[/red]")
            console.print_exception()
            time.sleep(2)

if __name__ == "__main__":
    main()
