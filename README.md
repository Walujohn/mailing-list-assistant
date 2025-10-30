# mailing-list-assistant

Talk to an LLM in casual English to add members to a mailing list.  
You approve each command before it runs.

## Quick Start
```powershell
git clone https://github.com/<you>/mailing-list-assistant.git
cd mailing-list-assistant
.\setup.ps1
.\assistant.ps1

---

### Extending later (e.g., “show me total members”)
- Add a new PowerShell script (e.g., `GetListCount.ps1`).
- Extend `models.py` with a new action (e.g., `get_member_count`).
- In `llm_router.py`, update the system instructions to allow that action and fields.
- In `main.py`, add the mapping for that action (build the PS command; same approval flow).

