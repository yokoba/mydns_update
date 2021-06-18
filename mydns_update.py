import base64
import logging
import os
import sys
import urllib.request
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

logfile = Path(__file__).parent.joinpath("ip.log")
logger = logging.getLogger(__name__)
fh = TimedRotatingFileHandler(logfile, when="W0", backupCount=4)
fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.setLevel(logging.INFO)

GLOBAL_IP_CHECK_SITE = ["inet-ip.info/ip", "api.ipify.org"]


class IpManage:
    def __init__(self, mydns_id, mydns_pass):
        self.mydns_id = mydns_id
        self.mydns_pass = mydns_pass

        fname = "ip.txt"
        self.file = Path(__file__).parent.joinpath(fname)

        if self.file.exists():
            res = self.file.read_text().split(",")
            self.idx = int(res[0])
            self.ip = res[1]
            self.update_time = datetime.fromtimestamp(float(res[2]))
        else:
            self.idx, self.ip, self.update_time = (0, "", datetime.now())

        logger.debug(f"old ip: {self.ip}")

        if self.idx >= len(GLOBAL_IP_CHECK_SITE):
            self.idx = 0

        self.url = GLOBAL_IP_CHECK_SITE[self.idx]
        self.change = False

    def check(self):
        url = f"https://{self.url}"
        logger.debug(f"check url: {url}")
        with urllib.request.urlopen(url) as res:
            ip = res.read()
            self.new_ip = ip.decode("ascii")
        logger.debug(f"now ip: {self.new_ip}")

    def write(self):
        if self.change:
            w = f"{self.idx},{self.new_ip},{datetime.now().timestamp()}"
            self.file.write_text(w)

    def update(self):
        def up(ip: str, user_id, user_pass):
            user_pass = base64.b64encode(f"{user_id}:{user_pass}".encode("utf-8"))
            headers = {"Authorization": "Basic " + user_pass.decode("utf-8")}

            url = "https://ipv4.mydns.jp/login.html"

            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request) as res:
                _ = res.read()
            return True

        if self.update_time + timedelta(days=1) < datetime.now():
            logger.info("24H update")
            self.change = True
            up(self.new_ip, self.mydns_id, self.mydns_pass)
            return True

        if self.ip != self.new_ip:
            logger.info("ip change update")
            self.change = True
            up(self.new_ip, self.mydns_id, self.mydns_pass)
            return True

        logger.info("no update")
        return False


def get_environ():
    mydns_id = os.environ.get("mydns_id", None)
    mydns_pass = os.environ.get("mydns_pass", None)

    if not all([mydns_id, mydns_pass]):
        logger.error("Environment variable is not registered")
        sys.exit(False)

    return mydns_id, mydns_pass


if __name__ == "__main__":
    logger.info("check start")
    chk = IpManage(*get_environ())
    chk.check()
    chk.update()
    chk.write()
    logger.info("check end")
