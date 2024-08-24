#!/usr/bin/env python3
import subprocess
import sys
import re

def run_command_in_zsh(command):
    try:
        result = subprocess.run(["zsh", "-c", command], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Command failed: {result.stderr}")
            return None
        
        # Clean up ANSI escape sequences
        cleaned_output = [remove_ansi_sequences(line) for line in result.stdout.splitlines()]
        return cleaned_output
    except Exception as exc:
        print(f"Error: {exc}")
        return None

def remove_ansi_sequences(text):
    ansi_escape = re.compile(r'\x1b\[([0-9;]*[a-zA-Z])')
    return ansi_escape.sub('', text)

def run_commands(input_file, katana=False):
    # Command 1: Run x9_p1.py with or without the -katana flag
    x9_p1 = "/nexiz/Tools/x9/x9_p1.py"
    x9_p2 = "/nexiz/Tools/x9/x9_p2.py"
    
    try:
        if katana:
            subprocess.run(["python3", x9_p1, input_file, "-katana"], check=True)
        else:
            subprocess.run(["python3", x9_p1, input_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running x9_p1.py: {e}")
        return

    # Command 2: Run x9_p2.py with additional options
    try:
        subprocess.run(
            ["python3", x9_p2, "-L", f"{input_file}.passive", "-r", "parameter.txt", "-c", "40"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running x9_p2.py: {e}")
        return

    # Command 3: Run nuclei with the output and save results
    command = "cat run.x9 | nuclei -t nuclei_xss.yaml -silent | tee x9.res"
    res = run_command_in_zsh(command)

    if res:
        print("Cleaned Output:", res)
        # Clean up temporary files
        cleanup_command = "rm *katana"
        run_command_in_zsh(cleanup_command)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mass_x9.py <input> [-katana]")
        sys.exit(1)

    input_file = sys.argv[1]
    katana_flag = "-katana" in sys.argv

    run_commands(input_file, katana=katana_flag)
