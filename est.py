#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'jneureuther'
__license__ = 'CC BY-SA 4.0'
__version__ = '1.0'

import sys
import threading
import time
import estUpload
import argparse
import getpass
from colorama import Fore, Style


class Spinner(threading.Thread):
    chars = ["\\", "|", "/", "-"]
    index = 0
    keeprunning = True

    def __init__(self, text):
        super(Spinner, self).__init__()
        self.text = text

    def run(self):
        while self.keeprunning:
            self.printing('[i] ' + self.chars[self.index % len(self.chars)] + ' ' + self.text)
            time.sleep(0.1)
            self.index += 1

    @staticmethod
    def printing(data):
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

    def stop(self):
        self.printing('[i] ✓ ' + self.text)
        self.keeprunning = False


est = estUpload.ESTUpload()
parser = argparse.ArgumentParser(description='Console Interface to Exercise Submission Tool')
subparsers = parser.add_subparsers()

login_parser = subparsers.add_parser('login', help='login on est')
login_parser.add_argument('-u', '--user', action='store', dest='user', help='username to login')
login_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
login_parser.add_argument('-V', '--verbose', action='store_true', dest='verbose',
                          default=False, help='show debugging information')

search_parser = subparsers.add_parser('search', help='search a file on est')
search_parser.add_argument('file', action='store', type=str, help='path to file to search')
search_parser.add_argument('-u', '--user', action='store', dest='user', help='username to login')
search_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
search_parser.add_argument('-V', '--verbose', action='store_true', dest='verbose',
                           default=False, help='show debugging information')

submit_parser = subparsers.add_parser('submit', help='submit a file on est')
submit_parser.add_argument('file', action='store', type=str, help='path to file to search')
submit_parser.add_argument('-u', '--user', action='store', dest='user', help='username to login')
submit_parser.add_argument('-g', '--group-submission-code', action='store', dest='group_submission_code',
                           default=0, help='submit with group_submission_code')
submit_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
submit_parser.add_argument('-V', '--verbose', action='store_true', dest='verbose',
                           default=False, help='show debugging information')

status_parser = subparsers.add_parser('status', help='check the status of a given file')
status_parser.add_argument('file', action='store', type=str, help='path to file to search')
status_parser.add_argument('-u', '--user', action='store', dest='user', help='username to login')
status_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
status_parser.add_argument('-s', action='store', dest='status', default=0)
status_parser.add_argument('-V', '--verbose', action='store_true', dest='verbose',
                           default=False, help='show debugging information')

results = parser.parse_args()

print(Fore.YELLOW +
      'Console Interface to Exercise Submission Tool | Rev' + __version__)
check_est_version = est.check_est_version()
if check_est_version is True:
    print('Current EST version is supported.' + Fore.RESET)
elif check_est_version in '-1':
    print(Fore.RESET + Fore.RED + Style.BRIGHT + '[FAIL] ' + Style.RESET_ALL + Fore.RESET + 'Cannot access est. Please check your internet connection!')
    sys.exit(1)
else:
    print(Fore.RESET + Fore.RED + 'Current EST version ('
          + check_est_version.split(' ')[-1] + ') is NOT supported!' + Fore.RESET)
    sys.exit(1)

if results.user is not None:
    retV = est.authenticate(results.user, getpass.getpass())
    if retV is True:
        print('[i] Successfully signed in with user ' + results.user + '!')
    else:
        print(Fore.RED + Style.BRIGHT + '[FAIL] ' + Style.RESET_ALL + Fore.RESET + retV)
        sys.exit(1)
else:
    user = raw_input('User: ')
    passwd = getpass.getpass()
    retV = est.authenticate(user, passwd)
    if retV is True:
        print('[i] Successfully signed in with user ' + user + '!')
    else:
        print(Fore.RED + Style.BRIGHT + '[FAIL] ' + Style.RESET_ALL + Fore.RESET + retV)
        sys.exit(1)

lecture_ids = est.get_lecture_ids()

if hasattr(results, 'file') and not hasattr(results, 'group_submission_code') and not hasattr(results, 'status'):
    for index, id in enumerate(lecture_ids):
        if id.isdigit():
            retV = est.search_file(results.file.split('/')[-1], id)
            if retV == 2:
                print(Fore.RED + Style.BRIGHT + '[FAIL] ' + Style.RESET_ALL + Fore.RESET +
                      'File ' + results.file.split('/')[-1] + ' not found on est!')
                sys.exit(1)
            else:
                print('[i] File found in lecture ' + lecture_ids[index + 1] + ', file id: ' + retV + '.')
                sys.exit(0)

if hasattr(results, 'group_submission_code'):
    for index, id in enumerate(lecture_ids):
        if id.isdigit():
            if est.search_file(results.file.split('/')[-1], id) is not 2:
                spinner = Spinner('Uploading..')
                spinner.start()
                retV = est.submit_file(results.file.split('/')[-1], results.file, id, results.group_submission_code)
                spinner.stop()
                if retV == 1:
                    print('')
                    print('[i] Successfully uploaded ' + results.file.split('/')[-1] + ' to ' + lecture_ids[index + 1])
                    if results.group_submission_code is not 0:
                        print('[i] Submission together with: '
                              + est.get_submission_with(results.group_submission_code, id).split('(')[0].strip())
                elif retV == 2:
                    print('')
                    print(Fore.RED + Style.BRIGHT + '[FAIL] ' + Style.RESET_ALL + Fore.RESET +
                          'File ' + results.file.split('/')[-1] + ' not found on est in lectures!')
                    sys.exit(1)
                elif retV == 3:
                    print('')
                    print(Fore.RED + Style.BRIGHT + '[FAIL] ' + Style.RESET_ALL + Fore.RESET +
                          'File is empty!')
                    sys.exit(1)
                else:
                    print('')
                    print('[i] ' + retV)
                spinner2 = Spinner('Waiting for test result..')
                spinner2.start()
                status = est.check_status(results.file.split('/')[-1], id)
                while status == 'Waiting for test result':
                    time.sleep(5)
                    status = est.check_status(results.file.split('/')[-1], id)
                spinner2.stop()
                if "Submitted files don't compile" in status:
                    print('')
                    print(Fore.RED + Style.BRIGHT + '[✗] ' + Style.RESET_ALL + Fore.RESET + status + '.')
                elif "Error in given test case" in status:
                    print('')
                    print(Fore.YELLOW + Style.BRIGHT + '[!] ' + Style.RESET_ALL + Fore.RESET + status + '.')
                elif "All files submitted" in status or "Test is OK for given test case" in status:
                    print('')
                    print(Fore.GREEN + Style.BRIGHT + '[✓] ' + Style.RESET_ALL + Fore.RESET + status + '.')
                else:
                    print('')
                    print('[i] ' + status + '.')
                sys.exit(0)
    print(Fore.RED + Style.BRIGHT + '[FAIL] ' + Style.RESET_ALL + Fore.RESET +
          'File ' + results.file.split('/')[-1] + ' not found on est!')
    sys.exit(1)

if hasattr(results, 'status'):
    for id in lecture_ids:
        if id.isdigit():
            status = est.check_status(results.file.split('/')[-1], id)
            if status is not None:
                print('[i] Status for file ' + results.file.split('/')[-1] + ': ' + status + '.')
