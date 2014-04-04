#! /usr/bin/env python

from sys import argv
import os.path
import requests

PUSH_URL = "https://api.pushbullet.com/api/pushes"

# utility methods
# ===============

def is_url(string):
    if " " in string:
        return False
    elif string[0:7] == "http://":
        return True
    elif string[0:8] == "https://":
        return True
    else:
        return False

def nickname_for(device):
    extras = device[u"extras"]
    if u"nickname" in extras:
        return extras[u"nickname"]
    else:
        return extras[u"model"]

# get the API key
# ===============

key_path = os.path.expanduser("~/.pushbulletkey")
if not os.path.isfile(key_path):

    print "What's your API key?"
    print "Find it at <https://www.pushbullet.com/account>."
    api_key = raw_input("> ").strip()
    with open(key_path, "w") as api_file:
        api_file.write(api_key)

    if len(argv) < 2:
        exit(0)

else:

    api_key = open(key_path, "r").read().strip()

    if len(argv) < 2:
        print "Please provide something to push!"
        exit(1)

# get the list of devices
# =======================

r = requests.get("https://api.pushbullet.com/api/devices", auth=(api_key, ""))

if (r.status_code == 401) or (r.status_code == 403):
    print "Bad API key. Check " + key_path + "."
    exit(1)

elif r.status_code != 200:
    print "Request failed with code " + str(r.status_code) + "."
    print "Try again?"
    exit(1)

devices = r.json()[u"devices"]

# pick the device to use
# ======================

push_to = None

if len(devices) < 1:
    print "You don't have any devices!"
    print "Add one at <https://www.pushbullet.com/>."
    exit(1)

elif len(devices) == 1:
    push_to = devices[0]

else:

    for i in xrange(len(devices)):

        device = devices[i]
        nickname = nickname_for(device)
        index = str(i + 1)

        print "[" + index + "]",
        if i == 0:
            print nickname,
            print "(default)"
        else:
            print nickname

    choice = -1
    while (choice < 0) or (choice > len(devices)):
        input = raw_input("Push to which device? ").strip()
        if input == "":
            choice = 0
        else:
            choice = int(input) - 1

    push_to = devices[choice]

# push!
# =====

print "Pushing to " + nickname_for(push_to) + "..."

data = {
    "device_iden": push_to[u"iden"]
}
file = None

argument = " ".join(argv[1:])

if is_url(argument):
    data["type"] = "link"
    data["title"] = "Link"
    data["url"] = argument
elif os.path.isfile(argument):
    data["type"] = "file"
    file = argument
else:
    data["type"] = "note"
    data["title"] = "Note"
    data["body"] = argument

r = None
if file == None:
    r = requests.post(
        PUSH_URL,
        auth=(api_key, ""),
        data=data
    )
else:
    r = requests.post(
        PUSH_URL,
        auth=(api_key, ""),
        data=data,
        files={ "file": open(file, "rb") }
    )

if r.status_code == 200:
    print "Pushed!"
else:
    print "Failed with status code " + str(r.status_code) + "."
    exit(1)