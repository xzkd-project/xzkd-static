import os
from json import load, dumps
from typing import Optional
from pprint import pprint
import jsonpickle


class Campus:
    def __init__(self, id: int, name: str, latitude: float, longitude: float):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    id: int
    name: str
    latitude: float
    longitude: float


east = Campus(1, "东区", 117.268264, 31.83892)
west = Campus(2, "西区", 117.256645, 31.839258)
north = Campus(3, "北区", 117.268125, 31.841933)
south = Campus(4, "南区", 117.283853, 31.822112)
xianyanyuan = Campus(5, "先研院", 117.129257, 31.826345)
gaoxin = Campus(6, "高新", 117.129369, 31.820447)


# Route = list[Campus]
class Route:
    def __init__(self, id: int, campuses: list[Campus]):
        self.id = id
        self.campuses = campuses

    id: int
    campuses: list[Campus]


routeA = Route(1, [east, north, west])
routeB = Route(2, [west, north, east])
routeC = Route(3, [east, south])
routeD = Route(4, [south, east])
routeE = Route(5, [west, south])
routeF = Route(6, [south, west])
routeG = Route(7, [gaoxin, xianyanyuan, west, east])
routeH = Route(8, [east, west, xianyanyuan, gaoxin])


class RouteSchedule:
    def __init__(self, id: int, route: Route, time: list[list[str]]):
        self.id = id
        self.route = route
        self.time = time

    id: int
    route: Route
    time: list[list[Optional[str]]]


class RouteScheduleP:
    def __init__(self, id: int, route: Route, time: list[(list[str], bool)]):
        self.id = id
        self.route = route
        self.time = time

    id: int
    route: Route
    time: list[(list[Optional[str]], bool)]


# starts at 7:25, 9:20, 9:35, 11:35, 12:20, 13:30, 15:30, 15:50, 17:30, 17:50, 18:40, 20:10, 21:15, 22:10,
# keep None for north(second stop), west at start + 10 minutes
rsA = RouteScheduleP(1, routeA, [
    (["07:25", None, "07:35"], True),
    (["09:20", None, "09:30"], False),
    (["09:35", None, "09:45"], False),
    (["11:35", None, "11:45"], True),
    (["12:20", None, "12:30"], False),
    (["13:30", None, "13:40"], True),
    (["15:30", None, "15:40"], False),
    (["15:50", None, "16:00"], False),
    (["17:30", None, "17:40"], True),
    (["17:50", None, "18:00"], False),
    (["18:40", None, "18:50"], True),
    (["20:10", None, "20:20"], False),
    (["21:15", None, "21:25"], True),
    (["22:10", None, "22:20"], False),
])
# rsB is essentially the continuation of rsA, so when the bus arrives at the last stop, it will turn back again,
# so time starts at rsA's finsh time, None, then +10 minutes
rsB = RouteScheduleP(2, routeB, [
    (["07:35", None, "07:45"], True),
    (["09:30", None, "09:40"], False),
    (["09:45", None, "09:55"], False),
    (["11:45", None, "11:55"], True),
    (["12:30", None, "12:40"], False),
    (["13:40", None, "13:50"], True),
    (["15:40", None, "15:50"], False),
    (["16:00", None, "16:10"], False),
    (["17:40", None, "17:50"], True),
    (["18:00", None, "18:10"], False),
    (["18:50", None, "19:00"], True),
    (["20:20", None, "20:30"], False),
    (["21:25", None, "21:35"], True),
    (["22:20", None, "22:30"], False),
])
# rsC takes 15 minutes, start at these times:
# 07:35, 08:30, 11:35, 11:45, 12:05, 12:40, 14:30, 17:25, 17:45, 18:10, 19:00, 20:30, 21:35, 22:30
rsC = RouteScheduleP(3, routeC, [
    (["07:35", "07:50"], False),
    (["08:30", "08:45"], False),
    (["11:35", "11:50"], False),
    (["11:45", "12:00"], True),
    (["12:05", "12:20"], False),
    (["12:40", "12:55"], False),
    (["14:30", "14:45"], False),
    (["17:25", "17:40"], False),
    (["17:45", "18:00"], True),
    (["18:10", "18:25"], False),
    (["19:00", "19:15"], True),
    (["20:30", "20:45"], False),
    (["21:35", "21:50"], True),
    (["22:30", "22:45"], False),
])
# rsD takes 15 minutes, start at these times:
# 07:10, 07:30, 08:00, 09:00, 12:00, 13:20, 13:40, 14:00, 15:10, 18:20, 19:15, 20:45, 21:50, 22:45
rsD = RouteScheduleP(4, routeD, [
    (["07:10", "07:25"], False),
    (["07:30", "07:45"], True),
    (["08:00", "08:15"], False),
    (["09:00", "09:15"], False),
    (["12:00", "12:15"], False),
    (["13:20", "13:35"], False),
    (["13:40", "13:55"], True),
    (["14:00", "14:15"], False),
    (["15:10", "15:25"], False),
    (["18:20", "18:35"], False),
    (["19:15", "19:30"], True),
    (["20:45", "21:00"], False),
    (["21:50", "22:05"], True),
    (["22:45", "23:00"], False),
])
# rsE: 20min, start times:
# 07:35, 11:35, 12:30, 17:35, 18:00, 18:50, 20:20, 21:35, 22:20
rsE = RouteScheduleP(5, routeE, [
    (["07:35", "07:55"], False),
    (["11:35", "11:55"], True),
    (["12:30", "12:50"], False),
    (["17:35", "17:55"], True),
    (["18:00", "18:20"], False),
    (["18:50", "19:10"], True),
    (["20:20", "20:40"], False),
    (["21:35", "21:55"], True),
    (["22:20", "22:40"], False),
])
# rsF: 20min, start times:
# 07:10, 07:30, 08:00, 08:30, 09:00, 13:20, 13:40, 14:00, 15:10
rsF = RouteScheduleP(6, routeF, [
    (["07:10", "07:30"], False),
    (["07:30", "07:50"], True),
    (["08:00", "08:20"], False),
    (["08:30", "08:50"], False),
    (["09:00", "09:20"], False),
    (["13:20", "13:40"], False),
    (["13:40", "14:00"], True),
    (["14:00", "14:20"], False),
    (["15:10", "15:30"], False),
])
# rsG: start, +5, None, +45
# 06:40, 08:00, 09:35, 12:50, 14:30, 18:30, 22:05
rsG = RouteSchedule(7, routeG, [
    ["06:40", "06:45", None, "07:25"],
    ["08:00", "08:05", None, "08:50"],
    ["09:35", "09:40", None, "10:20"],
    ["12:50", "12:55", None, "13:35"],
    ["14:30", "14:35", None, "15:25"],
    ["18:30", "18:35", None, "19:25"],
    ["22:05", "22:10", None, "22:50"],
])
# rsH: start, +10, None, +45
# 06:50, 08:00, 12:50, 14:30, 18:30, 21:20, 22:05
rsH = RouteSchedule(8, routeH, [
    ["06:50", "07:00", None, "07:40"],
    ["08:00", "08:10", None, "09:00"],
    ["12:50", "13:00", None, "13:40"],
    ["14:30", "14:40", None, "15:25"],
    ["18:30", "18:40", None, "19:30"],
    ["21:20", "21:30", None, "22:00"],
    ["22:05", "22:15", None, "23:00"],
])
rsGweekend = RouteSchedule(9, routeG, [
    # 08:00, 13:40, 16:00, 21:50
    ["08:00", "08:05", None, "08:50"],
    ["13:40", "13:45", None, "14:30"],
    ["16:00", "16:05", None, "16:50"],
    ["21:50", "21:55", None, "22:40"]
])
rsHweekend = RouteSchedule(10, routeH, [
    # 07:00, 12:50, 18:30, 21:50
    ["07:00", "07:10", None, "07:50"],
    ["12:50", "13:00", None, "13:40"],
    ["18:30", "18:40", None, "19:30"],
    ["21:50", "22:00", None, "22:50"]
])


