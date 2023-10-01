import json
import urllib.parse

from utils.environs import USTC_PASSPORT_USERNAME, USTC_PASSPORT_PASSWORD


def cas_login_data(lt: str) -> json:
    return {
        "model": "uplogin.jsp",
        "CAS_LT": lt,
        "service": "https://jw.ustc.edu.cn/ucas-sso/login",
        "warn": "",
        "showCode": "",
        "qrcode": "",
        "username": USTC_PASSPORT_USERNAME,
        "password": USTC_PASSPORT_PASSWORD,
        "LT": "",
        "button": "",
    }


def cas_login_data_str(lt: str) -> str:
    data = cas_login_data(lt)
    return "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in data.items()])
