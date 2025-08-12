import os, shutil, subprocess
from pathlib import Path

def open_in_terminal(run_cmd):
    term = os.environ.get("TERMINAL")
    if term and shutil.which(term):
        cmd = [term, "-e", "bash", "-lc", run_cmd]
    elif shutil.which("alacritty"):
        cmd = ["alacritty", "-e", "bash", "-lc", run_cmd]
    elif shutil.which("xterm"):
        cmd = ["xterm", "-e", run_cmd]
    else:
        raise RuntimeError("No terminal found. Set $TERMINAL or install one.")
    subprocess.Popen(cmd)


if __name__ == "__main__":
    # Get full path to program.py
    program_path = Path(__file__).parent / "program.py"

    # Activate your venv's Python explicitly
    python_bin = Path(__file__).parent.parent / ".venv" / "bin" / "python"

    # Run program.py in the venv's Python
    open_in_terminal(f"{python_bin} {program_path}")