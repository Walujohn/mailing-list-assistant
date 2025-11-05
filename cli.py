from typing import Optional
from exceptions import ValidationError

class CLI:
    @staticmethod
    def print_welcome():
        print("mailing-list-assistant (type 'quit' to exit)")
        print("Try things like:")
        print('  add these 3 emails to the new member mailing list: a@x.com, b@x.com and c@x.com\n')

    @staticmethod
    def get_user_input(prompt: str = ">> ") -> str:
        return input(prompt).strip()

    @staticmethod
    def confirm(prompt: str) -> bool:
        return input(f"{prompt} (y/n) ").strip().lower() == "y"

    @staticmethod
    def print_plan(list_name: str, emails: list[str]):
        print(f"\nPlan: add {len(emails)} email(s) to '{list_name}':")
        for email in emails:
            print(f"   {email}")

    @staticmethod
    def print_command(cmd: str):
        print(f"\nAbout to run:\n   {cmd}")

    @staticmethod
    def print_result(result_text: str):
        print(result_text)

    @staticmethod
    def print_error(error_text: str):
        print(f"[ERROR] {error_text}")