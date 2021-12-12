from collections import UserDict
from datetime import datetime
from typing import Optional, List
import re


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


class Tag(Field):
    """Tag for notes of the contact"""

    def __str__(self):
        return f"{self.value}"


class Note(Field):
    """Notes of the contact"""

    def __init__(self, value, tag: List[Tag] = None):
        if tag is None:
            self.tag = []
        else:
            self.tag = [Tag(p) for p in tag]
        super(Note, self).__init__(value)

    def __str__(self):
        return f"The note is '{self.value}'. And the tags are {[p.value for p in self.tag]}"

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        self.__value = value

    def add_tag(self, input_tag: str) -> None:
        tag = Tag(input_tag)
        if tag not in self.tag:
            self.tag.append(tag)


class Address(Field):
    """Address of the contact"""


class Email(Field):
    """Email of the contact"""

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, new_email: str) -> None:
        if re.search(r"[.a-z0-9-_]+@[a-z]{1,8}\.[a-z]{1,3}", new_email) is None:
            raise EmailError
        self.__value = new_email


class AddressBook(UserDict):
    """All contacts data"""

    def add_record(self, record: dict) -> None:
        new_record = Record(name=record['name'],
                            phones=record['numbers'],
                            birthday=record['birthday'],
                            addresses=record['address'],
                            email=record['email'])
        self.data[new_record.name.value] = new_record

    def find_record(self, sought_string: str) -> dict:
        findings = {'by_name': [],
                    'by_phone': [],
                    'by_email': [],
                    'by_address': [],
                    }
        for name, record in self.data.items():
            if sought_string in name:
                findings['by_name'].append(str(record))
            elif sought_string in '|,|'.join([p.value for p in record.phone]):
                findings['by_phone'].append(str(record))
            elif record.email is not None and sought_string in record.email.value:
                findings['by_email'].append(str(record))
            elif sought_string in '|,|'.join(addr.value for addr in record.address):
                findings['by_address'].append(str(record))
        return findings


class Record:
    """Records(contacts) in users contact book.
    Only one name , birthday and email, but it can be more than one phone and more than one address"""

    def __init__(self, name: str,
                 phones: List[str] = None,
                 birthday: str = None,
                 addresses: List[str] = None,
                 email: str = None,
                 note: List[str] = None) -> None:
        self.phone = []
        if phones is not None:
            for p in phones:
                new_phone = Phone()
                new_phone.value = p
                self.phone.append(new_phone)
        self.address = []
        if addresses is not None:
            for this_address in addresses:
                new_address = Address()
                new_address.value = this_address
                self.address.append(new_address)
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

        if note is None:
            self.note = []
        else:
            self.note = [Note(p) for p in note]

    def add_note(self, input_note: str, input_tag: List[str] = None) -> None:
        note_to_add = Note(input_note, input_tag)
        self.note.append(note_to_add)
        return [p.value for p in self.note]

    def find_note(self, note: str) -> Optional[Note]:
        for p in self.note:
            if p.value == note:
                return p

    def delete_note(self, note: str) -> None:
        note_to_delete = self.find_note(note)
        self.note.remove(note_to_delete) if note_to_delete else None

    def __str__(self):
        return f"Record of {self.name.value} has phones {[p.value for p in self.phone]}. And following notes: {[p.value for p in self.note]}"


class AddressBook(UserDict):
    """All contacts data"""

    def add_record(self, record: dict) -> None:
        new_record = Record(name=record['name'],
                            phones=record['numbers'],
                            birthday=record['birthday'],
                            addresses=record['addresses'],
                            email=record['email'])
        self.data[new_record.name.value] = new_record

    def search_for_notes(self, search_symbols: str) -> Optional[Record]:
        contacts = list(self.data.values())
        found_contacts = set()
        for contact in contacts:
            contact_notes = ' '.join([p.value for p in contact.note])
            if search_symbols in contact_notes:
                found_contacts.add(contact)
        return found_contacts

    def __str__(self) -> str:
        phones = ', '.join([p.value for p in self.phone]) if len(
            self.phone) > 0 else 'None'
        birthday = self.birthday.value.strftime(
            '%d.%m.%Y') if self.birthday is not None else 'None'
        addresses = ', '.join([addr.value for addr in self.address]) if len(
            self.address) > 0 else 'None'
        email = self.email.value if self.email is not None else 'None'
        return f"\n|Record of {self.name.value} :\n" \
               f"|phones : {phones}\n" \
               f"|birthday : {birthday}\n" \
               f"|addresses : {addresses}\n" \
               f"|email : {email}\n"
