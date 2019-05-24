#!/usr/bin/env python3
"""Python-Pinboard

Python script for syncronizing Hacker News <http://news.ycombinator.com> saved
stories to Pinboard <http://pinboard.in/> via its API.

Originally written on Pythonista on iPad
"""

__version__ = "1.1"
__license__ = "BSD"
__copyright__ = "Copyright 2013-2014, Luciano Fiandesio"
__author__ = "Luciano Fiandesio <http://fiandes.io/>"

import sys
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as xml

HACKERNEWS = 'https://news.ycombinator.com'


def getSavedStories(session, hnuser):
    print("Getting saved stories...")
    savedStories = {}
    saved = session.get(HACKERNEWS + '/upvoted?id=' + hnuser)

    soup = BeautifulSoup(saved.content, "html.parser")

    for tag in soup.findAll('td', attrs={'class': 'title'}):
        if not isinstance(tag.a, type(None)):
            try:
                _href = tag.a['href']
                if not str.startswith(str(_href),
                                      '/x?fnid'):  # skip the 'More' link
                    _href = HACKERNEWS + _href if str.startswith(
                        str(_href), 'item?') else _href
                    savedStories[_href] = tag.a.text
            except:  # noqa: E722
                print("The saved story has no link, skipping")
    return savedStories


def loginToHackerNews(username, password):
    s = requests.Session()  # init a session (use cookies across requests)
    # we need to specify an header to get the right cookie
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0',  # noqa E501
        'Accept':
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    # Build the login POST data and make the login request.
    payload = {'whence': 'news', 'acct': username, 'pw': password}
    auth = s.post(HACKERNEWS + '/login', data=payload, headers=headers)
    if 'Bad login' in str(auth.content):
        raise Exception("Hacker News authentication failed!")
    if username not in str(auth.content):
        raise Exception("Hacker News didn't succeed, username not displayed.")

    return s  # return the http session


def postToPinboard(token, url, title):

    payload = {
        'auth_token': token,
        'url': url,
        'description': title,
        'tags': 'via:hackernews',
        'replace': 'no',
        'toread': 'yes'
    }
    r = requests.get('https://api.pinboard.in/v1/posts/add', params=payload)
    return 1 if isAdded(r.text) else 0


def isAdded(addresult):
    res = xml.fromstring(addresult)
    code = res.attrib["code"]
    return code == 'done'


def main():
    count = 0
    links = getSavedStories(loginToHackerNews(sys.argv[1], sys.argv[2]),
                            sys.argv[1])
    for key, value in links.items():
        count += postToPinboard(sys.argv[3], key, value)

    print("Added {} links to Pinboard".format(count))


if __name__ == "__main__":
    main()
