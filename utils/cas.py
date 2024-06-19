import json
import urllib.parse

from utils.environs import USTC_PASSPORT_USERNAME, USTC_PASSPORT_PASSWORD


def cas_login_data(cas_lt: str, lt: str) -> json:
    return {
        "model": "uplogin.jsp",
        "CAS_LT": cas_lt,
        "service": "https://jw.ustc.edu.cn/ucas-sso/login",
        "warn": "",
        "showCode": "1",
        "resultInput": "",
        "qrcode": "",
        "username": USTC_PASSPORT_USERNAME,
        "password": USTC_PASSPORT_PASSWORD,
        "LT": lt,
    }


def cas_login_data_str(lt: str) -> str:
    data = cas_login_data(lt)
    return "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in data.items()])
