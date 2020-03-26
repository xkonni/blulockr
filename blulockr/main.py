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
    parser.add_argument("-n", "--noop", dest="noop", action="store_true",
            help="don't execute lock/unlock commands")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
            help="debug mode")
    parser.add_argument("-c", "--config", dest="config_file", type=str, default=CONFIG_FILE,
            help="config file")

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
    if not config.get("btdevice"):
        config["btdevice"] = BTDEVICE
    if not config.get("interval"):
        config["interval"] = INTERVAL
    if not config.get("ltype"):
        config["ltype"] = LTYPE
    # overwrite with arguments
    if args.btdevice:
        config["btdevice"] = args.btdevice
    if args.interval:
        config["interval"] = args.interval
    if args.ltype:
        config["ltype"] = args.ltype

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
    if args.noop:
        config["noop"] = args.noop
    else:
        config["noop"] = False
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
            interval=config.get("interval"), noop=config.get("noop"),
            debug=config.get("debug"))
    if config.get("scan") or not config.get("btdevice"):
        BL.scan()
    else:
        BL.run()


if __name__ == "__main__":
    main()
