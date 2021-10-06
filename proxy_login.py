import base64
import csv
import datetime
import json
import time
from pathlib import Path

import requests

# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# files
credentials_path = Path('credentials.json')
logfile_path = Path('proxy_login.log.csv')

# site to load
site = 'https://www.bing.com/'
expect_string = 'bing'


def main():
    print('program started at:', datetime.datetime.now())

    # load username and password
    with credentials_path.open(encoding='utf8') as f:
        credentials = json.load(f)
        credentials_header = {
            'username': base64.b64encode(credentials['username'].encode('ascii')),
            'password': base64.b64encode(credentials['password'].encode('ascii'))
        }

    # make log file dir
    logfile_path.parent.mkdir(parents=True, exist_ok=True)

    # make log file
    if not logfile_path.exists():
        with logfile_path.open('w', newline='') as f:
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
            'timestamp': datetime.datetime.now(),
            'connectivity': 1,
            'login_redirect': 0,
            'start_time': time.time(),
            'logged_in': 0,
        }

        # attempt to login
        try:
            # make request to any https site
            r_init = requests.get(site,
                                  verify=False,
                                  timeout=30)
            print(r_init.url)

            # already logged in?
            if expect_string in r_init.url:
                data['logged_in'] = 1

            # catch the redirect to login
            elif ':8080/mwg-internal' in r_init.url:
                data['login_redirect'] = 1

                # log in
                print('caught redirect, logging in...')
                r_login = requests.post(r_init.url,
                                        headers=credentials_header,
                                        verify=False,
                                        timeout=30)
                print(r_login.url)

                # resolve the url
                print('resolving url...')
                r_resolve = requests.get(r_login.url,
                                         verify=False,
                                         timeout=30)
                print(r_resolve.url)

                if expect_string in r_resolve.url:
                    data['logged_in'] = 1

            # log the time
            if data['logged_in']:
                print('logged in')
            else:
                print('failed to login')

        except requests.exceptions.ConnectionError:
            data['connectivity'] = 0
            print('network is down! (connection error)')

        except requests.exceptions.Timeout:
            data['connectivity'] = 0
            print('network is down! (timeout)')

        # log to csv (ascii only)
        with logfile_path.open('a', newline='') as f:
            c = csv.writer(f)
            c.writerow([
                data['timestamp'],
                data['connectivity'],
                data['login_redirect'],
                time.time() - data['start_time'],
                data['logged_in'],
            ])

        # sleep
        print('going to sleep, time is:', datetime.datetime.now())
        time.sleep(30)
        print()
        print('woke up at:', datetime.datetime.now())


if __name__ == '__main__':
    main()
