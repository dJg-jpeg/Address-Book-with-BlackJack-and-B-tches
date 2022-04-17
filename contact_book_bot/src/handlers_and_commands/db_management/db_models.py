from mongoengine import EmbeddedDocument, Document
from mongoengine.fields import StringField, DateField, EmbeddedDocumentField, ListField


class NoteTag(EmbeddedDocument):
    tag = StringField()


class ContactNote(EmbeddedDocument):
    note = StringField()
    tags = ListField(EmbeddedDocumentField(NoteTag))


class ContactAddress(EmbeddedDocument):
    address = StringField()


class ContactPhone(EmbeddedDocument):
    phone = StringField()


class ContactEmail(EmbeddedDocument):
    email = StringField()


class ContactBirthday(EmbeddedDocument):
    birthday = DateField()


class Contact(Document):
    name = StringField()
    phones = ListField(EmbeddedDocumentField(ContactPhone))
    birthday = EmbeddedDocumentField(ContactBirthday)
    addresses = ListField(EmbeddedDocumentField(ContactAddress))
    email = EmbeddedDocumentField(ContactEmail)
    notes = ListField(EmbeddedDocumentField(ContactNote))
    meta = {'allow_inheritance': True}
