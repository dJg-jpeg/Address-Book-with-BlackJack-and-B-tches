from collections import UserDict
from datetime import datetime
from typing import Optional, List
from . import bot_exceptions
from re import search
from abc import abstractmethod, ABC
from contact_book_bot.src.handlers_and_commands.db_management import connect_to_db
from contact_book_bot.src.handlers_and_commands.db_management.db_models import Contact, \
    ContactPhone, ContactBirthday, ContactAddress, ContactEmail, ContactNote, NoteTag

FIELD_NAMES = ('name', 'numbers', 'birthday', 'addresses', 'email', 'notes')


class UserOutput(ABC):

    def __init__(self, data):
        """User output must contain data what to show to user"""
        self.data = data

    @abstractmethod
    def prepare_data_for_output(self):
        """This is the method that puts in readiness for outputting the data , that user requested to see"""


class ContactOutput(UserOutput):

    def prepare_data_for_output(self):
        phones = 'None'
        if len(self.data.phone) > 0:
            phones = ', '.join([phone.value for phone in self.data.phone])
        birthday = 'None'
        if self.data.birthday:
            birthday = self.data.birthday.value.strftime('%d.%m.%Y')
        addresses = 'None'
        if len(self.data.address) > 0:
            addresses = ', '.join([addr.value for addr in self.data.address])
        email = 'None'
        if self.data.email:
            email = self.data.email.value
        notes = ''
        if len(self.data.note) > 0:
            for note in self.data.note:
                notes += f"/'{note.value}', tags: {', '.join([tag.value for tag in note.tag])}/ "
            notes = notes.strip()
        return f"\n|Contact {self.data.name.value} :\n" \
               f"|phones : {phones}\n" \
               f"|birthday : {birthday}\n" \
               f"|addresses : {addresses}\n" \
               f"|email : {email}\n" \
               f"|notes : {notes}\n"


class NoteOutput(UserOutput):

    def prepare_data_for_output(self):
        return f"The note is '{self.data.value}'. And the tags are " \
               f"{','.join([note_tag.value for note_tag in self.data.tag])}"


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
        raw_note = NoteOutput(self)
        return raw_note.prepare_data_for_output()


class Address:
    """ContactAddress of the contact"""

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
        raw_record = ContactOutput(self)
        return raw_record.prepare_data_for_output()

    @staticmethod
    def add_note(input_note: str, contact: Contact, input_tag: Optional[List[str]] = None) -> None:
        note_to_add = ContactNote(
            note=input_note,
            tags=[NoteTag(tag=tag) for tag in input_tag]
        )
        contact.notes.append(note_to_add)
        contact.save()

    @staticmethod
    def get_note(note: str, contact: Contact) -> ContactNote:
        for this_note in contact.notes:
            if this_note.note == note:
                return this_note
        else:
            raise bot_exceptions.UnknownNoteError

    def modify_note(self, note: str, new_note: str, contact: Contact) -> None:
        note_to_modify = self.get_note(note, contact)
        note_to_modify.note = new_note
        contact.save()

    def delete_note(self, note: str, contact: Contact) -> None:
        note_to_delete = self.get_note(note, contact)
        contact.notes.remove(note_to_delete)
        contact.save()

    def add_tag_to_note(self, input_tag: str, note: str, contact: Contact) -> None:
        required_note = self.get_note(note, contact)
        if input_tag not in [contact_note_tag.tag for contact_note_tag in required_note.tags]:
            required_note.tags.append(NoteTag(tag=input_tag))
            contact.save()
        else:
            raise bot_exceptions.ExistTagError

    def search_for_notes(self, search_symbols: str) -> List[Note]:
        found_notes = []
        for note in self.note:
            if search_symbols in note.value:
                found_notes.append(note)
        return found_notes

    @staticmethod
    def modify_email(new_email: str, contact: Contact) -> None:
        Email(new_email)
        if contact.email:
            contact.email.email = new_email
        else:
            contact.email = ContactEmail(email=new_email)
        contact.save()

    def modify_phone(self, old_phone: str, new_phone: str, contact: Contact) -> None:
        if len(self.phone) > 0:
            for this_contact_phone in contact.phones:
                if this_contact_phone.phone == old_phone:
                    contact.phones[contact.phones.index(this_contact_phone)].phone = new_phone
                    contact.save()
                    return None
            raise bot_exceptions.UnknownPhoneError
        else:
            self.add_phone(new_phone, contact)

    def modify_address(self, old_address: str, new_address: str, contact: Contact) -> None:
        if len(self.address) > 0:
            for this_contact_address in contact.addresses:
                if this_contact_address.address == old_address:
                    contact.addresses[contact.addresses.index(this_contact_address)].address = new_address
                    contact.save()
                    return None
            raise bot_exceptions.UnknownAddressError
        else:
            self.add_address(new_address, contact)

    def modify_birthday(self, new_birthday: str, contact: Contact) -> None:
        self.birthday = Birthday(new_birthday)
        if contact.birthday:
            contact.birthday.birthday = self.birthday.value
        else:
            contact.birthday = ContactBirthday(birthday=self.birthday.value)
        contact.save()

    @staticmethod
    def add_phone(new_phone: str, contact: Contact) -> None:
        Phone(new_phone)
        contact.phones.append(ContactPhone(phone=new_phone))
        contact.save()

    @staticmethod
    def add_address(new_address: str, contact: Contact) -> None:
        contact.addresses.append(ContactAddress(address=new_address))
        contact.save()


