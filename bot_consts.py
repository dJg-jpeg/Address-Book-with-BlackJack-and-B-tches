import handlers
from frozendict import frozendict

# args for commands , that user can see

HELLO = None

HELP = None

ADD_CONTACT = 'name, ' \
              'phone number/numbers(optional), ' \
              'birthday(optional), ' \
              'address/addresses(optional), ' \
              'email(optional) ' \
              'separating them by ,'

FIND_CONTACT = 'find request'

SORT_DIR = 'path to directory you want to sort'

DELETE_CONTACT = 'name of the contact you want to delete'

BIRTHDAYS_FROM_NOW = 'how many days from now would you like to lookup birthdays for?'

SHOW_ALL = None

GOODBYE = None

EXIT = None

CLOSE = None

ADD_NOTE = 'name of the contact, note, tags(optional) , separating them by ,'

DELETE_NOTE = 'name of the contact, note , separating them by ,'

SEE_NOTES = 'name of the contact'

ADD_TAG = 'name of the contact, note, tag to add, separating them by ,'

FIND_NOTES_WITH_TAG = 'name of the contact, tag, ' \
                      'type of the sort ' \
                      '("newest", "name", "length")(default: "oldest"), separating them by ,'

CHANGE_NOTE = 'name of the contact, note, new note, separating them by ,'

SEARCH_FOR_NOTES = 'name of the contact, searched symbols, separating them by ,'

EDIT_CONTACT = 'name of the contact, field to edit, old value (" " for name, email and birthday), '\
               'new value, separating them by,'

ADD_INFO = 'name of the contact, field to add (phone or address), new value, separating them by,'

# command functions with categories and arguments to input in command

COMMANDS = frozendict({
    'hello': (handlers.greetings, 'none_argument_commands', HELLO),
    'help': (handlers.greetings, 'none_argument_commands', HELP),
    'add_contact': (handlers.add_contact, 'contact_commands', ADD_CONTACT),
    'find_contact': (handlers.find_contact, 'one_argument_book_commands', FIND_CONTACT),
    'delete_contact': (handlers.delete_contact, 'one_argument_book_commands', DELETE_CONTACT),
    'birthdays_from_now': (handlers.get_birthdays_by_days, 'one_argument_book_commands', BIRTHDAYS_FROM_NOW),
    'see_notes': (handlers.see_notes, 'one_argument_book_commands', SEE_NOTES),
    'sort_dir': (handlers.dir_sort, 'sort_commands', SORT_DIR),
    'show_all': (handlers.show_all, 'only_book_commands', SHOW_ALL),
    'goodbye': (handlers.goodbye, 'none_argument_commands', GOODBYE),
    'exit': (handlers.goodbye, 'none_argument_commands', EXIT),
    'close': (handlers.goodbye, 'none_argument_commands', CLOSE),
    'add_note': (handlers.add_note, '3args_commands', ADD_NOTE),
    'delete_note': (handlers.delete_note, '2args_commands', DELETE_NOTE),
    'add_tag': (handlers.add_tag, '3args_commands', ADD_TAG),
    'find_notes_with_tag': (handlers.find_notes_with_tag, '3args_commands', FIND_NOTES_WITH_TAG),
    'change_note': (handlers.change_note, '3args_commands', CHANGE_NOTE),
    'search_for_notes': (handlers.search_for_notes, '2args_commands', SEARCH_FOR_NOTES),
    'edit_contact': [handlers.edit_contact, '4args_commands', EDIT_CONTACT],
    'add_info': [handlers.add_info, '3args_commands', ADD_INFO],
})
