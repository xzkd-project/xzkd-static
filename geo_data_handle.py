import os
from json import load, dump
from pprint import pprint

# read from geo_data_tmp.json


def read_geo_data():
    with open('geo_data_tmp.json', 'r') as f:
        geo_data = load(f)
    return geo_data


if __name__ == '__main__':
    json = read_geo_data()
    # turn each string into [lat, long]
    for key in json:
        json[key] = json[key].split(',')

    # calc: offset = json["base_moved"] - json["base"]:
    offset = [float(json["base_moved"][0]) - float(json["base"][0]),
              float(json["base_moved"][1]) - float(json["base"][1])]

    del (json["base"])
    del (json["base_moved"])

    for key in json:
        json[key] = [float(json[key][0]) - offset[0],
                     float(json[key][1]) - offset[1]]

    # export in format:
    # [{"name": "name", "latitude": lat, "longitude": long}, ...]
    export = []
    for key in json:
        export.append(
            {"name": key, "latitude": json[key][0], "longitude": json[key][1]})

    pprint(export)

    # write to geo_data_export.json:
    with open('geo_data_export.json', 'w') as f:
        dump(export, f)
