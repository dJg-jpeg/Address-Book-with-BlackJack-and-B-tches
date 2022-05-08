from flask import Flask

bot = Flask(__name__)

from contact_book_bot.src import routes
