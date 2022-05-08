from collections import UserDict
from datetime import datetime
from typing import Optional, List
from . import bot_exceptions
from re import search
from pathlib import Path
from abc import abstractmethod, ABC
from sqlalchemy.orm import sessionmaker
from contact_book_bot.src.handlers_and_commands.db_management.contact_db_models import Contact, \
    ContactPhone, ContactAddress, ContactNote, NoteTag, contact_db_engine

FIELD_NAMES = ('name', 'numbers', 'birthday', 'addresses', 'email', 'notes')
CONTACTS_PATH = Path(__file__).parent.absolute().parent / Path("db_management/contact_book.db")
ContactSession = sessionmaker(bind=contact_db_engine)
ContactSession.configure(bind=contact_db_engine)


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
        raw_record = ContactOutput(self)
        return raw_record.prepare_data_for_output()

    @staticmethod
    def add_note(
            input_note: str,
            contact: Contact,
            adding_note_session: ContactSession,
            input_tag: Optional[List[str]] = None,
    ) -> None:
        note_to_insert = ContactNote(
            note=input_note,
            tags=[NoteTag(tag=tag) for tag in input_tag] if input_tag else None
        )
        contact.notes.append(note_to_insert)
        adding_note_session.commit()
        adding_note_session.close()

    @staticmethod
    def get_note(note: str, contact: Contact) -> ContactNote:
        for this_note in contact.notes:
            if this_note.note == note:
                return this_note
        else:
            raise bot_exceptions.UnknownNoteError

    def add_tag_to_note(self, input_tag: str, note: str, contact: Contact, adding_tag_session: ContactSession) -> None:
        required_note = self.get_note(note, contact)
        required_note.tags.append(NoteTag(tag=input_tag))
        adding_tag_session.commit()

    def modify_note(self, note: str, new_note: str, contact: Contact, changing_note_session: ContactSession) -> None:
        note_to_modify = self.get_note(note, contact)
        note_to_modify.note = new_note
        changing_note_session.commit()
        changing_note_session.close()

    def delete_note(self, note: str, contact: Contact, deleting_note_session: ContactSession) -> None:
        note_to_delete = self.get_note(note, contact)
        deleting_note_session.delete(note_to_delete)
        deleting_note_session.commit()
        deleting_note_session.close()

    def search_for_notes(self, search_symbols: str) -> List[Note]:
        found_notes = []
        for note in self.note:
            if search_symbols in note.value:
                found_notes.append(note)
        return found_notes

    def modify_email(self, new_email: str, contact: Contact, edit_session: ContactSession) -> None:
        self.email = Email(new_email)
        contact.email = new_email
        edit_session.commit()
        edit_session.close()

    def modify_phone(
            self,
            old_phone:
            str, new_phone:
            str, contact: Contact,
            edit_session: ContactSession,
    ) -> None:
        if len(contact.phones) > 0:
            for phone, contact_phone in zip(self.phone, contact.phones):
                if phone.value == old_phone:
                    contact.phones[contact.phones.index(contact_phone)].phone = new_phone
                    edit_session.commit()
                    edit_session.close()
                    return None
            raise bot_exceptions.UnknownPhoneError
        else:
            self.add_phone(new_phone, contact, edit_session)

    def modify_address(
            self,
            old_address: str,
            new_address: str,
            contact: Contact,
            edit_session: ContactSession,
    ) -> None:
        if len(contact.addresses) > 0:
            for address, contact_address in zip(self.address, contact.addresses):
                if address.value == old_address:
                    contact.addresses[contact.addresses.index(contact_address)].address = new_address
                    edit_session.commit()
                    edit_session.close()
                    return None
            raise bot_exceptions.UnknownAddressError
        else:
            self.add_address(new_address, contact, edit_session)

    def modify_birthday(self, new_birthday: str, contact: Contact, edit_session: ContactSession) -> None:
        self.birthday = Birthday(new_birthday)
        contact.birthday = self.birthday.value
        edit_session.commit()
        edit_session.close()

    def add_phone(self, new_phone: str, contact: Contact, adding_info_session: ContactSession) -> None:
        self.phone.append(Phone(new_phone))
        contact.phones.append(ContactPhone(phone=new_phone))
        adding_info_session.commit()
        adding_info_session.close()

    @staticmethod
    def add_address(new_address: str, contact: Contact, adding_info_session: ContactSession) -> None:
        contact.addresses.append(ContactAddress(address=new_address))
        adding_info_session.commit()
        adding_info_session.close()


