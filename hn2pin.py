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
import logging
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as xml
from user_agent import generate_user_agent

HACKERNEWS = 'https://news.ycombinator.com'

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)


def getSavedStories(session, hnuser):
    logging.info("Getting upvoted stories from news.ycombinator.com")
    upvotedStories = {}
    upvoted = session.get(HACKERNEWS + '/upvoted?id=' + hnuser)

    soup = BeautifulSoup(upvoted.content, "html.parser")

    for tag in soup.findAll('td', attrs={'class': 'title'}):
        if not isinstance(tag.a, type(None)):
            try:
                _href = tag.a['href']
                # skip the 'More' link
                if not str.startswith(str(_href), '/x?fnid'):
                    _href = HACKERNEWS + _href if str.startswith(
                        str(_href), 'item?') else _href
                    upvotedStories[_href] = tag.a.text
            except:  # noqa: E722
                logging.warning("The saved story has no link, skipping")
    return upvotedStories


def loginToHackerNews(username, password):
    s = requests.Session()  # init a session (use cookies across requests)
    accept_header = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"  # noqa E501
    # we need to specify an header to get the right cookie
    headers = {
        'User-Agent': generate_user_agent(),
        'Accept': accept_header,
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

    if isAdded(r.text):
        logging.info("Posting to pinboard.in: {}: {}".format(title, url))

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

    logging.info("Added {} links to Pinboard".format(count))


if __name__ == "__main__":
    main()
