import sys
from contextlib import contextmanager

from appointment import Appointment, ClinicError, Status


class AppointmentLog:
    def __init__(self, path):
        self.__path = path
        self.__file = None
        self.__used = False
        self.__lines = []

    def open(self):
        if self.__used:
            raise RuntimeError("log can only be opened once")
        self.__file = open(self.__path, "a")
        self.__used = True
        print("[log] opened")

    def write(self, line):
        if self.__file is None:
            raise RuntimeError("log is not open")
        self.__lines.append(line)
        print(line)
        try:
            self.__file.write(line + "\n")
        except OSError as e:
            print("log write failed:", e, file=sys.stderr)

    def close(self):
        if self.__file is None:
            return
        try:
            self.__file.close()
        except OSError as e:
            print("log close failed:", e, file=sys.stderr)
        self.__file = None
        print("[log] closed")

    def lines(self):
        return tuple(self.__lines)


# Invariants:
# every person id in the clinic is unique, staff and patients share one id space
# appointment ids are unique and never reused
# no staff member and no patient has two non-cancelled appointments at the same hour
# a CONFIRMED appointment is never bumped
# the log is opened once when the clinic starts and closed once when it ends
# the internal lists are never handed out, only tuple copies
class Clinic:
    def __init__(self, clock, log_path="appointments.log"):
        self.__clock = clock
        self.__log = AppointmentLog(log_path)
        self.__staff = []
        self.__patients = []
        self.__appointments = []
        self.__ids = set()
        self.__next = 1

    def __enter__(self):
        self.__log.open()
        return self

    def __exit__(self, kind, value, trace):
        self.__log.close()
        return False

    @contextmanager
    def __attempt(self, label):
        try:
            yield
        except ClinicError as e:
            self.__log.write("FAILED " + label + ": " + str(e))
            raise

    def __claim(self, person):
        if person.id in self.__ids:
            raise ClinicError(f"id {person.id} already in use")
        self.__ids.add(person.id)

    def __pick(self, items, id, what):
        for item in items:
            if item.id == id:
                return item
        raise ClinicError(f"no such {what} #{id}")

    def __taken(self, start, staff=None, patient=None):
        for a in self.__appointments:
            if not a.is_active() or a.start != start:
                continue
            if a.staff is staff or a.patient is patient:
                return a
        return None

    def add_staff(self, staff):
        with self.__attempt(f"add staff #{staff.id}"):
            self.__claim(staff)
            self.__staff.append(staff)
            self.__log.write(f"add staff #{staff.id} {staff.name} ({staff.role()})")

    def add_patient(self, patient):
        with self.__attempt(f"add patient #{patient.id}"):
            self.__claim(patient)
            self.__patients.append(patient)
            self.__log.write(f"add patient #{patient.id} {patient.name}")

    def flag_emergency(self, patient_id):
        with self.__attempt(f"flag emergency #{patient_id}"):
            self.__pick(self.__patients, patient_id, "patient").flag_emergency()
            self.__log.write(f"flag emergency #{patient_id} ok")

    def book(self, staff_id, patient_id, start):
        with self.__attempt(f"book staff #{staff_id} patient #{patient_id} hour {start}"):
            staff = self.__pick(self.__staff, staff_id, "staff")
            patient = self.__pick(self.__patients, patient_id, "patient")
            if start < 0 or start > 167:
                raise ClinicError("hour must be from 0 to 167")
            if start < self.__clock.now():
                raise ClinicError("hour already passed")
            if self.__taken(start, patient=patient) is not None:
                raise ClinicError("patient already booked at that hour")
            other = self.__taken(start, staff=staff)
            if other is not None:
                if not patient.is_emergency():
                    raise ClinicError("staff already booked at that hour")
                if other.status is not Status.PENDING:
                    raise ClinicError("cannot bump a confirmed appointment")
                other.cancel("bumped")
                self.__log.write(f"cancel #{other.id} ok: bumped")
            appt = Appointment(self.__next, staff, patient, start, self.__clock)
            self.__next += 1
            self.__appointments.append(appt)
            self.__log.write(f"book #{appt.id} ok: {staff.name} / {patient.name} hour {start}")
            return appt.id

    def confirm(self, appt_id):
        with self.__attempt(f"confirm #{appt_id}"):
            self.__pick(self.__appointments, appt_id, "appointment").confirm()
            self.__log.write(f"confirm #{appt_id} ok")

    def cancel(self, appt_id, reason="cancelled by request"):
        with self.__attempt(f"cancel #{appt_id}"):
            self.__pick(self.__appointments, appt_id, "appointment").cancel(reason)
            self.__log.write(f"cancel #{appt_id} ok: {reason}")

    def staff(self):
        return tuple(self.__staff)

    def patients(self):
        return tuple(self.__patients)

    def summary(self):
        return tuple(str(a) for a in self.__appointments)
