import json
from typing import List
from openai import OpenAI
from pydantic import ValidationError
from models import AddMembersAction
from config import Config
from exceptions import ValidationError as AppValidationError

Config.validate()
client = OpenAI(api_key=Config.OPENAI_API_KEY)
import json
import re
from typing import List
from openai import OpenAI
from pydantic import ValidationError
from models import AddMembersAction
from config import Config

logger = Config.get_logger("llm_router")

Config.validate()
client = OpenAI(api_key=Config.OPENAI_API_KEY)

SYSTEM = (
    "You convert casual English mailing-list admin requests into JSON ONLY.\n"
    "Output exactly this shape:\n"
    "{ \"actions\": [ { \"action\":\"add_members\", \"list_name\":\"...\", \"emails\":[\"...\", \"...\"] } ] }\n"
    "Rules:\n"
    "- Only action is add_members (batch add).\n"
    "- Extract all emails mentioned (comma/space/and separated) preserving order.\n"
    "- Infer list_name from phrases like 'to ...', 'into ...', 'on ...', or after a colon.\n"
    "- No prose, no extra keys—ONLY the JSON object."
)


def _local_fallback_parse(text: str) -> List[AddMembersAction]:
    """A tiny heuristic parser for offline use. Extracts emails and a probable list name.

    This is intentionally simple and used only when the LLM call fails.
    """
    logger.debug("Using local fallback parser")
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)

    # Try to find a list name after keywords like 'to', 'into', 'on', or after a colon
    list_name = None
    # after a colon
    m = re.search(r":\s*([\w\-]+)", text)
    if m:
        list_name = m.group(1)
    else:
        # 'to the new-members list' or 'to new-members list'
        m = re.search(r"to (the )?([\w\-]+)( list)?", text, re.I)
        if m:
            list_name = m.group(2)

    if not list_name:
        # fallback to a generic list name
        list_name = "default"

    action = AddMembersAction(list_name=list_name, emails=emails)
    return [action]


def parse_user_request(user_text: str, mode: str = "auto") -> List[AddMembersAction]:
    """Parse user text into a list of AddMembersAction models.

    Tries the OpenAI API first, falls back to a small local parser on errors.
    """
    # mode: 'auto' (try LLM, fallback on error), 'llm' (only LLM), 'fallback' (only local)
    if mode not in {"auto", "llm", "fallback"}:
        raise ValueError("mode must be one of: auto, llm, fallback")

    if mode == "fallback":
        return _local_fallback_parse(user_text)

    # mode is 'auto' or 'llm' -> attempt LLM
    try:
        resp = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Request: {user_text}\nReturn ONLY the JSON object."},
            ],
        )

        content = resp.choices[0].message.content
        data = json.loads(content)
        raw_actions = data.get("actions")
        if not isinstance(raw_actions, list):
            logger.warning("LLM returned unexpected shape")
            if mode == "auto":
                return _local_fallback_parse(user_text)
            raise RuntimeError("LLM did not return an 'actions' array.")

        actions: List[AddMembersAction] = []
        for a in raw_actions:
            try:
                actions.append(AddMembersAction(**a))
            except ValidationError as ve:
                logger.error("Validation failed for action from LLM: %s", ve)
                raise RuntimeError(f"Validation failed: {ve}") from ve

        if not actions:
            logger.warning("LLM produced no actions")
            if mode == "auto":
                return _local_fallback_parse(user_text)
            raise RuntimeError("No actions produced.")

        return actions

    except Exception as e:
        logger.exception("LLM call failed: %s", e)
        if mode == "auto":
            return _local_fallback_parse(user_text)
        raise
