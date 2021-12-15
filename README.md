# About

This Address Book package works as a terminal/command line chatbot to help you save your contacts in one place on your computer and sort files. 

## This chatbot has following list of commands:

* hello, help – see the list of commands and a short instruction on how to use commands

* add_contact - adds a new contact to the Address Book with name, phone, email, birthday, notes and tags

* find_contact - searches for the contact in the Address Book based on your search input

* delete_contact – finds and deletes the record from the Address Book based on your search input

* birthdays_from_now – provides the list of people who have birthdays in a week, month, year, or any other given number of days.

* sort_dir – sorts the files in your directory by the extensions (videos, music, docs, etc.)

* show_all – shows all the records and record fields stored in your Address Book

* goodbye, exit, close – exits the program

* see_notes – shows notes for a specific contact

* sort_dir – sorts your files in the directory by extensions

* show_all – shows all existing records

* add_note – adds note to a record you would like update

* delete_note – deletes notes for the record you specify

* add_tag – adds a tag to a specified record

* find_notes_with_tag – finds and filters notes with the specified tag

* change_note – change the note for a specific record

* search_notes – searches notes notes by name and notes

The bot will try to guess what command you were trying to use in case you misspelled it. The package can be run in from anywhere on the computer.

# Package contents

* src folder - contains __init___ and setup file
* bot_classes.py – contains description of all the Address Book bot classes and their methods
* dir_sorter.py – a separate module to sort files in the directory to different folders by extensions
* handlers.py – contains functions and methods that call for bot_classes.py Classes and methods, additional methods to manipulate Address Book contents.
* main_bot.py – main script

# System Requirements
## Check if Python is installed on your system.
### **For mac users** 
Python comes pre-installed on **Mac OS X** so it is easy to start using. However, to take advantage of the latest versions of Python, you will need to download and install newer versions alongside the system ones. In Terminal check you python version by running 
> `python3 –version`

  If you would like to update python version to the latest first, install Homebrew (The   missing package manager for macOS) if you haven’t.

Type this in your terminal to install Homebrew:

> `/usr/bin/ruby -e “$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)”`

Now you can update your Python to python by running this command:

> `brew install python3 && cp /usr/local/bin/python3 /usr/local/bin/python`

 Your python should be up to date now 

### **For Windows users**

Open **command line** using Start menu. Type:

> `py –version`

If python is not installed on your system, follow the instructions provided by the link to install it on your **Windows Machine**: [Windows Python installation](https://phoenixnap.com/kb/how-to-install-python-3-windows)  

# Installing the bot package
To install Python package from [GitHub](https://github.com/dJg-jpeg/Address-Book-with-BlackJack-and-B-tches/tree/main), you need to clone this repository. In your Terminal/Command Line type:

> `git clone https://github.com/jkbr/httpie.git`


Navigate to the package folder using ‘cd’ command in your command line or Terminal (or open a new Terminal from the Folder/Git Bash Here in the package folder for Windows).
Install the script by running the following code in the Terminal:

> `python setup.py install`
> `pip install -e .`

Now you can run the script from any directory by running

> `book_bot`

After you see the Welcome message from bot, type ‘hello’ or ‘help’ to see the list of commands available in the chatbot.
