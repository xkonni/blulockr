#!/usr/bin/env python3
#
# main.py
# xkonni <konstantin.koslowski@gmail.com>
#

import argparse
import json
import logging
from xdg import XDG_CONFIG_HOME
# local
from blulockr.blulockr import BluLockr

# defaults
CONFIG_FILE=f"{XDG_CONFIG_HOME}/blulockr.json"
BTDEVICE = None
INTERVAL = 3
LTYPE = "undefined"
LTYPES = ["undefined", "loginctl"]
# 0: disable, 1: lock only, 2: unlock only, 3: both
MODE = 3

# runtime
logger = None


def setup():
    global logger

    # arguments
    parser = argparse.ArgumentParser(description="blulockr")
    parser.add_argument("-b", "--btdevice", dest="btdevice", type=str,
            help="bluetooth device to monitor")
    parser.add_argument("-i", "--interval", dest="interval", type=int,
            help="monitor interval")
    parser.add_argument("-t", "--ltype", dest="ltype", type=str,
            help=f"locker type [{', '.join(t for t in LTYPES)}]")
    parser.add_argument("-s", "--scan", dest="scan", action="store_true",
            help="scan for devices")
    parser.add_argument("-m", "--mode", dest="mode", type=int,
            help="mode, 0: disable, 1: lock, 2: unlock, 3: both [default]")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
            help="debug mode")
    parser.add_argument("-c", "--config", dest="config_file", type=str,
            default=CONFIG_FILE, help="config file")

    # parse arguments
    args = parser.parse_args()

    # initialize config
    config = {}
    try:
        with open(args.config_file, "r") as config_file:
            config = json.load(config_file)
    except Exception as ex:
        logger.warning(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")

    # fill new keys with defaults
    if not "btdevice" in config:
        config["btdevice"] = BTDEVICE
    if not "interval" in config:
        config["interval"] = INTERVAL
    if not "ltype" in config:
        config["ltype"] = LTYPE
    if not "mode" in config:
        config["mode"] = MODE
    # overwrite with arguments
    if args.btdevice is not None:
        config["btdevice"] = args.btdevice
    if args.interval is not None:
        config["interval"] = args.interval
    if args.ltype is not None:
        config["ltype"] = args.ltype
    if args.mode is not None:
        config["mode"] = args.mode

    # save updated config
    try:
        with open(args.config_file, "w") as config_file:
            json.dump(config, config_file, indent=4, sort_keys=True)
    except Exception as ex:
        logger.error(f"Exception, Type:{type(ex).__name__}, args:{ex.args}")

    # temporary options
    if args.scan:
        config["scan"] = args.scan
    else:
        config["scan"] = False
    if args.debug:
        config["debug"] = args.debug
    else:
        config["debug"] = False

    return config


def main():
    global logger
    FORMAT="[%(asctime)13s : %(name)12s : %(levelname)7s : %(funcName)s()] %(message)s"
    DATEFMT="%Y%m%d %H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=FORMAT,
            datefmt=DATEFMT)
    logger = logging.getLogger("main")
    config = setup()
    if config.get("debug"):
        logger.setLevel(logging.DEBUG)

    logger.debug(f"config: {config}")

    BL = BluLockr(ltype=config.get("ltype"), btdevice=config.get("btdevice"),
            interval=config.get("interval"), mode=config.get("mode"),
            debug=config.get("debug"))
    if config.get("scan") or not config.get("btdevice"):
        BL.scan()
    else:
        BL.run()


if __name__ == "__main__":
    main()
