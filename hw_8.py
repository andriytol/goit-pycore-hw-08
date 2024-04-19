from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


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
    
    def __str__(self):
        return f'+38{self.value}'
    

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") 

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    @staticmethod
    def find_next_weekday(d, weekday: int):  # Функція для знаходження наступного заданого дня тижня після заданої дати
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0: 
            days_ahead = days_ahead + 7 
        return d + timedelta(days=days_ahead)
    
    @staticmethod
    def parse_birthdays(users):
        prepared_users = []  # Список підготовлених користувачів
        for user in users:  # Ітерація по кожному користувачеві зі списку
            try:
                birthday = datetime.strptime(user['birthday'], '%Y.%m.%d').date()  # Парсимо дату народження
                prepared_users.append({"name": user['name'], 'birthday': birthday})  # Додаємо користувача з підготовленою датою народження
            except ValueError:
                print(f'Некоректна дата народження для користувача {user["name"]}')  # Виводимо повідомлення про помилку
        return prepared_users
    
    @staticmethod
    def get_upcoming_birthday(users):
        days = 7  # Кількість днів для перевірки на наближені дні народження
        today = datetime.today().date()  # Поточна дата
        prepared_users = AddressBook.parse_birthdays(users)
        upcoming_birthdays = []

        for user in prepared_users:  # Ітерація по підготовленим користувачам
            birthday_this_year = user["birthday"].replace(year=today.year)  # Заміна року на поточний для дня народження цього року

            if birthday_this_year < today:  # Якщо дата народження вже пройшла цього року
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)  # Переносимо наступний рік

            if 0 <= (birthday_this_year - today).days <= days:  # Якщо день народження в межах вказаного періоду
                if birthday_this_year.weekday() >= 5:  # Якщо день народження випадає на суботу або неділю
                    birthday_this_year = AddressBook.find_next_weekday(birthday_this_year, 0)  # Знаходимо наступний понеділок

                congratulation_date_str = birthday_this_year.strftime('%Y.%m.%d')  # Форматуємо дату у рядок
                upcoming_birthdays.append({  # Додаємо дані про майбутній день народження
                    "name": user["name"],
                    "congratulation_date": congratulation_date_str
            })
    
        return upcoming_birthdays

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        # Phone('0951111111') == '0951111111'
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return f"{self.name}'s birthday is on {self.birthday}"
        else:
            return f"{self.name} does not have a birthday set."
        
    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"

    
def input_error(func):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if result is None: 
                return "Contact not found."
            return result
        except KeyError:
            return "Contact not found."
        except ValueError:
            return "Give me name and phone please"
        except IndexError:
            return "Enter the argument for the command."
    return inner
    

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args
    
@input_error
def add_contact(args, address_book: AddressBook):
    name, phone, *_ = args
    record = address_book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        address_book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message
    
@input_error
def change_contact(args, address_book: AddressBook):
    name, phone = args
    record = address_book.find(name)
    if record:
        record.remove_phone(phone)
        record.add_phone(phone)
        return "Contact updated successfully"
    else:
        raise ValueError("Contact does not exist.")
    
@input_error
def show_contact(args, address_book: AddressBook):
    name = args[0]
    record = address_book.find(name)
    if record:
        return record
    else:
        raise KeyError("Contact not found.")

@input_error    
def all_contacts(address_book: AddressBook):
    for record in address_book.values():
        print(record)
    return record

@input_error
def add_birthday(args, address_book):
    name = args[0]
    birthday = args[1]
    record = address_book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday was added."
    else:
        raise KeyError
    
def save_data(adress_book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(adress_book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    
@input_error
def show_birthday(args, adress_book):
    name = args[0]
    record = adress_book.find(name)
    return str(record.birthday)



def birthdays(args, address_book):
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    birthdays_next_week = []
    for record in address_book.values():
        if record.birthday and today <= record.birthday.date <= next_week:
            birthdays_next_week.append((record.name, record.birthday.date))
    if birthdays_next_week:
        return "\n".join([f"{name}'s birthday on {date}" for name, date in birthdays_next_week])
    else:
        return "No birthdays in the next week."
    

def main():
    address_book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, address_book))
        elif command == "change":
            print(change_contact(args, address_book))
        elif command == "show":
            print(show_contact(args, address_book))   
        elif command == "all": 
            print(all_contacts(address_book))
        elif command == "add-birthday":
            print(add_birthday(args, address_book))
        elif command == "show-birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(birthdays(args, address_book))
        else:
            print("Invalid command.")
        save_data(address_book)
    
if __name__ == "__main__":
    main()
            

def __str__(self):
    return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"
    