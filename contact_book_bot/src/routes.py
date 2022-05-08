from . import bot
from flask import render_template, redirect, url_for, request
from contact_book_bot.src.handlers_and_commands.bot_classes_and_exceptions.bot_classes import AddressBook
from contact_book_bot.src.handlers_and_commands.handlers import see_notes, \
    delete_contact, add_note, delete_note, add_tag, add_contact, edit_contact, add_info
from contact_book_bot.src.handlers_and_commands.bot_classes_and_exceptions.bot_exceptions import ExistContactError, \
    PhoneError, EmailError


address_book = AddressBook()


@bot.route('/', strict_slashes=False, methods=['GET', 'POST', 'HEAD'])
def index():
    if request.method == 'POST':
        find_request = request.form.get('find_request')
        unprepared_contacts = address_book.find_record(find_request).values()
        contacts = []
        for category in unprepared_contacts:
            for this_contact in category:
                contacts.append(this_contact)
    else:
        contacts = address_book.see_all_contacts()
    return render_template("index.html", contacts=contacts)


@bot.route('/see_notes/<contact_name>/')
def see_record_notes(contact_name):
    notes = see_notes(contact_name, address_book)
    return render_template("see_notes.html", notes=notes)


@bot.route('/delete_contact/<contact_name>', methods=['GET', 'DELETE'])
def delete_user_contact(contact_name):
    delete_contact(contact_name, address_book)
    return redirect(url_for('index'))


@bot.route('/see_notes/<contact_name>/delete_note/<note_value>', methods=['GET', 'DELETE'])
def delete_note_from_contact(contact_name, note_value):
    delete_note(contact_name, note_value, address_book)
    return redirect(url_for('see_record_notes', contact_name=contact_name))


@bot.route('/see_notes/<contact_name>/add_tag/<note_value>', methods=['GET', 'POST', 'HEAD'])
def add_tag_to_contact_note(contact_name, note_value):
    if request.method == 'POST':
        tags_to_add = request.form.get('tags_to_add')
        prepared_tags = [tag.strip() for tag in tags_to_add.split(',')]
        add_tag(contact_name, note_value, address_book, prepared_tags)
        return redirect(url_for('see_record_notes', contact_name=contact_name))
    return render_template('add_tag.html', contact_name=contact_name, note_value=note_value)


@bot.route('/see_notes/<contact_name>/edit_note/<note_value>', methods=['GET', 'POST', 'HEAD'])
def edit_contact_note(contact_name, note_value):
    contact, editing_note_session = address_book.get_record_by_name(contact_name)
    record = address_book.convert_to_record(contact)
    required_note = record.get_note(note_value, contact)
    if request.method == 'POST':
        new_value = request.form.get('new_note')
        record.modify_note(note_value, new_value, contact, editing_note_session)
        return redirect(url_for('see_record_notes', contact_name=contact_name))
    note_tags = [this_tag.tag for this_tag in required_note.tags]
    editing_note_session.close()
    return render_template('edit_note.html', contact_name=contact_name, note_value=note_value, note_tags=note_tags)


@bot.route('/see_notes/<contact_name>/edit_note/<note_value>/delete_tag/<tag_value>', methods=['GET', 'DELETE'])
def delete_tag_from_contact_note(contact_name, note_value, tag_value):
    contact, deleting_tag_session = address_book.get_record_by_name(contact_name)
    record = address_book.convert_to_record(contact)
    required_note = record.get_note(note_value, contact)
    for this_tag in required_note.tags:
        if this_tag.tag == tag_value:
            deleting_tag_session.delete(this_tag)
            deleting_tag_session.commit()
            deleting_tag_session.close()
            break
    return redirect(url_for('edit_contact_note', contact_name=contact_name, note_value=note_value))


@bot.route('/add_note/<contact_name>', methods=['GET', 'POST', 'HEAD'])
def add_note_to_contact(contact_name):
    if request.method == 'POST':
        note = request.form.get('note')
        tags = request.form.get('note')
        add_note(contact_name, note, address_book, [tag.strip() for tag in tags.split(',')])
        return redirect(url_for('index'))
    return render_template('create_note.html', contact_name=contact_name)


