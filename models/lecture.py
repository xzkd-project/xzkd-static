class Lecture:
    startDate: int  # unix timestamp
    endDate: int  # unix timestamp
    name: str
    location: str
    teacherName: str
    periods: float
    additionalInfo: dict[str, str]
    startIndex: int
    endIndex: int

    def __init__(self, startDate: int, endDate: int, name: str, location: str, teacherName: str, periods: float,
                 additionalInfo: dict[str, str], startIndex: int, endIndex: int):
        self.startDate = startDate
        self.endDate = endDate
        self.name = name
        self.location = location
        self.teacherName = teacherName
        self.periods = periods
        self.additionalInfo = additionalInfo
        self.startIndex = startIndex
        self.endIndex = endIndex
