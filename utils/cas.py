import json
import urllib.parse

from utils.environs import (
    USTC_PASSPORT_USERNAME,
    USTC_PASSPORT_PASSWORD,
    USTC_PASSPORT_FINGERPRINT,
)


def cas_login_data(
    cas_lt: str,
    lt: str,
    service: str = "https://jw.ustc.edu.cn/ucas-sso/login",
) -> json:
    return {
        "model": "uplogin.jsp",
        "CAS_LT": cas_lt,
        "service": service,
        "warn": "",
        "showCode": "1",
        "resultInput": USTC_PASSPORT_FINGERPRINT,
        "qrcode": "",
        "username": USTC_PASSPORT_USERNAME,
        "password": USTC_PASSPORT_PASSWORD,
        "LT": lt,
    }


def cas_login_data_str(lt: str) -> str:
    data = cas_login_data(lt)
    return "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in data.items()])
