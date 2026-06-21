import hashlib
from pathlib import Path

from homematicip_demo.fake_cloud_server import AsyncFakeCloudServer


class FakeHcuServer(AsyncFakeCloudServer):
    """A fake server simulating a direct local hCU (HomematicIP Control Unit) connection.

    Unlike the cloud server, the hCU is reached directly on the local network.
    The same REST and WebSocket endpoints are used, but the /getHost lookup
    returns the device's own address instead of cloud URLs.
    """

    HCU_HOME_PATH = Path(__file__).parent.joinpath("json_data/hcu_home.json")
    HCU_SGTIN = "3014F711A000000HCU00001"
    HCU_HOME_ID = "00000000-0000-0000-0000-000000000002"
    HCU_CLIENT_AUTH_TOKEN = (
        hashlib.sha512((HCU_SGTIN + "jiLpVitHvWnIGD1yo7MA").encode("utf-8"))
        .hexdigest()
        .upper()
    )

    def __init__(self, home_path=None):
        if home_path is None:
            home_path = self.HCU_HOME_PATH
        self.reset(home_path=home_path)

    def reset(self, home_path=None):
        if home_path is None:
            home_path = self.HCU_HOME_PATH

        import json

        with open(home_path, encoding="utf-8") as file:
            self.data = json.load(file)

        self.sgtin = self.HCU_SGTIN
        self.client_auth_token = self.HCU_CLIENT_AUTH_TOKEN
        self.client_token_map = {
            "00000000-0000-0000-0000-000000000000": "8A45BAA53BE37E3FCA58E9976EFA4C497DAFE55DB997DB9FD685236E5E63ED7DE"
        }
        self.pin = None
        self.client_auth_waiting = None
        self.home_id = self.HCU_HOME_ID
        self.ws = None
