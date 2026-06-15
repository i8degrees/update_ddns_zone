#!.venv/bin/python3

import subprocess

def project_version() -> str:
    """Returns the official version string as per what is stated in the pyproject.toml"""
    return "1.1.1"

def git_revision_hash() -> str:
    """Returns the full git revision hash of the current directory."""
    try:
        # Run the git command to get the output
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        return commit_hash
    except subprocess.CalledProcessError:
        # Handle cases where git is not installed or not in a git repo
        return "Unknown"

def git_revision_short_hash() -> str:
    """Returns the short git revision hash of the current directory."""
    try:
        # Run the git command with the --short option
        commit_hash_short = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        return commit_hash_short
    except subprocess.CalledProcessError:
        return "Unknown"

__gitversion__ = git_revision_short_hash()
__version__ = project_version()

if __name__ == "__main__":
    pass
    #print(f"Git full hash: {get_git_revision_hash()}")
    #print(f"Git short hash: {get_git_revision_short_hash()}")

