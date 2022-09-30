#!/usr/bin/python3
import time
import os
import argparse
import subprocess
import threading
import signal
import sys


LOCK_TIME = 10 * 60
LOCK_PATH = "/usr/local/bin/slock"
LID_PATH = "/proc/acpi/button/lid/LID/state"
SCREEN_OFF = "xset dpms force off"
REFRESH_RATE = 0.2


def arg_parse():
    parser = argparse.ArgumentParser(description="Power managment")
    parser.add_argument("-l", "--locker", type=str, help="give path to screenlocker")
    parser.add_argument(
        "-t", "--time", type=int, help="time in minutes to lock while idle"
    )
    parser.add_argument(
        "-v", "--verbose", help="increse output verbosity", action="store_true"
    )
    args = parser.parse_args()
    return (
        args.locker if args.locker else LOCK_PATH,
        args.time if args.time else LOCK_TIME,
        args.verbose
    )


LOCK_PATH, LOCK_TIME, VERBOSE = arg_parse()

if VERBOSE:
    print(LOCK_PATH, LOCK_TIME)

def signal_handler(sig, frame):
    print('\nExiting pyautolock')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()

def get_idle():
    idle_time = int(subprocess.getoutput("xprintidle")) / 1000
    if VERBOSE:
        print(idle_time)
    return idle_time


def lid_closed():
    with open(LID_PATH, "r") as lid_file:
        return "closed" in lid_file.read()


def lock():
    os.system(SCREEN_OFF)
    os.system(LOCK_PATH)


def slock():
    subprocess.run(LOCK_PATH)


def suspend():
    os.system("systemctl suspend")


def main():
    while True:
        if lid_closed():
            lock()
        if get_idle() > LOCK_TIME:
            slock_thr = threading.Thread(target=slock)
            suspend_thr = threading.Thread(target=suspend)
            slock_thr.start()
            suspend_thr.start()
            slock_thr.join()
            suspend_thr.join()
        time.sleep(REFRESH_RATE)


if __name__ == "__main__":
    main()
