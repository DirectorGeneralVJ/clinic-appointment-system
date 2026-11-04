from abc import ABC, abstractmethod

P = 26042005


class Person(ABC):
    __made = 0

    def __init__(self, name, id, **rest):
        super().__init__(**rest)
        if name is None or str(name).strip() == "":
            raise ValueError("name cannot be empty")
        if id <= 0:
            raise ValueError("id must be positive")
        self.__name = str(name).strip()
        self.__id = id
        Person.__made += 1

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    @staticmethod
    def made():
        return Person.__made

    @abstractmethod
    def role(self):
        pass


class Patient(Person):
    def __init__(self, name, id):
        super().__init__(name=name, id=id)
        self.__emergency = False

    def role(self):
        return "Patient"

    def flag_emergency(self):
        self.__emergency = True

    def is_emergency(self):
        return self.__emergency


class Staff(Person):
    @abstractmethod
    def fee(self):
        pass


class Doctor(Staff):
    def role(self):
        return "Doctor"

    def fee(self):
        return 40 + 5 * (P % 5)


class Nurse(Staff):
    def role(self):
        return "Nurse"

    def fee(self):
        return 10 + (P % 3)


class Pharmacist(Staff):
    def role(self):
        return "Pharmacist"

    def fee(self):
        return 5


class Lecturer(Person):
    def __init__(self, name, id, module, **rest):
        if module is None or str(module).strip() == "":
            raise ValueError("module cannot be empty")
        super().__init__(name=name, id=id, **rest)
        self.__module = str(module).strip()

    @property
    def module(self):
        return self.__module

    def role(self):
        return "Lecturer"


class MedicalLecturer(Doctor, Lecturer):
    def role(self):
        return "Doctor and Lecturer"
