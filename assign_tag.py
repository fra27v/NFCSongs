#!/usr/bin/env python3
import sys
import sqlite3
import time
from smartcard.System import readers
from smartcard.util import toHexString

DB_PATH = "nfc_music.db"


# Ensure the table exists
def ensure_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tag_map (
            uid TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


# Write mapping to DB
def save_mapping(uid, title):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO tag_map (uid, title) VALUES (?, ?);",
        (uid, title),
    )
    conn.commit()
    conn.close()


# Wait until a tag is presented
def wait_for_tag():
    r = readers()
    if not r:
        print("? No NFC reader found.")
        sys.exit(1)

    reader = r[0]
    print(f"? NFC reader detected: {reader}")
    print("?? Present the NFC tag now...")

    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]

    while True:
        try:
            conn = reader.createConnection()
            conn.connect()

            data, sw1, sw2 = conn.transmit(GET_UID)

            # VERY IMPORTANT!!!!
            conn.disconnect()

            if sw1 == 0x90 and sw2 == 0x00:
                uid = toHexString(data).replace(" ", ":")
                return uid

        except Exception:
            # No tag present; wait a bit
            time.sleep(0.2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 assign_tag.py <song_filename.mp3>")
        sys.exit(1)

    song_title = sys.argv[1]

    # Prepare DB
    ensure_table()

    print(f"?? Ready to associate tag with: {song_title}")
    uid = wait_for_tag()

    print(f"?? Tag detected: {uid}")
    save_mapping(uid, song_title)
    print(f"? Saved: {uid} ? {song_title}")


if __name__ == "__main__":
    main()
