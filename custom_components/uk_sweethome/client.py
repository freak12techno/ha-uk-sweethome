import requests
import logging

_LOGGER = logging.getLogger(__name__)

class UkSweethomeClient:
    def __init__(self, hass, username, password):
        self.host = "https://api.sm-center.ru"
        self.company = "kapitalinvest_ooo_yk_cvitxom2"

        self.hass = hass
        self.username = username
        self.password = password
        self.token = None

    def auth(self):
        request = requests.post(
            "{self.host}/{self.company}/auth/login",
            json={"phone": self.username, "password": self.password}
        )
        body = request.json()
        self.token = body.acx

    def getRequest(self, url):
        try:
            request = requests.get(
                url,
                headers={"acx": self.token}
            )
            body = request.json()
            return body
        except Exception:
            self.auth()
            request = requests.get(
                url,
                headers={"acx": self.token}
            )
            body = request.json()
            return body


    def accounting(self):
        return self.getRequest("{self.host}/{self.company}/Accounting/Info")
