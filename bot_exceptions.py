class ExistContactError(Exception):
    """Contact already exists"""


class PhoneError(Exception):
    """Invalid phone input"""


class BirthdayError(Exception):
    """Unmatched birthday pattern"""


class EmailError(Exception):
    """Invalid email input"""


class InvalidDirectoryPathError(Exception):
    """Invalid directory path"""


class UnknownContactError(Exception):
    """Unknown contact in contact book"""


class UnknownNoteError(Exception):
    """Unknown note in contact book"""


class ZeroDaysError(Exception):
    """Days should be more than 0"""


class LiteralsInDaysError(Exception):
    """Literals were inputted in amount of days argument"""
