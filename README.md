# mailing-list-assistant

Turn plain-English admin requests into mailing-list actions. You review and approve every command before it runs.

Quick start

1. One-time setup (PowerShell):

```powershell
git clone https://github.com/<you>/mailing-list-assistant.git
cd mailing-list-assistant
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

2. Open a new PowerShell window and run:

```powershell
mailing-assistant  # or: .\assistant.ps1
```

Example

```
add alice@example.com and bob@example.com to the new-members list
```

Notes

- Parsing: user text is validated into `AddMembersAction` (Pydantic).
- LLM: supports `pydantic.ai` or OpenAI SDK fallback.
- Commands: `commands.py` builds & runs PowerShell scripts; `AddUserToList.ps1` is a harmless placeholder.
- Tests: minimal pytest tests are under `tests/`.

Files of interest: `main.py`, `llm_router.py`, `models.py`, `commands.py`, `cli.py`, `config.py`.

If you'd like more examples or CI integration, I can add them.
