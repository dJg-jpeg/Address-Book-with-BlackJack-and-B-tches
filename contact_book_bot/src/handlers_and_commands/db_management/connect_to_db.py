from mongoengine import connect
from configparser import ConfigParser
from pathlib import Path


config = ConfigParser()
config.read(Path(__file__).parent.absolute() / Path('config.ini'))

username = config.get('DB', 'user')
password = config.get('DB', 'password')
db_name = config.get('DB', 'db_name')
domain = config.get('DB', 'domain')

connect(host=f"""mongodb+srv://{username}:{password}@{domain}/{db_name}?retryWrites=true&w=majority""", ssl=True)
