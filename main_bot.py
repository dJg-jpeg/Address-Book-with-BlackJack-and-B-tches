import bot_exceptions
from bot_classes import AddressBook
from re import search
from typing import List, Callable
from difflib import get_close_matches
from bot_consts import COMMANDS


def get_handler(
        contacts: AddressBook,
        handler: Callable,
        category: str,
        arguments: List[str] = None
) -> str:
    try:
        if not arguments:
            if category == 'only_book_commands':
                return handler(contacts)
            return handler()
        if category == 'one_argument_book_commands':
            return handler(arguments[0], contacts)
        elif category == 'sort_commands':
            return handler(arguments[0])
        elif category == 'contact_commands':
            return handler(parse_user_input(arguments), contacts)
        elif category == '2args_commands':
            return handler(arguments[0], arguments[1], contacts)
        elif category == '3args_commands':
            return handler(arguments[0], arguments[1], arguments[2:], contacts)
        elif category == '4args_commands':
            if len(arguments) == 4:
                return handler(arguments[0], arguments[1], arguments[3], contacts, arguments[2])
            else:
                return handler(arguments[0], arguments[1], arguments[2], contacts)

    except bot_exceptions.ExistContactError:
        return "This contact already exists, " \
               "if you want to change number please use command change"
    except bot_exceptions.UnknownContactError:
        return "No contact with such name in contact book, " \
               "please try input different name"
    except bot_exceptions.UnknownNoteError:
        return "No such note for this contact, " \
               "please try input different note"
    except bot_exceptions.UnknownPhoneError:
        return "No such phone for this contact, " \
               "please try input different phone"
    except bot_exceptions.UnknownAddressError:
        return "No such address for this contact, " \
               "please try input different phone"
    except bot_exceptions.PhoneError:
        return "Phone number must starts from + " \
               "and phone must contain only digits" \
               ", please try again"
    except bot_exceptions.BirthdayError:
        return "Data must match pattern 'day.month.year', " \
               "please try again"
    except bot_exceptions.EmailError:
        return "You are trying to input invalid email address, " \
               "please try again"
    except bot_exceptions.InvalidDirectoryPathError:
        return 'It is not a directory , ' \
               'please insert a valid directory path'
    except bot_exceptions.ZeroDaysError:
        return 'Please input more than zero days, try again'
    except bot_exceptions.LiteralsInDaysError:
        return 'Please input only numbers'
    except bot_exceptions.UnknownFieldError:
        return 'No such field for the contact ' \
               '(if add_info , accepted are phone or address, ' \
               'if edit_contact, accepted are phone, address, birthday and email)' \
               ', please try again'
    except IndexError:
        return "Seems you haven't inputted obligatory arguments for the command, " \
               "or you have inputted too much arguments. Please try again"


def parse_user_input(raw_contact: list) -> dict:
    parsed_contact = {
        'name': raw_contact[0],
        'numbers': [],
        'birthday': None,
        'address': [],
        'email': None,
    }
    for attribute in raw_contact[1:]:
        if attribute.startswith('+') or attribute.isalnum():
            parsed_contact['numbers'].append(attribute)
        elif '@' in attribute:
            parsed_contact['email'] = attribute
        elif search(r'\d{1,4}[.\s\\/]\d{1,4}[.\s\\/]\d{1,4}', attribute):
            parsed_contact['birthday'] = attribute
        else:
            parsed_contact['address'].append(attribute)
    return parsed_contact


def get_most_close_commands(command: str) -> list[str]:
    return get_close_matches(command, list(COMMANDS.keys()))


def main() -> None:
    bot_answer = None
    address_book = AddressBook()
    address_book.load()
    print('Welcome! '
          'Please separate arguments using the , character.\n'
          'For example : \n add_contact \n name , phones, birthday\n\n'
          'For more details input "help" or "hello"')
    while bot_answer != 'Good bye!':
        raw_command = input("Input command :")
        lowered_command = raw_command.lower()
        prepared_command = lowered_command.strip()
        try:
            handler, category, args_for_command = COMMANDS[prepared_command]
        except KeyError:
            close_commands = get_most_close_commands(prepared_command)
            if len(close_commands) != 0:
                print(f"Seems like you'd missprinted this command. "
                      f"The most close commands to your input are: \n {', '.join(close_commands)}")
            else:
                print("I don't know such command, please try again(")
            continue
        if args_for_command:
            raw_user_args = input(f"Input {args_for_command} :")
            split_user_args = raw_user_args.split(',')
            user_args = [arg.strip() for arg in split_user_args]
            bot_answer = get_handler(
                address_book, handler, category, user_args)
        else:
            bot_answer = get_handler(address_book, handler, category)
        if bot_answer == 'Good bye!':
            address_book.save()
        print(bot_answer)


if __name__ == '__main__':
    main()
