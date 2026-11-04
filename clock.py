class Clock:
    def __init__(self, start=0):
        self.__hour = 0
        self.set(start)

    def now(self):
        return self.__hour

    def set(self, hour):
        if hour < 0 or hour > 168:
            raise ValueError("hour must be from 0 to 168")
        self.__hour = hour

    def advance(self, hours):
        self.set(self.__hour + hours)
