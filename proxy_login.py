import base64
import csv
import datetime
import json
import os
import time

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open('credentials.json', 'rt') as f:
    credentials = json.load(f)

logfile = os.path.abspath(u'proxy_login.log.csv')

print(u'program started at:', datetime.datetime.now())

# make log file dir
if not os.path.isdir(os.path.dirname(logfile)):
    assert not os.path.exists(os.path.dirname(logfile))
    os.makedirs(os.path.dirname(logfile))

# make log file
if not os.path.exists(logfile):
    with open(logfile, 'wt', newline='') as f:
        c = csv.writer(f)
        c.writerow([
            'timestamp',
            'connectivity',
            'login_redirect',
            'duration',
            'successfully_logged_in'
        ])

while True:

    # data to log
    data = {
        'timestamp':      datetime.datetime.now(),
        'connectivity':   1,
        'login_redirect': 0,
        'start_time':     time.time(),
        'logged_in':      0,
    }

    # attempt to login
    try:
        # make request to any https site
        r_init = requests.get(u'http://maps.google.com/',
                              verify=False,
                              timeout=30)
        print(r_init.url)

        # catch the redirect
        if u':8080/mwg-internal' in r_init.url:
            data['login_redirect'] = 1

            # log in
            print(u'caught redirect, logging in...')
            r_login = requests.post(r_init.url,
                                    headers={u'username': base64.b64encode(credentials['username'].encode('ascii')),
                                             u'password': base64.b64encode(credentials['password'].encode('ascii'))
                                             },
                                    verify=False,
                                    timeout=30)
            print(r_login.url)

            # resolve the url
            print(u'resolving url...')
            r_resolve = requests.get(r_login.url,
                                     verify=False,
                                     timeout=30)
            print(r_resolve.url)

            if u'google' in r_resolve.url:
                data['logged_in'] = 1

        elif u'google' in r_init.url:
            data['logged_in'] = 1

        # log the time
        if data['logged_in']:
            print(u'logged in')
        else:
            print(u'failed to login')

    except requests.exceptions.ConnectionError:
        data['connectivity'] = 0
        print(u'network is down! (connection error)')

    except requests.exceptions.Timeout:
        data['connectivity'] = 0
        print(u'network is down! (timeout)')

    # log to csv (ascii only)
    with open(logfile, 'at', newline='') as f:
        c = csv.writer(f)
        c.writerow([
            data['timestamp'],
            data['connectivity'],
            data['login_redirect'],
            time.time() - data['start_time'],
            data['logged_in'],
        ])

    # sleep 1 min
    print(u'going to sleep, time is:', datetime.datetime.now())
    time.sleep(60)
    print(u'')
    print(u'woke up at:', datetime.datetime.now())

