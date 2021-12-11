from collections import UserDict
from datetime import datetime
from typing import List
import re
import csv


FIELD_NAMES = ('name', 'numbers', 'birthday', 'addresses', 'email')
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
                 email: str = None) -> None:
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

    def __str__(self) -> str:
        phones = ', '.join([p.value for p in self.phone]) if len(self.phone) > 0 else 'None'
        birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday is not None else 'None'
        addresses = ', '.join([addr.value for addr in self.address]) if len(self.address) > 0 else 'None'
        email = self.email.value if self.email is not None else 'None'
        return f"\n|Record of {self.name.value} :\n" \
               f"|phones : {phones}\n" \
               f"|birthday : {birthday}\n" \
               f"|addresses : {addresses}\n" \
               f"|email : {email}\n"


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

    def load(self) -> None:
        with open(CONTACTS_PATH, 'r') as tr:
            contacts_reader = csv.DictReader(tr)
            for row in contacts_reader:
                contact_phones = row['numbers'].split(',') if row['numbers'] != 'None' else None
                contact_birthday = row['birthday'] if row['birthday'] != 'None' else None
                contact_addresses = row['addresses'].split(',') if row['addresses'] != 'None' else None
                contact_email = row['email'] if row['email'] != 'None' else None
                self.data[row['name']] = Record(row['name'],
                                                contact_phones,
                                                contact_birthday,
                                                contact_addresses,
                                                contact_email
                                                )

    def save(self) -> None:
        with open(CONTACTS_PATH, 'w') as tw:
            contacts_writer = csv.DictWriter(tw, FIELD_NAMES, )
            contacts_writer.writeheader()
            for name, record in self.data.items():
                contact_phones = ','.join([p.value for p in record.phone]) if len(record.phone) > 0 else 'None'
                if record.birthday is not None:
                    contact_birthday = record.birthday.value.strftime("%d.%m.%Y")
                else:
                    contact_birthday = 'None'
                contact_addresses = ','.join(
                    [addr.value for addr in record.address]
                ) if len(record.address) > 0 else 'None'
                contact_email = record.email.value if record.email is not None else 'None'
                contacts_writer.writerow({'name': name,
                                          'numbers': contact_phones,
                                          'birthday': contact_birthday,
                                          'addresses': contact_addresses,
                                          'email': contact_email,
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
