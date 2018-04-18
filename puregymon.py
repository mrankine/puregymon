#!/usr/bin/env python
import os
import re
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

PUREGYM_LOGIN = "https://www.puregym.com/login/"
PUREGYM_LOGIN_API = "https://www.puregym.com/api/members/login"
PUREGYM_MEMBERS = "https://www.puregym.com/members/"

FILE_MEMBERS = "members.csv"
FILE_CREDENTIALS = ".puregym_credentials"

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

    with open("temp_login.html", "w") as f:
        f.write(r.text)

    return r.cookies

def count_members(url, cookies):
    r = requests.get(url, cookies=cookies)

    soup = BeautifulSoup(r.text, "html.parser")
    span = soup.find("span", class_="heading heading--level3 secondary-color margin-none")
    t = span.text

    m = re.match(r"\d+", t)
    if m:
        count = int(m.group())
        if re.match(r"Fewer than \d+ people", t):
            print "Gym reports members at lower bound of %d" % count
        return count
    else:
        return -1
    
def record_members(members_log, members):
    with open(os.path.join(__location__, members_log), "a") as f:
        f.write("%s,%s\n" % (datetime.now().strftime(r"%Y/%m/%d %H:%M:%S"), members))

__location__ = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    username = None
    pin = None
    try:
        with open(os.path.join(__location__, FILE_CREDENTIALS)) as f:
            l = f.readline().strip().split(" ")
            username = l[0]
            pin = l[1]
            print "Using credentials {%s, %s}" % (username, pin)
    except Exception as x:
        print "Failed to read credentials file"
        quit()

    session, token = get_session(PUREGYM_LOGIN)
    #print "Session: %s" % session
    #print "Token: %s" % token

    loggedin_session = login(PUREGYM_LOGIN_API, session, token, username, pin)
    #print "Logged in session: %s" % loggedin_session

    members = count_members(PUREGYM_MEMBERS, loggedin_session)
    if members is not -1:
        record_members(FILE_MEMBERS, members)