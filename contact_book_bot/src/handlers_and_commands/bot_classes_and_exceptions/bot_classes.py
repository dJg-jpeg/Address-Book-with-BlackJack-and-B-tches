from collections import UserDict
from datetime import datetime
from typing import Optional, List
from . import bot_exceptions
from re import search
from csv import DictReader, DictWriter
from pathlib import Path

FIELD_NAMES = ('name', 'numbers', 'birthday', 'addresses', 'email', 'notes')
CONTACTS_PATH = Path(__file__).parent.absolute().parent.parent / Path("contact_book.csv")


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
            raise bot_exceptions.BirthdayError(
                "Data must match pattern '%d.%m.%Y'")


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

    # list of strings or empty list
    def __init__(self, note: str, tags: List[str] or list) -> None:
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
        if not search(r"[.a-z0-9-_]+@[a-z]{1,8}\.[a-z]{1,3}", email):
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
        if self.birthday:
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
        phones = 'None'
        if len(self.phone) > 0:
            phones = ', '.join([phone.value for phone in self.phone])
        birthday = 'None'
        if self.birthday:
            birthday = self.birthday.value.strftime('%d.%m.%Y')
        addresses = 'None'
        if len(self.address) > 0:
            addresses = ', '.join([addr.value for addr in self.address])
        email = 'None'
        if self.email:
            email = self.email.value
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

    def modify_email(self, new_email: str) -> None:
        self.email = Email(new_email)

    def modify_phone(self, old_phone: str, new_phone: str) -> None:
        if self.phone:
            for phone in self.phone:
                if phone.value == old_phone:
                    phone.value = new_phone
                    return None
            raise bot_exceptions.UnknownPhoneError
        else:
            self.add_phone(new_phone)

    def modify_address(self, old_address: str, new_address: str) -> None:
        if self.address:
            for address in self.address:
                if address.value == old_address:
                    address.value = new_address
                    return None
            raise bot_exceptions.UnknownAddressError
        else:
            self.add_address(new_address)

    def modify_birthday(self, new_birthday: str) -> None:
        self.birthday = Birthday(new_birthday)

    def add_phone(self, new_phone: str) -> None:
        self.phone.append(Phone(new_phone))

    def add_address(self, new_address: str) -> None:
        self.address.append(Address(new_address))


class AddressBook(UserDict):
    """All contacts data"""

    def add_record(self, record: dict) -> None:
        new_record = Record(
            name=record['name'],
            phones=record['numbers'],
            birthday=record['birthday'],
            addresses=record['address'],
            email=record['email'],
        )
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
            elif record.email and sought_string in record.email.value:
                found_contacts['by_email'].append(str(record))
            elif sought_string in '|,|'.join(addr.value for addr in record.address):
                found_contacts['by_address'].append(str(record))
        return found_contacts

    def load(self) -> None:
        with open(CONTACTS_PATH, 'r') as tr:
            contacts_reader = DictReader(tr)
            for row in contacts_reader:
                contact_phones = None
                if row['numbers'] != 'None':
                    contact_phones = row['numbers'].split(',')
                contact_birthday = None
                if row['birthday'] != 'None':
                    contact_birthday = row['birthday']
                contact_addresses = None
                if row['addresses'] != 'None':
                    contact_addresses = row['addresses'].split(',')
                contact_email = None
                if row['email'] != 'None':
                    contact_email = row['email']
                if row['notes'] != 'None':
                    raw_notes = (row['notes'].split(','))[:-1]
                    self.data[row['name']] = Record(
                                                row['name'],
                                                contact_phones,
                                                contact_birthday,
                                                contact_addresses,
                                                contact_email,
                                             )
                    contact = self.get_record_by_name(row['name'])
                    for raw_note in raw_notes:
                        prepared_note, raw_tags = raw_note.split('|tags:|')
                        prepared_tags = raw_tags.split('/|')
                        contact.add_note(prepared_note, prepared_tags)
                else:
                    self.data[row['name']] = Record(
                                                row['name'],
                                                contact_phones,
                                                contact_birthday,
                                                contact_addresses,
                                                contact_email,
                                             )

    def save(self) -> None:
        with open(CONTACTS_PATH, 'w') as tw:
            contacts_writer = DictWriter(tw, FIELD_NAMES, )
            contacts_writer.writeheader()
            for name, record in self.data.items():
                contact_phones = 'None'
                if len(record.phone) > 0:
                    contact_phones = ','.join([phone.value for phone in record.phone])
                contact_birthday = 'None'
                if record.birthday:
                    contact_birthday = record.birthday.value.strftime("%d.%m.%Y")
                contact_addresses = 'None'
                if len(record.address) > 0:
                    contact_addresses = ','.join([addr.value for addr in record.address])
                notes = ''
                if len(record.note) != 0:
                    for this_note in record.note:
                        this_note_tags = ""
                        if len(this_note.tag) > 0:
                            this_note_tags = "/|".join([tag.value for tag in this_note.tag])
                        notes += f'{this_note.value}' \
                                 f'|tags:|' \
                                 f'{this_note_tags},'
                else:
                    notes = 'None'
                contact_email = 'None'
                if record.email:
                    contact_email = record.email.value
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
            if record.birthday:
                if record.days_to_birthday() == days_from_now:
                    birthdays_in_future.append(name)
        return f'These people have birthdays in ' \
               f'{days_from_now} days from now: ' \
               f'{",".join(birthdays_in_future) if len(birthdays_in_future) != 0 else "None"}'
