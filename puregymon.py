#!/usr/bin/env python3
import csv
import os
import re
import sys
from datetime import date, time, datetime

import requests
from bs4 import BeautifulSoup

PUREGYM_LOGIN = "https://www.puregym.com/login/"
PUREGYM_LOGIN_API = "https://www.puregym.com/api/members/login"
PUREGYM_MEMBERS = "https://www.puregym.com/members/"
PUREGYM_ACTIVITY = "https://www.puregym.com/members/activity/?view=year"

CONFIGFILE_CREDENTIALS = ".puregym_credentials"
CONFIGFILE_OUTPUTDIR = ".puregym_outputdir"
FILE_HEADCOUNT = "headcount.csv"
FILE_ACTIVITY = "activity.csv"

def get_session(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    tag = soup.find("input", {"name": "__RequestVerificationToken"})
    token = tag["value"]
    return r.cookies, token

def login(url, cookies, token, username, pin):
    headers = {
        "Content-Type": "application/json",
         "__requestverificationtoken": token
         }
    data = {
        "email": username,
        "pin": pin
        }
    r = requests.post(url, headers=headers, cookies=cookies, json=data)

    return r.cookies

def count_members(url, cookies):
    r = requests.get(url, cookies=cookies)

    soup = BeautifulSoup(r.text, "html.parser")
    span = soup.find("span", class_="heading heading--level3 secondary-color margin-none")
    t = span.text

    m = re.search(r"\d+", t)
    if m:
        count = int(m.group())
        if re.search(r"Fewer than \d+ people", t):
            print("Gym reports members at lower bound of {count}.".format(count=count))
        return count
    else:
        return -1
    
def record_members(filename, members):
    with open(os.path.join(__location__, filename), "a") as f:
        f.write("{ts},{c}\n".format(ts=datetime.now().strftime(r"%Y/%m/%d %H:%M:%S"), c=members))

def get_activity(url, cookies):
    activity = []

    # Maps logical keys to css classnames in PureGym html
    cols = {
        "date": "calendar-card__date",
        "entry_time": "calendar-card__entry-time",
        "gym": "calendar-card__gym",
        "class": "calendar-card__class",
        "duration": "calendar-card__duration",
    }

    r = requests.get(url, cookies=cookies)

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all("div", class_="calendar-card calendar-card--static")
    if rows is None:
        return None
    for r in rows:
        record = {}
        for col_label, col_selector  in cols.items():
            cell = r.find("div", class_=col_selector)
            if cell is None:
                continue
            t = cell.text.strip()
            record[col_label] = t

        activity.append({
            "datetime": str(
                datetime.combine(
                    datetime.strptime(record["date"], r"%d/%m/%Y"),
                    datetime.strptime(record["entry_time"], r"%H:%M").timetz()
                )),
            "gym": record["gym"],
            "class": record["class"],
            "duration": record["duration"].replace(" minutes", "")
        })

    activity.reverse()
    return activity

def save_activity(filename, activity):
    with open(os.path.join(__location__, filename), "a+") as f:
        f.seek(0)
        existing = list(f)
        for record in activity:
            pickled_record = ",".join((record["datetime"], record["gym"], record["class"], record["duration"])) + "\n"
            if pickled_record not in existing:
                print("Saving new activity: {r}".format(r=record))
                f.write(pickled_record)

__location__ = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    username = None
    pin = None
    try:
        with open(os.path.join(__location__, CONFIGFILE_CREDENTIALS)) as f:
            l = f.readline().strip().split(" ")
            username = l[0]
            pin = l[1]
            print("Using credentials {username}, {pin}.".format(username=username, pin=pin))
    except Exception as x:
        print("Failed to read credentials file!")
        quit()

    try:
        with open(os.path.join(__location__, CONFIGFILE_OUTPUTDIR)) as f:
            o = f.readline().strip()
            FILE_HEADCOUNT = os.path.join(o, FILE_HEADCOUNT)
            FILE_ACTIVITY = os.path.join(o, FILE_ACTIVITY)
            print("Using output directory: {o}".format(o=o))
    except Exception as x:
        print("Failed to read output directory from config file - assuming current working directory")

    session, token = get_session(PUREGYM_LOGIN)

    loggedin_session = login(PUREGYM_LOGIN_API, session, token, username, pin)

    members = count_members(PUREGYM_MEMBERS, loggedin_session)
    if members is not -1:
        record_members(FILE_HEADCOUNT, members)
        print("Current headcount: {count}.".format(count=members))
    else:
        print("Could not get current headcount.")

    activity = get_activity(PUREGYM_ACTIVITY, loggedin_session)
    save_activity(FILE_ACTIVITY, activity)
