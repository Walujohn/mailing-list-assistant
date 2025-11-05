import json
from types import SimpleNamespace

import llm_router
from models import AddMembersAction


class DummyChoice:
    def __init__(self, content):
        self.message = SimpleNamespace(content=content)


def test_parse_user_request_with_mocked_response(monkeypatch):
    # Prepare fake JSON content the same shape parse_user_request expects
    fake = {"actions": [{"action": "add_members", "list_name": "new-members", "emails": ["a@x.com", "b@x.com"]}]}
    fake_content = json.dumps(fake)

    class DummyResp:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]

    def fake_create(*args, **kwargs):
        return DummyResp(fake_content)

    # Patch the client's chat.completions.create method
    monkeypatch.setattr(llm_router.client.chat.completions, "create", fake_create)

    actions = llm_router.parse_user_request("Add a@x.com and b@x.com to new-members")
    assert len(actions) == 1
    a = actions[0]
    assert isinstance(a, AddMembersAction)
    assert a.list_name == "new-members"
    assert a.emails == ["a@x.com", "b@x.com"]


def test_local_fallback_parse_simple():
    # ensure fallback parsing extracts emails and infers a list name
    actions = llm_router.parse_user_request("Add x@x.com and y@y.com to the special-list", mode="fallback")
    assert len(actions) == 1
    a = actions[0]
    assert a.list_name == "special-list"
    assert a.emails == ["x@x.com", "y@y.com"]
