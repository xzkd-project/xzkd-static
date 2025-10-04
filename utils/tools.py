import jsonpickle
from datetime import datetime, timedelta
from pytz import timezone
from typing import Any

tz = timezone("Asia/Shanghai")


def raw_date_to_unix_timestamp(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    tz_aware_datetime = tz.localize(dt)
    return int(tz_aware_datetime.timestamp())


def save_json(obj: Any, path: str) -> None:
    with open(path, "w") as f:
        encoded = jsonpickle.encode(obj, indent=4)
        if encoded is not None:
            f.write(encoded)