class AddressBook(UserDict):
    """All contacts data"""

    def add_record(self, record: dict) -> ContactOutput:
        add_record_session = ContactSession()
        try:
            self.get_record_by_name(record['name'])
            add_record_session.close()
            raise bot_exceptions.ExistContactError
        except bot_exceptions.UnknownContactError:
            new_contact_in_record = Record(
                name=record['name'],
                phones=record['numbers'],
                birthday=record['birthday'],
                addresses=record['address'],
                email=record['email'],
            )
            new_contact = Contact(
                name=record['name'],
                birthday=new_contact_in_record.birthday.value if record['birthday'] else None,
                email=record['email'],
                phones=[ContactPhone(phone=phone_number) for phone_number in record['numbers']],
                addresses=[ContactAddress(address=contact_address) for contact_address in record['address']],
            )
            add_record_session.add(new_contact)
            add_record_session.commit()
            add_record_session.close()
            return ContactOutput(new_contact_in_record)

    @staticmethod
    def convert_to_record(contact_in_db: Contact) -> Record:
        contact_phones = [rec_phone.phone for rec_phone in contact_in_db.phones]
        contact_addresses = [rec_address.address for rec_address in contact_in_db.addresses]
        converted_in_record = Record(
            name=contact_in_db.name,
            phones=contact_phones,
            addresses=contact_addresses,
            birthday=contact_in_db.birthday.strftime("%d.%m.%Y") if contact_in_db.birthday else None,
            email=contact_in_db.email,
        )
        for this_note_for_contact in contact_in_db.notes:
            converted_in_record.note.append(
                Note(this_note_for_contact.note, [rec_note_tag.tag for rec_note_tag in this_note_for_contact.tags])
            )
        return converted_in_record

    def find_record(self, sought_string: str) -> dict:
        finding_session = ContactSession()
        found_contacts = {
            'by_name': finding_session.query(Contact).filter(
                Contact.name.ilike(f"%{sought_string}%")
            ).all(),
            'by_phone': finding_session.query(Contact).join(
                ContactPhone, Contact.id == ContactPhone.contact_id).filter(
                ContactPhone.phone.ilike(f"%{sought_string}%")
            ).all(),
            'by_email': finding_session.query(Contact).filter(
                Contact.email.ilike(f"%{sought_string}%")
            ).all(),
            'by_address': finding_session.query(Contact).join(
                ContactAddress, Contact.id == ContactAddress.contact_id).filter(
                ContactAddress.address.ilike(f"%{sought_string}%")
            ).all(),
        }
        found_contacts_for_output = {
            'by_name': [],
            'by_phone': [],
            'by_email': [],
            'by_address': [],
        }
        contact_names = []
        for category, contacts in found_contacts.items():
            for this_contact in contacts:
                this_contact_in_record = self.convert_to_record(this_contact)
                if this_contact_in_record.name.value in contact_names:
                    continue
                contact_names.append(this_contact_in_record.name.value)
                found_contacts_for_output[category].append(this_contact_in_record)
        return found_contacts_for_output

    def see_all_contacts(self) -> list[Record]:
        see_all_session = ContactSession()
        all_records = []
        for this_contact in see_all_session.query(Contact).all():
            new_record = self.convert_to_record(this_contact)
            all_records.append(new_record)
        see_all_session.close()
        return all_records

    @staticmethod
    def get_record_by_name(name: str) -> (Contact, ContactSession):
        get_record_session = ContactSession()
        founded_record = get_record_session.query(Contact).filter(Contact.name == name).first()
        if founded_record:
            return founded_record, get_record_session
        else:
            raise bot_exceptions.UnknownContactError

    def delete_record(self, name: str) -> None:
        contact_to_delete, get_record_session = self.get_record_by_name(name)
        get_record_session.close()
        deleting_session = ContactSession()
        deleting_session.delete(contact_to_delete)
        deleting_session.commit()
        deleting_session.close()

    def get_birthdays_by_days(self, days_from_now: int) -> str:
        birthdays_session = ContactSession()
        birthdays_in_future = []
        for contact in birthdays_session.query(Contact).filter(Contact.birthday is not None):
            record = self.convert_to_record(contact)
            if record.days_to_birthday() == days_from_now:
                birthdays_in_future.append(record.name.value)
        return f'These people have birthdays in ' \
               f'{days_from_now} days from now: ' \
               f'{",".join(birthdays_in_future) if len(birthdays_in_future) != 0 else "None"}'
