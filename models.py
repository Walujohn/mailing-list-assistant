from typing import List, Literal
from pydantic import BaseModel, EmailStr, Field

# AI assistant sends email template to members who have sent their funds and optionally continues the whole pipeline flow
class EnterMembersAction(BaseModel):
    action: Literal["receive_new_members"] = Field(default="receive_new_members")
    list_name: str = Field(..., description="Target Teams")
    emails: List[EmailStr] = Field(..., description="One or more members to add along with appropriate actions to take")

# AI assistant reads the docusign pdfs and updates the CAP table with new member
class AddMembersToCAPTable(BaseModel):
    action: Literal["add_members_to_cap"] = Field(default="add_members_to_cap")
    list_name: str = Field(..., description="Target CAP table")
    emails: List[EmailStr] = Field(..., description="One or more members to add to CAP table")

# AI assistant reads the docusign pdfs and updates the CAP table with old member's new information
class AddMembersInformationToCAPTable(BaseModel):
    action: Literal["add_members_information_to_cap"] = Field(default="add_members_information_to_cap")
    list_name: str = Field(..., description="Target CAP table")
    emails: List[EmailStr] = Field(..., description="One or more members information to update in CAP table")

# AI assistant adds new members to mailing lists
class AddMembersAction(BaseModel):
    action: Literal["add_members"] = Field(default="add_members")
    list_name: str = Field(..., description="Target mailing list / distro")
    emails: List[EmailStr] = Field(..., description="One or more emails to add")

#TODO Organize all the actions that an assistant could take over with access to William's terminal logins 
class AddMembersToArchive

class UpdateMembersinArchive

class GenerateDailyBrief
    # Take recording of Will speaking or Will records himself
    # Transcription from Will speaking is taken into account
    # Bot retrieves the Excel workbook in the cloud
    # Bot retrieves the previous 6 Daily Briefs for context
    # Bot generates a new Daily Brief


