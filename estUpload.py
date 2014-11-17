#!/usr/bin/env python

__author__ = 'jneureuther'
__license__ = 'CC BY-SA 4.0'
__version__ = '1.0'
__est_version__ = 'Version 2.0.2360'

import filecmp
import requests
from bs4 import BeautifulSoup
import magic
from collections import OrderedDict


class ESTUpload:

    def __init__(self):
        self.s = requests.session()
        self.base_url = 'https://est.informatik.uni-erlangen.de'

    def __del__(self):
        self.s.close()

    def authenticate(self, user, passwd):
            params = {'login': user, 'password': passwd, 'submit': 'login'}
            est_error = self.parse_html_id(self.s.post(self.base_url + '/login.html?action=student',
                                                       params=params).text, 'estError')
            return True if est_error is None else est_error.next.strip()

    def search_file(self, name, lecture_id):
        est_file_id_tag = self.parse_html_text(self.s.get(self.base_url + '/encodingchecker.html?lectureId=' + lecture_id
                                                          + '&action=submit&tab=upload').text, name, "label")
        if est_file_id_tag is None:
            return 2
        else:
            return est_file_id_tag['for']

    def submit_file(self, name, path, lecture_id, submission_member_code):
        est_file_id = self.search_file(name, lecture_id)
        if est_file_id is 2:
            return 2

        my_magic = magic.open(magic.MAGIC_MIME_TYPE)
        my_magic.load()
        mime_type = my_magic.file(path)
        if mime_type == 'inode/x-empty':
            return 3

        file = [(est_file_id, (name, open(path, 'rb'), mime_type))]
        params = {'upload': 'upload', 'lectureId': lecture_id,
                  'submitterCode_' + est_file_id[:4]: submission_member_code, 'action': 'submit', 'tab': 'upload'}
        est_error = self.parse_html_id(self.s.post(self.base_url + '/encodingchecker.html', files=file, data=params)
                                       .text, 'estError')
        if est_error is None:
            return 1
        else:
            return est_error.next.strip()

    def check_file(self, name, path, lecture_id):
        file_url = self.base_url + '/' + self.parse_html_text(self.s.get(self.base_url + '/judging.html?lectureId=' +
                                                                         lecture_id + '&action=submit&tab=overview')
                                                              .text, name, "td").find_next("a").get('href')
        temp_file_path = "/tmp/" + name
        self.download_file(file_url, temp_file_path)
        if filecmp.cmp(path, temp_file_path, shallow=False):
            return 1
        else:
            return 0

    def check_status(self, name, lecture_id):
        name_tag = self.parse_html_text(self.s.get(self.base_url + '/judging.html?lectureId=' +
                                                   lecture_id + '&action=submit&tab=overview').text, name, "td")
        if name_tag is not None:
            return name_tag.find_previous("span").get('title')

    def download_file(self, url, path):
        # local_filename = url.split('/')[-1]
        r = self.s.get(url, stream=True)
        f = open(path, 'wb')
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        f.close()
        return

    def get_lecture_ids(self):
        ids = []
        for a in self.parse_html_id(self.s.get(self.base_url).text, 'estContent').find_all_next("a"):
            if 'index.html?lectureId' in a['href']:
                ids.append(a['href'].split('=')[1].split('&')[0])
                ids.append(a.next.strip())
        return list(OrderedDict.fromkeys(ids))

    def get_est_version(self):
        try:
            return self.parse_html_id(self.s.get(self.base_url).text, 'footermenu').find_next("li").text
        except requests.exceptions.ConnectionError:
            return '-1'

    def check_est_version(self):
        est_version = self.get_est_version()
        return True if __est_version__ in est_version else est_version

    def get_submission_with(self, group_submission_code, lecture_id):
        return self.parse_html_text(self.s.get(self.base_url + '/submissiongroupdynamic.html?lectureId=' + lecture_id +
                                               '&action=submit&tab=overview')
                                    .text, group_submission_code, "span").previous_element

    def parse_html_id(self, html, id):
        soup = BeautifulSoup(html)
        return soup.find(id=id)

    def parse_html_text(self, html, text, type):
        soup = BeautifulSoup(html)
        return soup.find(type, text=text)

    def parse_html_find_all(self, html, type):
        soup = BeautifulSoup(html)
        return soup.find_all(type)
