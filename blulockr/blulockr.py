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

class BluLockr:
    def __init__(self, ltype, btdevice, interval, noop=False, debug=False):
        self.ltype = ltype
        self.btdevice = btdevice
        self.interval = interval
        self.failcount = 0
        self.noop = noop
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
        try:
            ret = subprocess.run(["l2ping", self.btdevice, "-t", "1", "-c", "1"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # handle specific errors
            if ret.stderr == b"Can't create socket: Operation not permitted\n":
                self.logger.warning(f"error: {ret.stderr.decode()}, run setup.sh as root!")
                return
            if ret.stderr == b"Can't connect: Device or resource busy\n":
                time.sleep(1)
                return

            r = ret.returncode
            self.logger.debug(f"l2ping success, failcount: {self.failcount}")
            if r == 0:
                self.failcount = 0
                if self.locker.locked():
                    self.logger.info("unlocking...")
                    if not self.noop:
                        self.locker.unlock()
            elif r == 1:
                if not self.locker.locked():
                    self.failcount += 1
                    self.logger.debug(f"l2ping fail, failcount: {self.failcount}")
                    if self.failcount > MAX_RETRIES:
                        self.logger.info("locking...")
                        if not self.noop:
                            self.locker.lock()
            time.sleep(self.interval)
        except Exception as ex:
            self.logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")


    def run(self):
        self.logger.info("running...")
        while True:
            self.watch()
