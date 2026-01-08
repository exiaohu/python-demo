import os
import sys

# Ensure the current directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.cli import cli

if __name__ == "__main__":
    cli()
