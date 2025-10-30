# mailing-list-assistant

Talk to an LLM in casual English to add members to a mailing list.  
You approve each command before it runs.

---

## 🚀 Quick Start

```powershell
git clone https://github.com/<you>/mailing-list-assistant.git
cd mailing-list-assistant
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1               # one time; asks for your OpenAI key and installs deps

# After setup:
# open a NEW PowerShell window so the profile loads, then just type:
mailing-assistant         # or: .\assistant.ps1


🧩 Extending Later (optional)

Want to add new actions (e.g. “show me the total members”)?

Create a new PowerShell script, e.g. GetListCount.ps1.

Add a new Pydantic model in models.py (e.g. GetMemberCountAction).

Update the LLM’s SYSTEM instructions in llm_router.py to support the new action type.

Extend main.py to handle that new action (build the PowerShell command, same approval logic).
