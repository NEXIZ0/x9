import subprocess

def run_command_in_zsh(command):
    try:
        result = subprocess.run(["zsh", "-c", command], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Command failed: {result.stderr}")
            return None
        
        return result.stdout.splitlines()
    except Exception as exc:
        print(f"Error: {exc}")
        return None
    

command = f"rm run.x9 x9.res *passive "
run_command_in_zsh(command)
