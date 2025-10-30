from typing import List, Literal
from pydantic import BaseModel, EmailStr, Field

class AddMembersAction(BaseModel):
    action: Literal["add_members"] = Field(default="add_members")
    list_name: str = Field(..., description="Target mailing list / distro")
    emails: List[EmailStr] = Field(..., description="One or more emails to add")
