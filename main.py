import os
import subprocess
import sys
from dotenv import load_dotenv
from openai import OpenAI
from llm_router import parse_user_request

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def ps_add_cmd(list_name: str, email: str) -> str:
    # Must match your AddUserToList.ps1 parameter names
    return f'PowerShell.exe -File ".\\AddUserToList.ps1" -ListName "{list_name}" -Email "{email}"'

def suggest_fix(command: str, stdout: str, stderr: str, code: int) -> str:
    if client is None:
        return "(No LLM available. Set OPENAI_API_KEY to get troubleshooting tips.)"
    prompt = (
        "You are a PowerShell troubleshooting assistant. "
        "Given the failed command, return 3–5 concise steps to diagnose/fix it. "
        "Keep it brief and practical for a Windows/PowerShell user.\n\n"
        f"Command:\n{command}\n\nReturn Code: {code}\n\nSTDERR:\n{stderr}\n\nSTDOUT:\n{stdout}"
    )
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role":"system","content":"Be concise, step-by-step, and accurate."},
            {"role":"user","content":prompt},
        ],
    )
    return resp.choices[0].message.content.strip()

def run(cmd: str):
    print(f"\n[EXECUTING] {cmd}")
    cp = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("[STDOUT]\n" + cp.stdout)
    if cp.stderr:
        print("[STDERR]\n" + cp.stderr, file=sys.stderr)
    print("[RETURN CODE]", cp.returncode)

    if cp.returncode != 0:
        print("\n--- Troubleshooting suggestions ---")
        tips = suggest_fix(cmd, cp.stdout, cp.stderr, cp.returncode)
        print(tips)

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
