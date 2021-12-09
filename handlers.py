import bot_classes
from typing import Optional


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
           f"{','.join(contact['addresses'])} addresses, " \
           f"{contact['email']} email"


def goodbye() -> str:
    return 'Good bye!'


COMMANDS = {
    'hello': greetings,
    'help': greetings,
    'add': add_contact,
    'goodbye': goodbye,
    'exit': goodbye,
    'close': goodbye,
}
