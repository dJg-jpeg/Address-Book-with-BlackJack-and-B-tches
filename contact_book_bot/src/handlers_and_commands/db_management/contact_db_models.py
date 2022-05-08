from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Date


contact_db_engine = create_engine('sqlite:///src/handlers_and_commands/db_management/contact_book.db')
Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False)
    birthday = Column(Date)
    email = Column(String(30))
    phones = relationship("ContactPhone", backref="contact", cascade="all, delete, delete-orphan")
    addresses = relationship("ContactAddress", backref="contact", cascade="all, delete, delete-orphan")
    notes = relationship("ContactNote", backref="contact", cascade="all, delete, delete-orphan")


class ContactPhone(Base):
    __tablename__ = "phones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String)
    contact_id = Column(Integer, ForeignKey(Contact.id, ondelete="CASCADE"))


class ContactAddress(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String)
    contact_id = Column(Integer, ForeignKey(Contact.id, ondelete="CASCADE"))


class ContactNote(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    note = Column(String)
    contact_id = Column(Integer, ForeignKey(Contact.id, ondelete="CASCADE"))
    tags = relationship("NoteTag", backref="note", cascade="all, delete, delete-orphan")


class NoteTag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String)
    note_id = Column(Integer, ForeignKey(ContactNote.id, ondelete="CASCADE"))
