#!/bin/bash
#
# setup.sh
# xkonni <konstantin.koslowski@gmail.com>
#
# allow l2ping to run as user
#

CMD=l2ping
FILE=$(which $CMD 2> /dev/null)

if [ $? -ne 0 ]; then
  echo "missing $CMD executable, exiting..."
  exit 0
fi

sudo setcap cap_net_raw+ep $FILE
