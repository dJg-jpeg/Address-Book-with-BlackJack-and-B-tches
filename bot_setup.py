from setuptools import setup, find_namespace_packages

setup(
    name='contact_book_bot',
    version='2.0',
    description='Address book bot with dir sorting functions',
    url='https://github.com/dJg-jpeg/address_book_with_blackjack_and_b_tches/tree/main',
    author='dJg.jpeg, oleksiievetsno, yarynakor',
    author_email='vvl5656@gmail.com, oleksiievets.n.o@gmail.com, Irenekor87@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    entry_points={
        'console_scripts': [
            'book_bot = contact_book_bot.src.main_bot:main'
        ]
    },
    install_requires=['frozendict'],
)
