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
    def __init__(self, ltype, btdevice, interval, debug=False):
        self.ltype = ltype
        self.btdevice = btdevice
        self.interval = interval
        self.locked = 0
        self.failcount = 0
        self.debug = debug
        self.logger = logging.getLogger("BluLockr")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

        self.locker = locker.Locker(ltype=self.ltype, debug=self.debug)
    

    def scan(self):
        self.logger.info("scanning...")
        try:
            devices = bluetooth.discover_devices(lookup_names=True)
            self.logger.info("devices found:")
            for d in devices:
                self.logger.info(f"\t{d[0]} {d[1]}")
        except Exception as ex:
            self.logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")


    def watch(self):
        try:
            ret = subprocess.run(["l2ping", self.btdevice, "-t", "1", "-c", "1"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if ret.stderr == b"Can't create socket: Operation not permitted\n":
                self.logger.warning(f"error: {ret.stderr.decode()}")
                return

            r = ret.returncode
            if r == 0:
                self.logger.debug(f"returncode: {r}")
                self.failcount = 0
                if self.locked:
                    self.logger.info("unlocking...")
                    self.locked = False
                    self.locker.unlock()
            elif r == 1:
                self.logger.debug(f"ret: {ret}")
                if not self.locked:
                    self.failcount += 1
                    self.logger.debug(f"failcount: {self.failcount}")
                    if self.failcount > MAX_RETRIES:
                        self.logger.info("locking...")
                        self.failcount = 0
                        self.locked = True
                        self.locker.lock()
        except Exception as ex:
            self.logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")


    def run(self):
        self.logger.info("running...")
        while True:
            self.watch()
            time.sleep(self.interval)