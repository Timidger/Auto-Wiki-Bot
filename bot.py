#!/usr/bin/env python3
from __future__ import print_function

import time
import re
import praw
from wikia import wikia

URL_SEARCH_STRING = ("(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))"
                     "([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?")
MIDDLE_OF_URL = ".wikia.com/wiki/"


def get_creds():
    with open("creds.txt", "r") as cred_file:
        return (cred_file.readline().strip(), cred_file.readline().strip())


def replied_yet(comment, user):
    """Checks to see if the user has replied yet to the comment"""
    for reply in comment.replies:
        if str(reply.author) == str(user.user):
            return True
    return False


def find_wikia_and_title(url):
    """Searchs a url for the string that denote the wikia and title for the
    linked article"""
    middle = url.find(MIDDLE_OF_URL)
    if middle < 0:
        return (None, None)
    # Find the sub-wikia part of the url
    start = url.find("//") + 2
    sub_wikia = url[start:middle]
    # Find the title part of the url
    post_middle = middle + len(MIDDLE_OF_URL)
    title = url[post_middle:]
    return sub_wikia, title


def find_url(comment):
    """Finds a wikia url in the comment. If one can't be found, an empty string
    is returned instead"""
    url = re.search(URL_SEARCH_STRING, comment)
    if not url:
        return ""
    url = url.group()
    if "wikia" not in url:
        return ""
    return url


def get_summary(sub_wikia, title):
    page = wikia.page(sub_wikia, title)
    return page.section(page.sections[0])

if __name__ == "__main__":
    username, password = get_creds()
    USER = praw.Reddit("posts summaries for wikia links, by /u/iprefervim")
    USER.login(username, password)
    print("Logged in")
    while True:
        try:
            for comment in praw.helpers.comment_stream(USER, "all", limit=None,
                                                       verbosity=0):
                url = find_url(comment.body)
                # Ignore if /u/autowikiabot post
                if comment.author == USER.user:
                    continue
                # Can't find url? Ignore it
                if not url:
                    continue
                sub_wikia, title = find_wikia_and_title(url)
                if not (sub_wikia and title):
                    continue
                summary = get_summary(sub_wikia, title)
                print("BODY: ", comment.body)
                #print("SUMMARY: ", summary)
                #print()
                print()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
