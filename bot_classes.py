from collections import UserDict
from datetime import datetime
from typing import Optional, List
import bot_exceptions
from re import search
from csv import DictReader, DictWriter

FIELD_NAMES = ('name', 'numbers', 'birthday', 'addresses', 'email', 'notes')
CONTACTS_PATH = 'contact_book.csv'


class Name:
    """Name of the contact"""

    def __init__(self, name: str) -> None:
        self.value = name


class Birthday:
    """Birthday of the contact"""

    def __init__(self, birthday: str) -> None:
        try:
            self.value = datetime.strptime(birthday, "%d.%m.%Y")
        except (ValueError, TypeError):
            raise bot_exceptions.BirthdayError("Data must match pattern '%d.%m.%Y'")


class Phone:
    """Phone / phones of the contact"""

    def __init__(self, phone: str) -> None:
        if phone[0] != '+':
            raise bot_exceptions.PhoneError("Phone number must starts from +")
        if not phone[1:].isalnum():
            raise bot_exceptions.PhoneError("Phone must contain only digits")
        self.value = phone


class Tag:
    """Tag for notes of the contact"""

    def __init__(self, tag):
        self.value = tag

    def __str__(self):
        return f"{self.value}"


class Note:
    """Notes of the contact"""

    def __init__(self, note: str, tags: List[str] or list) -> None:  # list of strings or empty list
        self.value = note
        self.tag = []
        if len(tags) > 0:
            self.tag = [Tag(new_tag) for new_tag in tags]

    def __str__(self) -> str:
        return f"The note is '{self.value}'. And the tags are {','.join([p.value for p in self.tag])}"

    def add_tag(self, input_tag: str) -> None:
        all_tags = [tag.value for tag in self.tag]
        if input_tag not in all_tags:
            self.tag.append(Tag(input_tag))


class Address:
    """Address of the contact"""

    def __init__(self, address: str) -> None:
        self.value = address


class Email:
    """Email of the contact"""

    def __init__(self, email: str) -> None:
        if search(r"[.a-z0-9-_]+@[a-z]{1,8}\.[a-z]{1,3}", email) is None:
            raise bot_exceptions.EmailError
        self.value = email


class Record:
    """Records(contacts) in users contact book.
    Only one name , birthday and email, but it can be more than one phone and more than one address"""

    def __init__(
            self,
            name: str,
            phones: List[str] = None,
            birthday: str = None,
            addresses: List[str] = None,
            email: str = None,
    ) -> None:
        self.phone = []
        if phones:
            self.phone = [Phone(new_phone) for new_phone in phones]
        self.address = []
        if addresses:
            self.address = [Address(new_addr) for new_addr in addresses]
        self.name = Name(name)
        if birthday:
            self.birthday = Birthday(birthday)
        else:
            self.birthday = None
        if email:
            self.email = Email(email)
        else:
            self.email = None
        self.note = []

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
        phones = ', '.join([phone.value for phone in self.phone]) if len(self.phone) > 0 else 'None'
        birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday is not None else 'None'
        addresses = ', '.join([addr.value for addr in self.address]) if len(self.address) > 0 else 'None'
        email = self.email.value if self.email is not None else 'None'
        notes = ''
        if len(self.note) > 0:
            for note in self.note:
                notes += f"/'{note.value}', tags: {', '.join([tag.value for tag in note.tag])}/ "
            notes = notes.strip()
        return f"\n|Record of {self.name.value} :\n" \
               f"|phones : {phones}\n" \
               f"|birthday : {birthday}\n" \
               f"|addresses : {addresses}\n" \
               f"|email : {email}\n" \
               f"|notes : {notes}\n"

    def add_note(self, input_note: str, input_tag: Optional[List[str]] = None) -> None:
        note_to_add = Note(input_note, input_tag)
        self.note.append(note_to_add)

    def get_note(self, note: str) -> Note:
        for this_note in self.note:
            if this_note.value == note:
                return this_note
        else:
            raise bot_exceptions.UnknownNoteError

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
        found_contacts = {
            'by_name': [],
            'by_phone': [],
            'by_email': [],
            'by_address': [],
        }
        for name, record in self.data.items():
            if sought_string in name:
                found_contacts['by_name'].append(str(record))
            elif sought_string in '|,|'.join([phone.value for phone in record.phone]):
                found_contacts['by_phone'].append(str(record))
            elif record.email is not None and sought_string in record.email.value:
                found_contacts['by_email'].append(str(record))
            elif sought_string in '|,|'.join(addr.value for addr in record.address):
                found_contacts['by_address'].append(str(record))
        return found_contacts

    def load(self) -> None:
        with open(CONTACTS_PATH, 'r') as tr:
            contacts_reader = DictReader(tr)
            for row in contacts_reader:
                contact_phones = row['numbers'].split(',') if row['numbers'] != 'None' else None
                contact_birthday = row['birthday'] if row['birthday'] != 'None' else None
                contact_addresses = row['addresses'].split(',') if row['addresses'] != 'None' else None
                contact_email = row['email'] if row['email'] != 'None' else None
                if row['notes'] != 'None':
                    raw_notes = (row['notes'].split(','))[:-1]
                    self.data[row['name']] = Record(row['name'], contact_phones, contact_birthday, contact_addresses,
                                                    contact_email)
                    contact = self.get_record_by_name(row['name'])
                    for raw_note in raw_notes:
                        prepared_note, raw_tags = raw_note.split('|tags:|')
                        prepared_tags = raw_tags.split('/|')
                        contact.add_note(prepared_note, prepared_tags)
                else:
                    self.data[row['name']] = Record(row['name'], contact_phones, contact_birthday, contact_addresses,
                                                    contact_email)

    def save(self) -> None:
        with open(CONTACTS_PATH, 'w') as tw:
            contacts_writer = DictWriter(tw, FIELD_NAMES, )
            contacts_writer.writeheader()
            for name, record in self.data.items():
                contact_phones = ','.join([phone.value for phone in record.phone]) \
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
                                 f'{"/|".join([tag.value for tag in this_note.tag]) if len(this_note.tag) > 0 else ""},'
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
            raise bot_exceptions.UnknownContactError

    def delete_record(self, name: str) -> None:
        self.get_record_by_name(name)
        self.data.pop(name)

    def get_birthdays_by_days(self, days_from_now: int) -> str:
        birthdays_in_future = []
        for name, record in self.data.items():
            if record.birthday is not None:
                if record.days_to_birthday() == days_from_now:
                    birthdays_in_future.append(name)
        return f'These people have birthdays in ' \
               f'{days_from_now} days from now: ' \
               f'{",".join(birthdays_in_future) if len(birthdays_in_future) != 0 else "None"}'
