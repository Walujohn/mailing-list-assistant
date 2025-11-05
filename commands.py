import subprocess
from typing import Optional
from dataclasses import dataclass
from exceptions import CommandError

@dataclass
class CommandResult:
    stdout: str
    stderr: str
    returncode: int
    command: str

class CommandExecutor:
    @staticmethod
    def run(cmd: str) -> CommandResult:
        """Execute a shell command and return the result"""
        try:
            cp = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return CommandResult(
                stdout=cp.stdout,
                stderr=cp.stderr,
                returncode=cp.returncode,
                command=cmd
            )
        except Exception as e:
            raise CommandError(f"Failed to execute command: {e}")

    @staticmethod
    def build_add_user_cmd(list_name: str, email: str) -> str:
        """Build the PowerShell command to add a user to a list"""
        # Use -NoProfile and -ExecutionPolicy Bypass so the command runs even when
        # the user's PowerShell profile or execution policy would otherwise block scripts.
        return (
            f'PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File ".\\AddUserToList.ps1" '
            f'-ListName "{list_name}" -Email "{email}"'
        )