def convert(rsp: RouteScheduleP, is_weekend: bool) -> RouteSchedule:
    if is_weekend:
        # only return True times
        return RouteSchedule(rsp.id, rsp.route, [x[0] for x in rsp.time if x[1]])
    else:
        # return all
        return RouteSchedule(rsp.id, rsp.route, [x[0] for x in rsp.time])


class Message:
    def __init__(self, message: str, url: str):
        self.message = message
        self.url = url
    message: str
    url: str


class BusData:
    def __init__(self, campuses: list[Campus], routes: list[Route], weekday_routes: list[RouteSchedule],
                 weekend_routes: list[RouteSchedule], message: Message):
        self.campuses = campuses
        self.routes = routes
        self.weekday_routes = weekday_routes
        self.weekend_routes = weekend_routes
        self.message = message

    campuses: list[Campus]
    routes: list[Route]
    weekday_routes: list[RouteSchedule]
    weekend_routes: list[RouteSchedule]
    message: Message


data = BusData(
    campuses=[east, west, north, south, xianyanyuan, gaoxin],
    routes=[routeA, routeB, routeC, routeD, routeE, routeF, routeG, routeH],
    weekday_routes=list(map(
        lambda x: convert(x, False),
        [rsA, rsB, rsC, rsD, rsE, rsF]
    )) + [rsG, rsH],
    weekend_routes=list(map(
        lambda x: convert(x, True),
        [rsA, rsB, rsC, rsD, rsE, rsF]
    )) + [rsGweekend, rsHweekend],
    message=Message(
        message="本表为 2024 秋季学期时间表，来源：蜗壳小道消息",
        url="https://mp.weixin.qq.com/s/IQP3Qh2MNfwNJwiyvORr5g"
    )
)

data_json = jsonpickle.encode(data, unpicklable=False, indent=2)
# write to ./bus_data.json
with open(os.path.join(os.path.dirname(__file__), "bus_data_v3.json"), "w") as f:
    f.write(data_json)
