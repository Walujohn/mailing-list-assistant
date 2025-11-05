import sys
import argparse
from openai import OpenAI
from config import Config
from commands import CommandExecutor
from cli import CLI
from llm_router import parse_user_request

Config.validate()
client = OpenAI(api_key=Config.OPENAI_API_KEY)

def suggest_fix(result) -> str:
    prompt = (
        "You are a PowerShell troubleshooting assistant. "
        "Given the failed command, return 3–5 concise steps to diagnose/fix it. "
        "Keep it brief and practical for a Windows/PowerShell user.\n\n"
        f"Command:\n{result.command}\n\n"
        f"Return Code: {result.returncode}\n\n"
        f"STDERR:\n{result.stderr}\n\n"
        f"STDOUT:\n{result.stdout}"
    )
    resp = client.chat.completions.create(
        model=Config.OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Be concise, step-by-step, and accurate."},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content.strip()

def execute_command(cmd: str) -> None:
    CLI.print_command(cmd)
    result = CommandExecutor.run(cmd)
    
    print(f"\n[EXECUTING] {cmd}")
    print("[STDOUT]\n" + result.stdout)
    if result.stderr:
        print("[STDERR]\n" + result.stderr, file=sys.stderr)
    print("[RETURN CODE]", result.returncode)

    if result.returncode != 0:
        print("\n--- Troubleshooting suggestions ---")
        tips = suggest_fix(result)
        print(tips)

def main():
    parser = argparse.ArgumentParser(description="mailing-list-assistant")
    parser.add_argument("--yes", "-y", action="store_true", help="auto-approve all prompts and commands")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fallback", action="store_true", help="force local fallback parsing (no LLM)")
    group.add_argument("--llm-only", action="store_true", help="force LLM-only parsing (fail on LLM errors)")
    args = parser.parse_args()

    auto_yes = args.yes
    parse_mode = "auto"
    if args.fallback:
        parse_mode = "fallback"
    elif args.llm_only:
        parse_mode = "llm"

    CLI.print_welcome()

    while True:
        text = CLI.get_user_input()
        if text.lower() in {"quit", "exit"}:
            break

        try:
            actions = parse_user_request(text, mode=parse_mode)
        except Exception as e:
            CLI.print_error(f"Error understanding: {e}")
            continue

        batch = actions[0]
        list_name, emails = batch.list_name, batch.emails

        CLI.print_plan(list_name, emails)

        if not auto_yes and not CLI.confirm("\nProceed?"):
            CLI.print_error("Canceled.")
            continue

        for email in emails:
            cmd = CommandExecutor.build_add_user_cmd(list_name, email)
            if auto_yes or CLI.confirm("Run this command?"):
                execute_command(cmd)
            else:
                CLI.print_error("Skipped.")
        
        CLI.print_result("\nDone.\n")

if __name__ == "__main__":
    main()
