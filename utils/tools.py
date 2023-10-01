import json


def parse_header(raw: str) -> dict:
    return {i.split(": ")[0]: i.split(": ")[1] for i in raw.split("\n")[1:-1]}


def save_json(obj: any, path: str):
    with open(path, "w") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)
