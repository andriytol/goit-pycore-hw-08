from collections import UserDict
import re
from datetime import datetime as dtdt
import datetime as dt
import pickle


class Field:
    def __init__(self, value) -> None:
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
class Name(Field):
    def __init__(self, value):
        if len(value) != 0:
            super().__init__(value)
        else: pass 
        
class Phone(Field):
    def __init__(self, number):
        if self.validate_number(number):
            super().__init__(number)
        else:
            raise ValueError
    
    def validate_number(self, number):
        if (len(number)==10) and \
            (re.match(r"^\d+$",number)):
            return True
        else:
            raise ValueError

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Phone):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return super().__str__()
        
class Birthday(Field):
    def __init__(self, value: str) -> None:
        try:
            b_date = dtdt.strptime(value,"%d.%m.%Y").date()
            super().__init__(b_date)
        except:
            raise ValueError ("please input date in correct format \
                              DD.MM.YYYY")

class Record:
    def __init__(self, name) -> None:
        self.name = Name(name)
        self.birthday = None
        self.phones = []

    def add_phone(self, phone_number):
        number = Phone(phone_number)
        if number:
            self.phones.append(number)

    def add_birthday(self,b_day):
        b_day = Birthday(b_day)
        if b_day:
            self.birthday = b_day

    def remove_phone(self, phone_number):
        phone_obj = Phone(phone_number)
        for obj in self.phones:
            if obj.value == phone_obj.value:
                self.phones.remove(obj)

    def edit_phone(self, old_number, new_number):
        self.find_phone(old_number)
        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, phone_number):
        ph = Phone(phone_number)
        if ph in self.phones:
            return ph
        else:
            raise ValueError
   
    def __str__(self) -> str:
        all_phones_str = []
        for tel in self.phones:
            all_phones_str.append(str(tel))
        return f" Phones:{str(all_phones_str)} Birthday: {self.birthday}"
    
class AddressBook(UserDict):

    def add_record(self, record_item: "Record"):
        self.data[record_item.name.value] = record_item
    
    def find(self, key):
        return self[key]

    def delete(self, key):
        del self[key]

    def get_birthdays (self, for_the_period:7):
        congrat_list = [] 
        bd_dict = {k: v.birthday.value for k, v in self.items() \
      if v.birthday is not None }
        curr_date = dtdt.today().date()
        end_date = curr_date + dt.timedelta(for_the_period)
        for k, v in bd_dict.items():
            bd_date = v
            bd_date_this_year = dt.date(curr_date.year, bd_date.month, bd_date.day)
            if bd_date_this_year.weekday() == 6:
                bd_date_this_year = bd_date_this_year + dt.timedelta(1)
            if bd_date_this_year.weekday() == 5:
                bd_date_this_year = bd_date_this_year + dt.timedelta(2)
            
            if (bd_date_this_year <= end_date) and (bd_date_this_year >= curr_date):
                dct = {"name": k, "congratulation_date": bd_date_this_year.strftime("%Y.%m.%d")}
                congrat_list.append (dct)
        return congrat_list
    
    def __str__(self) -> str:
        dict = {}
        for k, v in self.items():
            dict[k] = str(v)
            result_str = "\n".join([f"{k}:{v}" for k,v in dict.items()])
        return str(result_str)
    
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)
    
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "+rb") as f:
            restored_bk = pickle.load(f)
            cnt = len(restored_bk)
            print(f"{cnt} contacts in AddressBook loaded")
            return restored_bk
    except:
        return AddressBook()
    
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Command not Found."
        except KeyError:
            return "Name not Found."
        except NameError:
            return "Name not Found."
        except Exception as e:
            return f"Error: {e}"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args  

@input_error
def add_contact(*args):
    if args[0] in book:
        record = book.find(args[0])
        record.add_phone(args[1])
    else:
        record = Record(args[0])
        record.add_phone(args[1])
        book.add_record(record)
    return record

@input_error
def change_contact(command, *args):
    record = book.find(args[0])
    record.edit_phone(args[1], args[2])
    return record

@input_error
def show_phone(*args):
    record = book.find(args[0])
    return record

@input_error
def show_all():
    return book

@input_error
def show_birthday(*args):
    record = book.find(args[0])
    return record.birthday

@input_error
def add_birthday(*args):
    record = book.find(args[0])
    record.add_birthday(args[1])
    return record

book = load_data()
    
def main():
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = parse_input(user_input) 
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command in ["hello"]:
            print("Hello how can I help you?")
        elif command in ["add"]:
            add = add_contact(command, *args)
            print(add)

        elif command in ["change"]:
            ch = change_contact(command, *args)
            print(ch)

        elif command in ["phone"]:
            p = show_phone(*args)
            print(p)
        
        elif command in ["all"]:
            all = show_all()
            print (all)
            
        elif command == "add-birthday":
            print(add_birthday(*args))
                 
        elif command == "show-birthday":
            b_day = show_birthday(*args)
            print(b_day)
        
        elif command == "birthdays":
            congrat_list = book.get_birthdays(7)
            print(congrat_list)
        
        else:
            print("Invalid comand")              
                
        
if __name__ == "__main__":
     main()