#!/bin/bash
tmp=`ls /dev/serial/by-id/usb-Prolific* 2>/dev/null | head -1`
file $tmp 2>/dev/null | grep -o -e ttyUSB[0-9][0-9]*
