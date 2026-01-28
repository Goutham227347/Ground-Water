"""
Helper script to create migrations non-interactively
"""
import subprocess
import sys

# Create migration with default values
result = subprocess.run(
    [sys.executable, 'manage.py', 'makemigrations', '--noinput'],
    input='1\ntimezone.now\n1\ntimezone.now\n',
    text=True,
    cwd='.'
)

sys.exit(result.returncode)
