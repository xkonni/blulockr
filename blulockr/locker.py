#
# locker.py
# xkonni <konstantin.koslowski@gmail.com>
#

import logging
import re
import subprocess

class Locker:
    def __init__(self, ltype="undefined", debug=False):
        self.ltype = ltype
        self.debug = debug
        self.logger = logging.getLogger(f"locker")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

        self.lock_cmd = ["/usr/bin/touch", "/tmp/lock"]
        self.unlock_cmd = ["/usr/bin/touch", "/tmp/unlock"]


    def lock(self):
        try:
            ret = subprocess.run(self.lock_cmd)
            self.logger.debug(f"ret: {ret}")
        except Exception as ex:
            self.logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")


    def unlock(self):
        try:
            ret = subprocess.run(self.unlock_cmd)
            self.logger.debug(f"ret: {ret}")
        except Exception as ex:
            self.logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")

    def locked(self):
        return False


class LoginCtl(Locker):
    def __init__(self, debug=False):
        self.ltype = "loginctl"
        super().__init__(ltype=self.ltype, debug=debug)
        self.lock_cmd = ["/usr/bin/loginctl", "lock-session"]
        self.unlock_cmd = ["/usr/bin/loginctl", "unlock-session"]
        self.sessionid = self.get_sessionid()
        self.logger.info(f"{self.ltype} ready")

    def get_sessionid(self):
        ret = subprocess.run(["/usr/bin/loginctl", "list-sessions"], stdout=subprocess.PIPE)
        sessionid = 0
        for line in ret.stdout.decode().split("\n"):
            if "seat" in line:
                words = re.findall(r'\w+', line)[0]
                sessionid = words[0]

        self.logger.debug(f"sessionid: {sessionid}")
        return sessionid


    def locked(self):
        ret = subprocess.run(["/usr/bin/loginctl", "show-session", self.sessionid], stdout=subprocess.PIPE)
        res = False
        for line in ret.stdout.decode().split("\n"):
            if "LockedHint" in line:
                locked = line.split("=")[1]
                if locked == "no":
                    res = False
                elif locked == "yes":
                    res =  True
                else:
                    self.logger.error(f"locked: {locked}")
        self.logger.debug(f"locked: {res}")
        return res
