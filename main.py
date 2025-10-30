import subprocess, sys
from llm_router import parse_user_request

def ps_add_cmd(list_name: str, email: str) -> str:
    return f'PowerShell.exe -File ".\\AddUserToList.ps1" -ListName "{list_name}" -Email "{email}"'

def run(cmd: str):
    print(f"\n[EXECUTING] {cmd}")
    cp = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("[STDOUT]\n" + cp.stdout)
    if cp.stderr:
        print("[STDERR]\n" + cp.stderr, file=sys.stderr)
    print("[RETURN CODE]", cp.returncode)

def main():
    print("mailing-list-assistant (type 'quit' to exit)")
    print("Try things like:")
    print('  add these 3 emails to the new member mailing list: a@x.com, b@x.com and c@x.com\n')

    while True:
        text = input(">> ").strip()
        if text.lower() in {"quit", "exit"}:
            break

        try:
            actions = parse_user_request(text)   # list with one batch
        except Exception as e:
            print(f"[ERROR understanding]: {e}")
            continue

        batch = actions[0]
        list_name, emails = batch.list_name, batch.emails

        print(f"\nPlan: add {len(emails)} email(s) to '{list_name}':")
        for e in emails:
            print(f"   {e}")

        approve_all = input("\nProceed? (y/n) ").strip().lower()
        if approve_all != "y":
            print("Canceled.\n"); continue

        for e in emails:
            cmd = ps_add_cmd(list_name, e)
            print(f"\nAbout to run:\n   {cmd}")
            approve = input("Run this? (y/n) ").strip().lower()
            if approve == "y":
                run(cmd)
            else:
                print("Skipped.")
        print("\nDone.\n")

if __name__ == "__main__":
    main()
