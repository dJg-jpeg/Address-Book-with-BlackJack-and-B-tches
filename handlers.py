import bot_classes
from typing import Optional
import dir_sorter


def greetings() -> str:
    return f"Hi!\n" \
           f"My list of commands is : {', '.join(list(COMMANDS.keys()))}\n" \
           f"How can I help you?"


def add_contact(contact: dict, contacts_book: bot_classes.AddressBook) -> Optional[str]:
    if contact['name'] in contacts_book.keys():
        raise bot_classes.ExistContactError
    contacts_book.add_record(contact)
    return f"You successfully added {contact['name']} contact " \
           f"with {','.join(contact['numbers'])} numbers, " \
           f"{contact['birthday']} birthday, " \
           f"{','.join(contact['address'])} address, " \
           f"{contact['email']} email"


def find_contact(find_string: str, contacts_book: bot_classes.AddressBook) -> str:
    findings = contacts_book.find_record(find_string)
    return f"By the '{find_string}' request bot founded contacts :\n" \
           f"\n\tIn name :" \
           f"\n\n{''.join(findings['by_name']) if len(findings['by_name']) > 0 else 'Nothing found'}\n" \
           f"\n\tIn phone number/numbers :" \
           f"\n\n{''.join(findings['by_phone']) if len(findings['by_phone']) > 0 else 'Nothing found'}\n" \
           f"\n\tIn email :" \
           f"\n\n{''.join(findings['by_email']) if len(findings['by_email']) > 0 else 'Nothing found'}\n" \
           f"\n\tIn address/addresses :" \
           f"\n\n{''.join(findings['by_address']) if len(findings['by_address']) > 0 else 'Nothing found'}\n"


def dir_sort(path_to_dir: str) -> str:
    return dir_sorter.sort_dir(path_to_dir)


def show_all(contacts_book: bot_classes.AddressBook) -> str:
    return contacts_book.see_all_contacts()


def delete_contact(name: str, contacts_book: bot_classes.AddressBook) -> str:
    contacts_book.delete_record(name)
    return f"Successfully deleted {name} contact"


def goodbye() -> str:
    return 'Good bye!'

def days_from_now(self, days) -> int:
    days = input('how many days from now would you like to lookup birthdays for?')
    if days < 0:
        raise Exception('Days should be more than 0. Try again')
    self.days_from_now = days


COMMANDS = {
    'hello': [greetings, 'none_argument_commands'],
    'help': [greetings, 'none_argument_commands'],
    'add_contact': [add_contact, 'contact_commands'],
    'find_contact': [find_contact, 'one_argument_book_commands'],
    'delete_contact': [delete_contact, 'one_argument_book_commands'],
    'sort_dir': [dir_sort, 'sort_commands'],
    'show_all': [show_all, 'only_book_commands'],
    'goodbye': [goodbye, 'none_argument_commands'],
    'exit': [goodbye, 'none_argument_commands'],
    'close': [goodbye, 'none_argument_commands'],
    'get_birthday_list': [birthday_list, 'birthday_commands']
}

COMMAND_ARGS = {
    'hello': None,
    'help': None,
    'add_contact': 'name, '
                   'phone number/numbers(optional), '
                   'birthday(optional), '
                   'address/addresses(optional), '
                   'email(optional) separating them by ,',
    'find_contact': 'find request',
    'sort_dir': 'path to directory you want to sort',
    'delete_contact': 'name of the contact you want to delete',
    'show_all': None,
    'goodbye': None,
    'exit': None,
    'close': None,
    'days_from_now': 'how many days from now would you like to lookup birthdays for?'
}
