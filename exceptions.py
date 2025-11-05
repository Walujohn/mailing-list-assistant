class MailingListError(Exception):
    """Base exception for mailing list operations"""
    pass

class CommandError(MailingListError):
    """Error executing a command"""
    pass

class ValidationError(MailingListError):
    """Error validating user input or data"""
    pass