# Script created to use Gallery-dl set up in multiple folders
# and mass download for each of them. Once each folder is dowloaded,
# it uses the JPG to PNG powershell script to convert them to such
# and then move them to a designated folder based on what that
# script outlines.



import subprocess
import os
import sys
import traceback
from datetime import datetime

BASE_DIR = r"PATH/TO/FILE"
LOG_DIR = os.path.join(BASE_DIR, "Logs")

FOLDERS = ["Folder Name", "Folder Name", "Folder Name"]

def ensure_logs():
    os.makedirs(LOG_DIR, exist_ok=True)

def log_error(folder, error):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(LOG_DIR, f"{folder}_error_{timestamp}.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(error)

def run_command(command, cwd):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(
            f"Command failed:\n{command}\n\n"
            f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        )

def main():
    ensure_logs()

    for folder in FOLDERS:
        folder_path = os.path.join(BASE_DIR, folder)
        ps1_script = os.path.join(folder_path, f"{folder}.ps1")

        try:
            # gallery-dl via PATH (this is the fix)
            run_command(
                "gallery-dl --cookies-from-browser <browser> -i <file>.txt",
                cwd=folder_path
            )

            # PowerShell script
            if not os.path.isfile(ps1_script):
                raise FileNotFoundError(f"Missing PowerShell script: {ps1_script}")

            run_command(
                f'powershell -ExecutionPolicy Bypass -File "{ps1_script}"',
                cwd=folder_path
            )

        except Exception as e:
            error_details = (
                f"Folder: {folder}\n"
                f"Time: {datetime.now()}\n\n"
                f"{str(e)}\n\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            log_error(folder, error_details)
            sys.exit(1)

if __name__ == "__main__":
    main()
