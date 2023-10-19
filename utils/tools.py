import jsonpickle
from datetime import datetime, timedelta
from pytz import timezone

tz = timezone('Asia/Shanghai')


def raw_date_to_unix_timestamp(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    tz_aware_datetime = tz.localize(dt)
    return int(tz_aware_datetime.timestamp())


def parse_header(raw: str) -> dict:
    return {i.split(": ")[0]: i.split(": ")[1] for i in raw.split("\n")[1:-1]}


def save_json(obj: any, path: str):
    with open(path, "w") as f:
        f.write(jsonpickle.encode(obj, indent=4))
