# NFC Music Box

Turn NFC tags (e.g., NTAG215 stickers) into triggers for MP3 music playback using:

- Raspberry Pi 4 or 5
- ACR122U NFC USB Reader
- Python 3 + pyscard
- mpg123 audio player
- SQLite database for tag ? song mapping

This document lists all steps needed to replicate the setup on any Raspberry Pi.

------------------------------------------------------------
1. Raspberry Pi OS Preparation
------------------------------------------------------------

Update system:

    sudo apt update
    sudo apt upgrade -y
    sudo reboot
------------------------------------------------------------
2. Required Packages
------------------------------------------------------------

Install Python and Pip:

    sudo apt install -y python3 python3-pip python3-venv

Install PC/SC smart card stack:

    sudo apt install -y pcscd pcsc-tools libccid

Install MP3 player:

    sudo apt install -y mpg123

Install SQLite:

    sudo apt install -y sqlite3

Install Python libraries:

    pip3 install pyscard

Verify pyscard:

    python3 -c "import smartcard; print('pyscard OK')"

------------------------------------------------------------
3. ACR122U Driver Notes
------------------------------------------------------------

Most ACR122U units work with the built-in CCID driver.
If detection issues occur, install the ACS proprietary driver:

    sudo apt install -y libacsccid1
    sudo reboot

If the reader becomes unresponsive: unplug and replug the USB cable.
------------------------------------------------------------
4. Verifying the NFC Reader
------------------------------------------------------------

Run:

    pcsc_scan

Expected output:

    0: ACS ACR122U PICC Interface 00 00

If it hangs at �Waiting for the first reader��
? unplug/replug the reader.

------------------------------------------------------------
5. Project Folder Structure
------------------------------------------------------------

NFCSongs/
 +-- assign_tag.py
 +-- player.py
 +-- nfc_music.db       (auto-created)
 +-- mp3/
       +-- song1.mp3
       +-- song2.mp3

------------------------------------------------------------
6. Script: assign_tag.py
------------------------------------------------------------

This script:
- Takes a song filename as argument
- Waits for an NFC tag
- Reads its UID
- Saves UID ? song filename into SQLite

Usage:

    python3 assign_tag.py "Quarantaquattro gatti.mp3"

IMPORTANT:
Ensure the script includes:

    conn.disconnect()

After reading the UID, otherwise the ACR122U stays locked.
------------------------------------------------------------
7. Script: player.py
------------------------------------------------------------

This script:
- Continuously detects NFC tags
- Looks up the mapped song in SQLite
- Plays the MP3 using mpg123
- Avoids retriggering via debounce
- Properly disconnects from PCSC after every read

Run it:

    python3 player.py

Stop with CTRL+C.

------------------------------------------------------------
8. SQLite Database Format
------------------------------------------------------------

Created automatically by assign_tag.py.

Table:

    tag_map(uid TEXT PRIMARY KEY, title TEXT)

Example:

    04:AB:CD:EF:12:34:56 ? Quarantaquattro gatti.mp3

Inspect database:

    sqlite3 nfc_music.db
    sqlite> SELECT * FROM tag_map;
------------------------------------------------------------
9. Autostart at Boot (optional)
------------------------------------------------------------

Create systemd service:

    sudo nano /etc/systemd/system/nfcplayer.service

Paste:

[Unit]
Description=NFC Music Player
After=pcscd.service sound.target

[Service]
WorkingDirectory=/home/pi/NFCSongs
ExecStart=/usr/bin/python3 /home/pi/NFCSongs/player.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

Enable autostart:

    sudo systemctl enable nfcplayer.service
    sudo systemctl start nfcplayer.service

Check:

    systemctl status nfcplayer.service

------------------------------------------------------------
10. USB Reset Trick (only if needed)
------------------------------------------------------------

If the reader stops responding:

    lsusb -t

Locate device path, e.g.:

    /sys/bus/usb/devices/3-2

Reset it:

    echo "3-2" | sudo tee /sys/bus/usb/drivers/usb/unbind
    sleep 1
    echo "3-2" | sudo tee /sys/bus/usb/drivers/usb/bind

This avoids rebooting the Raspberry Pi.
------------------------------------------------------------
11. Common Issues
------------------------------------------------------------

? "No NFC reader found":
- ACR122U locked
- pcscd not triggered
- unplug/replug the reader
- ensure conn.disconnect() in both scripts
- ensure you're using python3, not python2

? pcsc_scan shows nothing:
- ACR122U in bad CCID/firmware mode
- unplug/replug OR install libacsccid1

? Python sees [] as reader list:
Restart socket:

    sudo systemctl restart pcscd.socket

------------------------------------------------------------
12. Tags Used
------------------------------------------------------------

This project works with:

- NTAG213
- NTAG215
- NTAG216
- Mifare Ultralight (most)

Only the UID is used, not tag memory.

------------------------------------------------------------
13. Summary
------------------------------------------------------------

? Raspberry Pi + ACR122U + PCSC stack working  
? Python 3 with pyscard  
? Tag ? song mapping via SQLite  
? assign_tag.py for mapping  
? player.py for playback  
? Optional autostart with systemd  
? USB recovery procedure included  

This README explains everything required to deploy the NFC music player on any Raspberry Pi.

------------------------------------------------------------
END
------------------------------------------------------------
