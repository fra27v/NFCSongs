#!/usr/bin/env python3
import sqlite3
import time
import os
import subprocess
from smartcard.System import readers
from smartcard.util import toHexString
import threading
import sys

DB_PATH = "nfc_music.db"
MP3_DIR = "mp3"
DEBOUNCE_SECONDS = 1
POLL_INTERVAL = 0.2

exit_requested = False

def exit_listener():
    global exit_requested
    while True:
        cmd = sys.stdin.readline().strip()
        if cmd.lower() == "q":
            exit_requested = True
            break


def get_reader():
    r = readers()
    return r[0] if r else None


def get_uid(reader):
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    try:
        conn = reader.createConnection()
        conn.connect()
        data, sw1, sw2 = conn.transmit(GET_UID)
        conn.disconnect()
        if sw1 == 0x90 and sw2 == 0x00:
            return toHexString(data).replace(" ", ":")
    except Exception:
        return None
    return None


def lookup_song(uid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title FROM tag_map WHERE uid = ?", (uid,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def start_player(filename):
    """Start mpg123 in remote control mode (-R)."""
    full_path = os.path.join(MP3_DIR, filename)
    print(f"?? Playing: {filename}")
    proc = subprocess.Popen(
        ["mpg123", "-q", "-R"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    time.sleep(0.1)
    proc.stdin.write(f"LOAD {full_path}\n")
    proc.stdin.flush()
    return proc


def stop_player(proc):
    if proc:
        try:
            proc.stdin.write("STOP\n")
            proc.stdin.flush()
        except:
            pass
        proc.kill()


def pause_player(proc):
    if proc:
        try:
            proc.stdin.write("PAUSE\n")
            proc.stdin.flush()
        except:
            pass


def resume_player(proc):
    if proc:
        try:
            proc.stdin.write("PAUSE\n")  # PAUSE toggles
            proc.stdin.flush()
        except:
            pass


def main():
    print("?? NFC Music Player ready.")

    last_uid = None
    current_uid = None
    player_proc = None
    is_paused = False
    last_read_time = 0

    # Start exit listener
    listener = threading.Thread(target=exit_listener, daemon=True)
    listener.start()

    while True:
        if exit_requested:
            print("?? Exiting cleanly...")
            stop_player(player_proc)
            return

        reader = get_reader()
        if not reader:
            print("?? No NFC reader found. Retrying...")
            time.sleep(1)
            continue

        uid = get_uid(reader)
        now = time.time()

        if uid:  # Tag present
            last_read_time = now

            if uid != current_uid:
                # New tag detected ? stop the previous song and play the new one
                stop_player(player_proc)
                player_proc = None
                is_paused = False

                song = lookup_song(uid)
                if song:
                    player_proc = start_player(song)
                    current_uid = uid
                else:
                    print(f"? No song associated with tag {uid}")
                    current_uid = uid

            else:
                # Same tag still present
                if is_paused:
                    # Resume playback
                    resume_player(player_proc)
                    is_paused = False

        else:  # No tag detected
            if current_uid is not None and not is_paused:
                # Tag was removed ? pause playback
                if player_proc:
                    print("??  Tag removed ? pausing")
                    pause_player(player_proc)
                    is_paused = True

            # After a pause with no tag, do not change current_uid
            # Only when a new tag appears we switch songs

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
