#
# blulockr.py
# xkonni <konstantin.koslowski@gmail.com>
#

import bluetooth
import logging
import blulockr.locker as locker
import subprocess
import time

MAX_RETRIES = 5
MODE_LOCK = 1
MODE_UNLOCK = 2

class BluLockr:
    def __init__(self, ltype, btdevice, interval, mode=3, debug=False):
        self.ltype = ltype
        self.btdevice = btdevice
        self.interval = interval
        self.failcount = 0
        self.mode = mode
        self.debug = debug
        self.logger = logging.getLogger("BluLockr")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

        if self.ltype == "loginctl":
            self.locker = locker.LoginCtl(debug=self.debug)
        else:
            self.locker = locker.Locker(debug=self.debug)


    def scan(self):
        self.logger.info("scanning...")
        try:
            devices = bluetooth.discover_devices(lookup_names=True)
            self.logger.info(f"{len(devices)} devices found:")
            for d in devices:
                self.logger.info(f"\t{d[0]} {d[1]}")
        except Exception as ex:
            self.logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")


    def watch(self):
        t1 = time.time()
        try:
            ret = subprocess.run(["timeout", f"{self.interval}", "l2ping", self.btdevice,
                "-t", "0.5", "-c", "1"], shell=False, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except Exception as ex:
            self.logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")
        # handle specific errors
        if ret.stderr == b"Can't create socket: Operation not permitted\n":
            self.logger.warning(f"error: {ret.stderr.decode()}, run setup.sh as root!")
            return
        if ret.stderr == b"Can't connect: Device or resource busy\n":
            time.sleep(1)
            return

        if ret.returncode == 0:
            self.failcount = 0
            self.logger.debug(f"l2ping success, failcount: {self.failcount}")
            if self.locker.locked():
                if self.mode & MODE_UNLOCK:
                    self.logger.info("unlocking...")
                    self.locker.unlock()
                else:
                    self.logger.info("unlock disabled.")
        else:
            if not self.locker.locked():
                self.failcount += 1
                self.logger.debug(f"l2ping fail, failcount: {self.failcount}")
                if self.failcount > MAX_RETRIES:
                    if self.mode & MODE_LOCK:
                        self.logger.info("locking...")
                        self.locker.lock()
                    else:
                        self.logger.info("lock disabled.")
        t = self.interval - (time.time() - t1)
        self.logger.debug(f"sleep: {t}")
        if t > 0:
            time.sleep(t)


    def run(self):
        self.logger.info("running...")
        while True:
            self.watch()
