from appointment import ClinicError
from clinic import Clinic
from clock import Clock
from people import (Doctor, MedicalLecturer, Nurse, Patient, Person,
                    Pharmacist, Staff)


class Therapist(Staff):
    def role(self):
        return "Therapist"

    def fee(self):
        return 15


def tryit(fn, *args):
    try:
        fn(*args)
    except ClinicError:
        pass


clock = Clock(0)

try:
    with Clinic(clock) as clinic:
        clinic.add_staff(Doctor("Dr Chekeche", 1))
        clinic.add_staff(Nurse("Tatenda Sachikonye", 2))
        clinic.add_staff(Pharmacist("Ebba Mutasa", 3))

        before = Person.made()
        prof = MedicalLecturer("Prof Jera", 4, "Anatomy")
        print("Person constructor ran", Person.made() - before, "time")
        print(prof.role(), "|", prof.module, "|", prof.fee())
        clinic.add_staff(prof)
        clinic.add_staff(Therapist("Nyasha Chitima", 5))

        for s in clinic.staff():
            print(s.name, "|", s.role(), "|", s.fee())

        for name, id in (("", 9), ("Zed", 0)):
            try:
                Doctor(name, id)
            except ValueError as e:
                print("rejected:", e)
        try:
            Person("x", 1)
        except TypeError as e:
            print("abstract:", e)

        clinic.add_patient(Patient("Vitalis Jera", 11))
        clinic.add_patient(Patient("Farai Hungwe", 12))
        clinic.add_patient(Patient("Chipo Mutema", 13))
        tryit(clinic.add_patient, Patient("Copy", 11))

        clinic.book(1, 11, 10)
        clinic.book(2, 12, 10)
        clinic.confirm(1)
        tryit(clinic.book, 1, 13, 10)
        tryit(clinic.book, 2, 11, 10)

        clinic.flag_emergency(13)
        tryit(clinic.book, 1, 13, 10)
        clinic.book(2, 13, 10)
        clinic.confirm(3)

        clinic.book(1, 12, 20)
        clinic.cancel(4, "changed mind")
        tryit(clinic.cancel, 4)
        tryit(clinic.confirm, 4)

        for line in clinic.summary():
            print(line)

        clock.set(9)
        clinic.book(1, 12, 9)
        tryit(clinic.cancel, 5)
        clinic.cancel(3)
except ClinicError as e:
    print("stopped:", e)
