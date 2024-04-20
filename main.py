from collections import UserDict
from datetime import datetime
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value.istitle():
            self.__value = value
        else:
            raise ValueError('Invalid name')


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            self.__value = value
        except ValueError:
            raise ValueError('Invalid date')


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if p.value != phone_number]

    def edit_phone(self, old_phone_number, new_phone_number):
        for phone in self.phones:
            if phone.value == old_phone_number:
                self.phones = [Phone(new_phone_number) if p.value == old_phone_number else p for p in self.phones]
                break
        else:
            raise ValueError('Phone number not found')

    def find_phone(self, phone_number):
        return next(p for p in self.phones if p.value == phone_number)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return (f"Contact name: {self.name.value}, "
                f"phones: {'; '.join(p.value for p in self.phones)}, "
                f"birthday: {self.birthday.value}")


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthday(self):
        congratulation_dates = []
        today_date = datetime.now()
        for user in self.data.values():
            user_date = datetime.strptime(user.birthday.value, "%d.%m.%Y").replace(year=today_date.year)
            if user_date.date() < today_date.date():
                user_date = user_date.replace(year=user_date.year + 1)
            if user_date.weekday() == 5:
                user_date = user_date.replace(day=user_date.day + 2)
            if user_date.weekday() == 6:
                user_date = user_date.replace(day=user_date.day + 1)
            delta_date = user_date.date() - today_date.date()
            if delta_date.days <= 7:
                congratulation_dates.append({user.name.value: user_date.strftime("%d.%m.%Y")})
        return sorted(congratulation_dates, key=lambda x: str(x.values()))


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as k:
            return k
        except ValueError as v:
            return v
        except TypeError as t:
            return t
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        raise KeyError('Please enter contact name and phone number')
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 3:
        raise KeyError('Please enter contact name, old phone number and new phone number')
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Name not found")
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def remove_contact(args, book: AddressBook):
    if len(args) != 1:
        raise KeyError('Please enter contact name')
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Name not found")
    book.delete(name)
    return "Contact removed."


@input_error
def show_phones(args, book: AddressBook):
    if len(args) != 1:
        raise KeyError('Please enter contact name')
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Name not found")
    return [p.value for p in record.phones]


@input_error
def show_all(book: AddressBook):
    return [f'name: {contact.name}, phones: {[p.value for p in contact.phones]}, birthday: {contact.birthday}' for
            contact in book.data.values()]


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise KeyError('Please enter contact name and birthday date')
    name, birthday, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if birthday:
        record.add_birthday(birthday)
    return message


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise KeyError('Please enter contact name')
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Name not found")
    return record.birthday.value


@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthday()


def parse_input(user_input):
    if user_input:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args
    return '_'


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        match command:
            case 'close' | 'exit':
                print("Good bye!")
                break
            case "hello":
                print("How can I help you?")
            case "add":
                print(add_contact(args, book))
            case "change":
                print(change_contact(args, book))
            case "phone":
                print(show_phones(args, book))
            case 'all':
                print(show_all(book))
            case "add-birthday":
                print(add_birthday(args, book))
            case "show-birthday":
                print(show_birthday(args, book))
            case "birthdays":
                print(birthdays(book))
            case "remove":
                print(remove_contact(args, book))
            case _:
                print("Invalid command.")
    save_data(book)


if __name__ == "__main__":
    main()
