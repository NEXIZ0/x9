#!/usr/bin/env python3
import subprocess
import sys
import re
import tempfile

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

def split_into_chunks(file_path, chunk_size=100):
    # Read the contents of the input file and split into chunks of 'chunk_size' lines
    with open(file_path, "r") as f:
        urls = f.readlines()
    
    return [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

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
    
    passive_chunks = split_into_chunks(f"{input_file}.passive")

    # Command 2: Run x9_p2.py with additional options
    try:
        count = 0
        for pchunk in passive_chunks:

            with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
                for url in pchunk:
                    temp_file.write(f"{url.strip()}\n")
                temp_file.flush()
            passiv_file = temp_file.name

            subprocess.run(
                ["python3", x9_p2, "-L", f"{passiv_file}", "-r", "parameter.txt", "-c", "40"],
                check=True
            )
            count += 1
        print(f"sycle of x9_p2 : {count}")
    except subprocess.CalledProcessError as e:
        print(f"Error running x9_p2.py: {e}")
        return

    # Split 'run.x9' into chunks of 200 lines
    url_chunks = split_into_chunks("run.x9")

    # Command 3: Run nuclei for each chunk and save results
    for chunk in url_chunks:
        # Write each chunk into a temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
            for url in chunk:
                temp_file.write(f"{url.strip()}\n")
            temp_file.flush()

        urls_file = temp_file.name
        command = f"nuclei -l {urls_file} -t nuclei_xss.yaml -silent | tee -a x9.res"  # Append results to x9.res
        
        print(f"Running Nuclei command with {len(chunk)} URLs: {command}")
        res = run_command_in_zsh(command)

        if res:
            print(f"Output for chunk ({len(chunk)} URLs):", res)

    # Clean up temporary files (optional)
    cleanup_command = "rm *katana"
    run_command_in_zsh(cleanup_command)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mass_x9.py <input> [-katana]")
        sys.exit(1)

    input_file = sys.argv[1]
    katana_flag = "-katana" in sys.argv

    run_commands(input_file, katana=katana_flag)