class AddressBook(UserDict):
    """All contacts data"""

    @staticmethod
    def add_record(record: dict) -> ContactOutput:
        new_record = Record(
            name=record['name'],
            phones=record['numbers'],
            birthday=record['birthday'],
            addresses=record['address'],
            email=record['email'],
        )
        Contact(
            name=record['name'],
            phones=[ContactPhone(phone=phone) for phone in record['numbers']],
            birthday=ContactBirthday(birthday=new_record.birthday.value) if record['birthday'] else None,
            addresses=[ContactAddress(address=address) for address in record['address']],
            email=ContactEmail(email=record['email'])
        ).save()
        return ContactOutput(new_record)

    @staticmethod
    def convert_to_record(contact_in_db: Contact) -> Record:
        contact_phones = [rec_phone.phone for rec_phone in contact_in_db.phones]
        contact_addresses = [rec_address.address for rec_address in contact_in_db.addresses]
        converted_in_record = Record(
            name=contact_in_db.name,
            phones=contact_phones,
            addresses=contact_addresses,
            birthday=contact_in_db.birthday.birthday.strftime("%d.%m.%Y") if contact_in_db.birthday else None,
            email=contact_in_db.email.email,
        )
        for this_note_for_contact in contact_in_db.notes:
            converted_in_record.note.append(
                Note(this_note_for_contact.note, [rec_note_tag.tag for rec_note_tag in this_note_for_contact.tags])
            )
        return converted_in_record

    def find_record(self, sought_string: str) -> dict:
        found_contacts = {
            'by_name': Contact.objects(name__icontains=sought_string),
            'by_phone': Contact.objects(phones__phone__icontains=sought_string),
            'by_email': Contact.objects(email__email__icontains=sought_string),
            'by_address': Contact.objects(addresses__address__icontains=sought_string),
        }
        found_contacts_for_output = {
            'by_name': [],
            'by_phone': [],
            'by_email': [],
            'by_address': [],
        }
        for category, contacts in found_contacts.items():
            for this_contact in contacts:
                this_contact_in_record = self.convert_to_record(this_contact)
                found_contacts_for_output[category].append(str(this_contact_in_record))
        return found_contacts_for_output

    def see_all_contacts(self) -> str:
        all_records = []
        for this_contact in Contact.objects():
            all_records.append(str(self.convert_to_record(this_contact)))
        return '\n'.join(all_records)

    @staticmethod
    def get_record_by_name(name: str) -> Contact:
        founded_contact = Contact.objects(name__iexact=name).first()
        if founded_contact:
            return founded_contact
        else:
            raise bot_exceptions.UnknownContactError

    def delete_record(self, name: str) -> None:
        contact_to_delete = self.get_record_by_name(name)
        contact_to_delete.delete()

    def get_birthdays_by_days(self, days_from_now: int) -> str:
        birthdays_in_future = []
        for this_contact in Contact.objects(birthday__exists=True):
            this_contact_in_record = self.convert_to_record(this_contact)
            if this_contact_in_record.days_to_birthday() == days_from_now:
                birthdays_in_future.append(this_contact.name)
        return f'These people have birthdays in ' \
               f'{days_from_now} days from now: ' \
               f'{",".join(birthdays_in_future) if len(birthdays_in_future) != 0 else "None"}'
