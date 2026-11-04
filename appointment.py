from enum import Enum


class ClinicError(Exception):
    pass


class Status(Enum):
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3


_MOVES = {
    Status.PENDING: (Status.CONFIRMED, Status.CANCELLED),
    Status.CONFIRMED: (Status.CANCELLED,),
    Status.CANCELLED: (),
}


# Invariants:
# staff, patient, start and id are set once and never change
# start is a whole hour from 0 to 167
# status only moves PENDING -> CONFIRMED, PENDING -> CANCELLED, CONFIRMED -> CANCELLED
# a CANCELLED appointment never changes again and always has a reason
# a CONFIRMED appointment cannot be cancelled with less than 2 hours to start
# no appointment can be confirmed or cancelled once its start hour is reached
class Appointment:
    NOTICE = 2

    def __init__(self, id, staff, patient, start, clock):
        if id <= 0:
            raise ValueError("id must be positive")
        if start < 0 or start > 167:
            raise ValueError("start must be a whole hour from 0 to 167")
        if staff is None or patient is None or clock is None:
            raise ValueError("staff, patient and clock are required")
        self.__id = id
        self.__staff = staff
        self.__patient = patient
        self.__start = start
        self.__clock = clock
        self.__status = Status.PENDING
        self.__reason = None

    @property
    def id(self):
        return self.__id

    @property
    def staff(self):
        return self.__staff

    @property
    def patient(self):
        return self.__patient

    @property
    def start(self):
        return self.__start

    @property
    def status(self):
        return self.__status

    @property
    def reason(self):
        return self.__reason

    def is_active(self):
        return self.__status is not Status.CANCELLED

    def __allow(self, new):
        if new not in _MOVES[self.__status]:
            raise ClinicError("cannot go from " + self.__status.name + " to " + new.name)

    def confirm(self):
        self.__allow(Status.CONFIRMED)
        if self.__clock.now() >= self.__start:
            raise ClinicError("already started")
        self.__status = Status.CONFIRMED

    def cancel(self, reason):
        self.__allow(Status.CANCELLED)
        left = self.__start - self.__clock.now()
        if left <= 0:
            raise ClinicError("already started")
        if self.__status is Status.CONFIRMED and left < Appointment.NOTICE:
            raise ClinicError("too late")
        if reason is None or str(reason).strip() == "":
            raise ClinicError("reason is required")
        self.__status = Status.CANCELLED
        self.__reason = str(reason).strip()

    def __str__(self):
        text = f"#{self.__id} {self.__staff.name} / {self.__patient.name} hour {self.__start} {self.__status.name}"
        if self.__reason:
            text += f" ({self.__reason})"
        return text
