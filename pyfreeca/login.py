import requests
import json


def login_func():
    login_url = "https://login.afreecatv.com/app/LoginAction.php"

    username = json.load(open("../config.json", "r")).get("username")
    password = json.load(open("../config.json", "r")).get("password")

    form_data = {
        "szWork": "login",
        "szType": "json",
        "szUid": username,
        "szPassword": password,
        "isSaveId": "true",
        "szScriptVar": "oLoginRet",
        "szAction": ""
    }

    session = requests.Session()

    login_in = session.post(login_url, data=form_data)
    return session

