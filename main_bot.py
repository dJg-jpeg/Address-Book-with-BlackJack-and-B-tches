from functools import wraps
import handlers
import bot_classes
import re
from typing import List
from collections import deque


def input_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            answer = func(*args, **kwargs)
        except bot_classes.UnknownCommandError:
            return "I don't know this command, please try input again"
        except bot_classes.ExistContactError:
            return "This contact already exists, " \
                   "if you want to change number please use command change"
        except bot_classes.PhoneError:
            return "Phone number must starts from + and phone must contain only digits" \
                   ", please try again"
        except bot_classes.BirthdayError:
            return "Data must match pattern 'day.month.year', " \
                   "please try again"
        except bot_classes.EmailError:
            return "You are trying to input invalid email address, " \
                   "please try again"
        return answer

    return wrapper


@input_error
def get_handler(command_and_user_args: List[str], contacts: bot_classes.AddressBook) -> str:
    if command_and_user_args[0] not in handlers.COMMANDS.keys():
        raise bot_classes.UnknownCommandError
    necessary_handler = handlers.COMMANDS[command_and_user_args[0]]
    if command_and_user_args[0] == 'find':
        return necessary_handler(command_and_user_args[1], contacts)
    elif len(command_and_user_args) > 1:
        contact_args = parse_user_input(command_and_user_args[1:])
        return necessary_handler(contact_args, contacts)
    return necessary_handler()


def parse_user_input(raw_contact: list) -> dict:
    parsed_contact = {'name': raw_contact[0],
                      'numbers': [],
                      'birthday': None,
                      'address': [],
                      'email': None,
                      }
    for attribute in raw_contact[1:]:
        if attribute.startswith('+'):
            parsed_contact['numbers'].append(attribute)
        elif '@' in attribute:
            parsed_contact['email'] = attribute
        elif re.search(r'\d{1,4}[.\s\\/]\d{1,4}[.\s\\/]\d{1,4}', attribute) is not None:
            parsed_contact['birthday'] = attribute
        else:
            parsed_contact['address'].append(attribute)
    return parsed_contact


def main() -> None:
    bot_answer = ''
    address_book = bot_classes.AddressBook()
    print('Welcome! '
          'Please separate arguments using the , character.\n'
          'For example : \n add name , phones, birthday\n')
    while bot_answer != 'Good bye!':
        console_args = deque(input('\nInput command and arguments, separating them by , :\n').split(','))
        if len(console_args) > 1:
            command_and_name = console_args[0].split(' ')
            command_and_name[0] = command_and_name[0].lower()
            console_args.appendleft(command_and_name[0])
            console_args[1] = command_and_name[1]
            console_args = [arg.strip() for arg in console_args]
        else:
            if ' ' in console_args[0]:
                console_args = console_args[0].split(' ')
            console_args[0] = console_args[0].lower()
        bot_answer = get_handler(console_args, address_book)
        print(bot_answer)


if __name__ == '__main__':
    main()
