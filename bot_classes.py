from collections import UserDict
from datetime import datetime
from typing import List
import re


class UnknownCommandError(Exception):
    """Unknown command for the bot"""


class ExistContactError(Exception):
    """Contact already exists"""


class PhoneError(Exception):
    """Invalid phone input"""


class BirthdayError(Exception):
    """Unmatched birthday pattern"""


class EmailError(Exception):
    """Invalid email input"""


class Field:
    """Fields of records in contact book : name , phone/phones , etc."""

    def __init__(self):
        self.__value = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Name(Field):
    """Name of the contact"""


class Birthday(Field):
    """Birthday of the contact"""

    @property
    def value(self) -> datetime:
        return self.__value

    @value.setter
    def value(self, new_birthday: str) -> None:
        try:
            self.__value = datetime.strptime(new_birthday, "%d.%m.%Y")
        except (ValueError, TypeError):
            raise BirthdayError("Data must match pattern '%d.%m.%Y'")


class Phone(Field):
    """Phone / phones of the contact"""

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, new_phone: str) -> None:
        if new_phone[0] != '+':
            raise PhoneError("Phone number must starts from +")
        if not new_phone[1:].isalnum():
            raise PhoneError("Phone must contain only digits")
        self.__value = new_phone


class Address(Field):
    """Address of the contact"""


class Email(Field):
    """Email of the contact"""

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, new_email: str) -> None:
        if re.search(r"[.a-z0-9-_]+@[a-z]{2,8}\.[a-z]{1,3}", new_email) is None:
            raise EmailError
        self.__value = new_email


class AddressBook(UserDict):
    """All contacts data"""

    def add_record(self, record: dict) -> None:
        new_record = Record(name=record['name'],
                            phones=record['numbers'],
                            birthday=record['birthday'],
                            addresses=record['addresses'],
                            email=record['email'])
        self.data[new_record.name.value] = new_record


class Record:
    """Records(contacts) in users contact book.
    Only one name , birthday and email, but it can be more than one phone and more than one address"""

    def __init__(self, name: str,
                 phones: List[str] = None,
                 birthday: str = None,
                 addresses: List[str] = None,
                 email: str = None) -> None:
        self.phone = []
        if phones is not None:
            for p in phones:
                new_phone = Phone()
                new_phone.value = p
                self.phone.append(new_phone)
        self.addresses = []
        if addresses is not None:
            for this_address in addresses:
                new_address = Address()
                new_address.value = this_address
                self.addresses.append(new_address)
        self.name = Name()
        self.name.value = name
        if birthday is not None:
            self.birthday = Birthday()
            self.birthday.value = birthday
        else:
            self.birthday = None
        if email is not None:
            self.email = Email()
            self.email.value = email
        else:
            self.email = None
