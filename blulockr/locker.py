#
# locker.py
# xkonni <konstantin.koslowski@gmail.com>
#

import logging
import subprocess

class Locker:
    def __init__(self, ltype="simulate", debug=False):
        self.ltype = ltype
        self.debug = debug
        self.logger = logging.getLogger(f"Lockr:{self.ltype}")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

        if self.ltype == "loginctl":
            self.lock_cmd = ["loginctl", "lock-session"]
            self.unlock_cmd = ["loginctl", "unlock-session"]
        else:
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