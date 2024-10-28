import re
import sqlite3
from sqlite3 import Connection
from pathlib import Path
from datetime import datetime, date


class AddressBook:
    def __init__(self) -> None:
        path_db: Path = Path(__file__).resolve().parent.joinpath('contacts.db')
        self.conn: Connection = sqlite3.connect(database=path_db)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.conn.commit()

    def __is_contact_present(self, name: str) -> bool:
        return (
            self.conn.execute(
                'SELECT * FROM contacts WHERE contact_name = (?)', (name,)
            ).fetchone()
            is not None
        )

    def __is_phone_present(self, name: str, phone: str) -> bool:
        return (
            self.conn.execute(
                'SELECT * FROM phones WHERE contact_name = (?) AND phone = (?)',
                (name, phone),
            ).fetchone()
            is not None
        )

    def __is_birthday_present(self, name: str) -> bool:
        return (
            self.conn.execute(
                'SELECT * FROM birthdays WHERE contact_name = (?)', (name,)
            ).fetchone()
            is not None
        )

    def __insert_or_update_contact(self, name: str) -> None:
        self.conn.execute(
            '''
            INSERT INTO contacts(contact_name) VALUES (?) 
            ON CONFLICT(contact_name) 
            DO UPDATE SET contact_name=excluded.contact_name
            ''',
            (name,),
        )
        self.conn.commit()

    def __insert_or_update_birthday(self, name: str, birthday: str) -> None:
        self.conn.execute(
            '''
            INSERT INTO birthdays(contact_name, birthday) VALUES (?, ?)
            ON CONFLICT(contact_name)
            DO UPDATE SET birthday=excluded.birthday
            ''',
            (name, birthday),
        )
        self.conn.commit()

    def __insert_or_replace_phone(self, name: str, phone: str) -> None:
        self.conn.execute(
            'INSERT OR REPLACE INTO phones(contact_name, phone) VALUES (?, ?)',
            (name, phone),
        )
        self.conn.commit()

    def __update_phone(self, name: str, phone: str, new_phone: str) -> None:
        self.conn.execute(
            'UPDATE phones SET phone = (?) WHERE contact_name = (?) AND phone = (?)',
            (new_phone, name, phone),
        )
        self.conn.commit()

    def __select_birthday(self, name: str) -> tuple[str] | None:
        return self.conn.execute(
            'SELECT birthday FROM birthdays WHERE contact_name = (?)', (name,)
        ).fetchone()

    def __select_birthdays_next_week(self) -> list[tuple[str, str]]:
        return self.conn.execute(
            '''
            SELECT * FROM (
                SELECT contact_name, DATE(
                    STRFTIME('%Y', DATE('NOW')) || STRFTIME('-%m-%d', birthday)
                ) AS birthday_this_year FROM birthdays
            ) 
            WHERE 
                birthday_this_year >= DATE('NOW')
                and birthday_this_year <= DATE('NOW', '+7 days')
            '''
        ).fetchall()

    def __select_contact_phones(self, name: str) -> list[tuple[str, str]]:
        return self.conn.execute(
            'SELECT * FROM phones WHERE contact_name = (?)', (name,)
        ).fetchall()

    def __select_all_phones(self) -> list[tuple[str, str]]:
        return self.conn.execute('SELECT * FROM phones').fetchall()

    def __validate_input_name(self, name: str) -> str:
        if not re.fullmatch(r'[A-z]{2,32}', name):
            raise ValueError(f'Name can consist of letters A-z only.')
        return name

    def __validate_input_phone(self, phone: str) -> str:
        if not re.fullmatch(r'[0-9]{10}', phone):
            raise ValueError(
                f'Phone must consist of 10 digits, example 0971122333'
            )
        return phone

    def __validate_input_birthday(self, birthday: str) -> str:
        try:
            birthday_date: date = datetime.strptime(
                birthday, r'%d.%m.%Y'
            ).date()
            birthday: str = birthday_date.strftime(r'%Y-%m-%d')
        except:
            raise ValueError(
                f'Input date must be in format dd.mm.yyyy, '
                'example: 31.12.2024'
            )
        else:
            return birthday

    def __validate_output_birthday(self, birthday: str) -> str:
        try:
            birthday_date: date = datetime.strptime(
                birthday, r'%Y-%m-%d'
            ).date()
            birthday: str = birthday_date.strftime(r'%d.%m.%Y')
        except:
            raise ValueError(
                f'Database date must be in format yyyy-mm-dd, '
                'example: 2024-12-31'
            )
        else:
            return birthday

    def add_birthday(self, name: str, birthday: str) -> str:
        name: str = self.__validate_input_name(name=name)
        birthday: str = self.__validate_input_birthday(birthday=birthday)

        self.__insert_or_update_contact(name=name)
        self.__insert_or_update_birthday(name=name, birthday=birthday)

        return 'Birthday: added.'

    def add_phone(self, name: str, phone: str) -> str:
        name: str = self.__validate_input_name(name=name)
        phone: str = self.__validate_input_phone(phone=phone)

        self.__insert_or_update_contact(name=name)
        self.__insert_or_replace_phone(name=name, phone=phone)

        return 'Phone: added.'

    def edit_phone(self, name: str, phone: str, new_phone: str) -> str:
        name: str = self.__validate_input_name(name=name)
        phone: str = self.__validate_input_phone(phone=phone)
        new_phone: str = self.__validate_input_phone(phone=new_phone)

        if not self.__is_contact_present(name=name):
            return (
                f'Contact {name} is absent in address book '
                'and can not be edited.'
            )

        if not self.__is_phone_present(name=name, phone=phone):
            return (
                f'Phone {phone} is absent in contact {name} '
                'and can not be edited.'
            )

        self.__update_phone(name=name, phone=phone, new_phone=new_phone)

        return 'Phone: updated.'

    def show_birthday(self, name: str) -> str:
        name: str = self.__validate_input_name(name=name)

        if not self.__is_contact_present(name=name):
            return (
                f'Contact {name} is absent in address book, '
                'birthday can not be displayed.'
            )

        if not self.__is_birthday_present(name=name):
            return f'Contact: {name}, Birthday: not entered yet.'

        birthday_selected: tuple[str] = self.__select_birthday(name=name)
        birthday: str = self.__validate_output_birthday(
            birthday=birthday_selected[0]
        )

        return f'Contact: {name}, Birthday: {birthday}'

    def show_birthdays_next_week(self) -> str:
        congrats_next_week: list[tuple[str, str]] = (
            self.__select_birthdays_next_week()
        )

        if len(congrats_next_week) == 0:
            return 'There are no birthdays next week.'

        report: str = 'Birthdays next week: \n\n'
        for cnw in congrats_next_week:
            contact_name, birthday_this_year = cnw

            birthday_this_year: str = self.__validate_output_birthday(
                birthday=birthday_this_year
            )

            report += (
                f'Contact: {contact_name}, '
                f'Congratulation: {birthday_this_year} \n\n'
            )

        return report

    def show_phones(self, name: str) -> str:
        name: str = self.__validate_input_name(name=name)

        if not self.__is_contact_present(name=name):
            return (
                f'Contact {name} is absent in address book, '
                'phones can not be displayed.'
            )

        contact_phones: list[tuple[str, str]] = self.__select_contact_phones(
            name=name
        )

        if len(contact_phones) == 0:
            return f'Contact: {name}, Phones: not entered yet.'

        report: str = 'Contact phones: \n\n'
        for cp in contact_phones:
            contact_name, phone = cp
            report += f'Contact: {contact_name}, Phone: {phone} \n\n'

        return report

    def show_phones_all_contacts(self) -> str:
        all_phones: list[tuple[str, str]] = self.__select_all_phones()

        if len(all_phones) == 0:
            return 'Phones: not entered yet.'

        report: str = 'All phones in address book: \n\n'
        for ap in all_phones:
            contact_name, phone = ap
            report += f'Contact: {contact_name}, Phone: {phone} \n\n'

        return report
