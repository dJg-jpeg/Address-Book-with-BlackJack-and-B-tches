from collections import UserDict
from datetime import datetime
from typing import Optional, List
import re
import csv

FIELD_NAMES = ('name', 'numbers', 'birthday', 'addresses', 'email', 'notes')
CONTACTS_PATH = 'contact_book.csv'


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

    def __init__(self, tags: List[str] = None):
        super(Note, self).__init__()
        self.tag = []
        if len(tags) > 0:
            for this_tag in tags:
                new_tag = Tag()
                new_tag.value = this_tag
                self.tag .append(new_tag)

    def __str__(self):
        return f"The note is '{self.value}'. And the tags are {','.join([p.value for p in self.tag])}"

    def add_tag(self, input_tag: str) -> None:
        all_tags = [tag.value for tag in self.tag]
        if input_tag not in all_tags:
            new_tag = Tag()
            new_tag.value = input_tag
            self.tag.append(new_tag)


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


class Record:
    """Records(contacts) in users contact book.
    Only one name , birthday and email, but it can be more than one phone and more than one address"""

    def __init__(self, name: str,
                 phones: List[str] = None,
                 birthday: str = None,
                 addresses: List[str] = None,
                 email: str = None,
                 notes: List[str] = None) -> None:
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
        self.note = []
        if notes is not None:
            for this_note in notes:
                new_note = Note()
                new_note.value = this_note
                self.phone.append(new_note)

    def days_to_birthday(self) -> int:
        if self.birthday is not None:
            current_date = datetime.now().date()
            this_year_birthday = datetime(
                year=current_date.year,
                month=self.birthday.value.month,
                day=self.birthday.value.day,
            ).date()
            if current_date > this_year_birthday:
                this_year_birthday = datetime(
                    year=current_date.year + 1,
                    month=self.birthday.value.month,
                    day=self.birthday.value.day,
                ).date()
            return (this_year_birthday - current_date).days

    def __str__(self) -> str:
        phones = ', '.join([p.value for p in self.phone]) if len(self.phone) > 0 else 'None'
        birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday is not None else 'None'
        addresses = ', '.join([addr.value for addr in self.address]) if len(self.address) > 0 else 'None'
        email = self.email.value if self.email is not None else 'None'
        notes = ''
        if len(self.note) > 0:
            for note in self.note:
                notes += f"/'{note.value}', tags: {', '.join([t.value for t in note.tag])}/ "
            notes = notes.strip()
        return f"\n|Record of {self.name.value} :\n" \
            f"|phones : {phones}\n" \
            f"|birthday : {birthday}\n" \
            f"|addresses : {addresses}\n" \
            f"|email : {email}\n" \
            f"|notes : {notes}\n"

    def add_note(self, input_note: str, input_tag: Optional[List[str]] = None) -> None:
        note_to_add = Note(input_tag)
        note_to_add.value = input_note
        self.note.append(note_to_add)

    def get_note(self, note: str) -> Optional[Note]:
        for this_note in self.note:
            if this_note.value == note:
                return this_note
        else:
            raise UnknownNoteError

    def modify_note(self, note: str, new_note: str) -> None:
        note_to_modify = self.get_note(note)
        note_to_modify.value = new_note

    def delete_note(self, note: str) -> None:
        note_to_delete = self.get_note(note)
        self.note.remove(note_to_delete)

    def search_for_notes(self, search_symbols: str) -> List[Note]:
        found_notes = []
        for note in self.note:
            if search_symbols in note.value:
                found_notes.append(note)
        return found_notes


class AddressBook(UserDict):
    """All contacts data"""

    def add_record(self, record: dict) -> None:
        new_record = Record(name=record['name'], phones=record['numbers'], birthday=record['birthday'],
                            addresses=record['address'], email=record['email'])
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

    def load(self) -> None:
        with open(CONTACTS_PATH, 'r') as tr:
            contacts_reader = csv.DictReader(tr)
            for row in contacts_reader:
                contact_phones = row['numbers'].split(
                    ',') if row['numbers'] != 'None' else None
                contact_birthday = row['birthday'] if row['birthday'] != 'None' else None
                contact_addresses = row['addresses'].split(
                    ',') if row['addresses'] != 'None' else None
                contact_email = row['email'] if row['email'] != 'None' else None
                if row['notes'] != 'None':
                    raw_notes = (row['notes'].split(','))[:-1]
                    self.data[row['name']] = Record(row['name'], contact_phones, contact_birthday, contact_addresses,
                                                    contact_email)
                    contact = self.get_record_by_name(row['name'])
                    for this_note in raw_notes:
                        this_note = this_note.split('|tags:|')
                        this_note[1] = (this_note[1].split('/|'))
                        contact.add_note(this_note[0], this_note[1])
                else:
                    self.data[row['name']] = Record(row['name'], contact_phones, contact_birthday, contact_addresses,
                                                    contact_email, None)

    def save(self) -> None:
        with open(CONTACTS_PATH, 'w') as tw:
            contacts_writer = csv.DictWriter(tw, FIELD_NAMES, )
            contacts_writer.writeheader()
            for name, record in self.data.items():
                contact_phones = ','.join([p.value for p in record.phone]) \
                    if len(record.phone) > 0 else 'None'
                if record.birthday is not None:
                    contact_birthday = record.birthday.value.strftime("%d.%m.%Y")
                else:
                    contact_birthday = 'None'
                contact_addresses = ','.join(
                    [addr.value for addr in record.address]
                ) if len(record.address) > 0 else 'None'
                notes = ''
                if len(record.note) != 0:
                    for this_note in record.note:
                        notes += f'{this_note.value}' \
                                 f'|tags:|' \
                                 f'{"/|".join([t.value for t in this_note.tag]) if len(this_note.tag) > 0 else ""},'
                else:
                    notes = 'None'
                contact_email = record.email.value if record.email is not None else 'None'
                contacts_writer.writerow({'name': name,
                                          'numbers': contact_phones,
                                          'birthday': contact_birthday,
                                          'addresses': contact_addresses,
                                          'email': contact_email,
                                          'notes': notes,
                                          })

    def see_all_contacts(self) -> str:
        all_records = [str(record) for record in self.data.values()]
        return '\n'.join(all_records)

    def get_record_by_name(self, name: str) -> Record:
        try:
            return self.data[name]
        except KeyError:
            raise UnknownContactError

    def delete_record(self, name: str) -> None:
        self.get_record_by_name(name)
        self.data.pop(name)

    def birthday_list(self, days_from_now: int) -> str:
        birthdays_in_future = []
        for name, record in self.data.items():
            if record.birthday is not None:
                if record.days_to_birthday() == days_from_now:
                    birthdays_in_future.append(name)
        return f'These people have birthdays in ' \
               f'{days_from_now} days from now: ' \
               f'{",".join(birthdays_in_future) if len(birthdays_in_future) != 0 else "None"}'
