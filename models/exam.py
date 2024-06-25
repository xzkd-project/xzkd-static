class Exam:
    startDate: int  # unix timestamp
    endDate: int  # unix timestamp
    name: str
    location: str
    examType: str  # 期中/期末
    startHHMM: int
    endHHMM: int
    examMode: str  # 开卷/闭卷
    additionalInfo: dict[str, str]

    def __init__(
        self,
        startDate: int,
        endDate: int,
        name: str,
        location: str,
        examType: str,
        startHHMM: int,
        endHHMM: int,
        examMode: str,
        additionalInfo: dict[str, str],
    ):
        self.startDate = startDate
        self.endDate = endDate
        self.name = name
        self.location = location
        self.examType = examType
        self.startHHMM = startHHMM
        self.endHHMM = endHHMM
        self.examMode = examMode
        self.additionalInfo = additionalInfo
