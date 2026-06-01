#!/bin/bash

sleep 35

bluetoothctl disconnect 6C:47:60:20:04:46
sleep 2

for i in 1 2 3 4 5 6 7 8 9 10; do
    bluetoothctl connect 6C:47:60:20:04:46 && break
    sleep 5
done

sleep 5

cd /home/pi/NFCSongs
exec /usr/bin/python3 player.py