@bot.route('/add_contact', methods=['GET', 'POST', 'HEAD'])
def add_new_contact():
    if request.method == 'POST':
        new_contact = {
            'name': request.form.get('name'),
            'numbers': None,
            'birthday': None,
            'address': None,
            'email': None,
        }
        phones = request.form.get('phone_numbers')
        if len(phones) > 0:
            new_contact['numbers'] = [phone.strip() for phone in phones.split(',')]
        birthday = request.form.get('birthday')
        if len(birthday) > 0:
            birthday = birthday.split('-')
            birthday.reverse()
            new_contact['birthday'] = '.'.join(birthday)
        addresses = request.form.get('addresses')
        if len(addresses) > 0:
            new_contact['address'] = [addr.strip() for addr in addresses.split(',')]
        email = request.form.get('email')
        if len(email) > 0:
            new_contact['email'] = email
        try:
            add_contact(new_contact, address_book)
            return redirect(url_for('index'))
        except ExistContactError:
            return render_template(
                'contact_error.html',
                title="Помилка додання контакту",
                button_text=" Спробувати ще раз створити контакт",
                button_link="/add_contact",
                error_text="Контакт з цим іменем вже існує , будь ласка спробуйте ще раз",
            )
        except PhoneError:
            return render_template(
                'contact_error.html',
                title="Помилка додання контакту",
                button_text=" Спробувати ще раз створити контакт",
                button_link="/add_contact",
                error_text="Номер телефону має починатись з + і містити лише цифри , будь ласка спробуйте ще раз",
            )
        except EmailError:
            return render_template(
                'contact_error.html',
                title="Помилка додання контакту",
                button_text=" Спробувати ще раз створити контакт",
                button_link="/add_contact",
                error_text="Ви намагаєтесь ввести неправильну адресу електронної пошти , будь ласка спробуйте ще раз",
            )
    return render_template('create_contact.html')


@bot.route('/edit_contact/<contact_name>', methods=['GET', 'POST', 'HEAD'])
def change_contact_attributes(contact_name):
    contact, changing_contact_session = address_book.get_record_by_name(contact_name)
    record = address_book.convert_to_record(contact)
    changing_contact_session.close()
    if request.method == 'POST':
        user_input = request.form
        try:
            if 'birthday' in user_input.keys():
                new_birthday = '.'.join(reversed(user_input['birthday'].split('-')))
                edit_contact(contact_name, 'birthday', new_birthday, address_book)
            elif 'email' in user_input.keys():
                new_email = user_input['email']
                edit_contact(contact_name, 'email', new_email, address_book)
            elif 'new_number' in user_input.keys():
                new_number = user_input['new_number']
                add_info(contact_name, 'phone', address_book, [new_number])
            elif 'new_address' in user_input.keys():
                new_address = user_input['new_address']
                add_info(contact_name, 'address', address_book, [new_address])
            return redirect(url_for('change_contact_attributes', contact_name=contact_name))
        except EmailError:
            return render_template(
                'contact_error.html',
                title="Помилка редагування контакту",
                button_text="Спробувати ще раз відредагувати електронну пошту",
                button_link=url_for('change_contact_attributes', contact_name=contact_name),
                error_text="Ви намагаєтесь ввести неправильну адресу електронної пошти , будь ласка спробуйте ще раз",
            )
        except PhoneError:
            return render_template(
                'contact_error.html',
                title="Помилка редагування контакту",
                button_text="Спробувати ще раз додати номер",
                button_link=url_for('change_contact_attributes', contact_name=contact_name),
                error_text="Номер телефону має починатись з + і містити лише цифри , будь ласка спробуйте ще раз",
            )
    birthday = record.birthday.value if record.birthday else ''
    email = record.email.value if record.email else ''
    phones = [number.value for number in record.phone]
    addresses = [addr.value for addr in record.address]
    return render_template(
        'edit_contact.html',
        contact_name=contact_name,
        birthday_value=birthday,
        email_value=email,
        phone_numbers=phones,
        addresses=addresses,
    )


@bot.route('/edit_contact/<contact_name>/delete_number/<number_value>', methods=['GET', 'DELETE'])
def delete_phone_number(contact_name, number_value):
    contact, deleting_number_session = address_book.get_record_by_name(contact_name)
    for this_phone in contact.phones:
        if this_phone.phone == number_value:
            deleting_number_session.delete(this_phone)
            deleting_number_session.commit()
            deleting_number_session.close()
            break
    return redirect(url_for('change_contact_attributes', contact_name=contact_name))


@bot.route('/edit_contact/<contact_name>/delete_address/<address_value>', methods=['GET', 'DELETE'])
def delete_address(contact_name, address_value):
    contact, deleting_address_session = address_book.get_record_by_name(contact_name)
    for this_addr in contact.addresses:
        if this_addr.address == address_value:
            deleting_address_session.delete(this_addr)
            deleting_address_session.commit()
            deleting_address_session.close()
            break
    return redirect(url_for('change_contact_attributes', contact_name=contact_name))
