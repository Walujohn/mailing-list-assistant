import os, json
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError
from models import AddMembersAction

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing. Run setup.ps1 and enter your key.")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = (
    "You convert casual English mailing-list admin requests into JSON ONLY.\n"
    'Output exactly this shape:\n'
    '{ "actions": [ { "action":"add_members", "list_name":"...", "emails":["...", "..."] } ] }\n'
    "Rules:\n"
    "- Only action is add_members (batch add).\n"
    "- Extract all emails mentioned (comma/space/and separated) preserving order.\n"
    "- Infer list_name from phrases like 'to ...', 'into ...', 'on ...', or after a colon.\n"
    "- No prose, no extra keys—ONLY the JSON object."
)

def parse_user_request(user_text: str) -> List[AddMembersAction]:
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": f"Request: {user_text}\nReturn ONLY the JSON object."}
        ],
    )

    content = resp.choices[0].message.content
    data = json.loads(content)
    raw_actions = data.get("actions")
    if not isinstance(raw_actions, list):
        raise RuntimeError("LLM did not return an 'actions' array.")

    actions: List[AddMembersAction] = []
    for a in raw_actions:
        try:
            actions.append(AddMembersAction(**a))
        except ValidationError as ve:
            raise RuntimeError(f"Validation failed: {ve}") from ve

    if not actions:
        raise RuntimeError("No actions produced.")
    return actions
