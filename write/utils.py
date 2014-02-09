# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

def tidy_html(text):
    soup = BeautifulSoup(text)
    return soup.prettify()

class TidyMiddleware(object):
    # cf http://pyevolve.sourceforge.net/wordpress/?p=814
    def process_response(self, request, response):
        if response.status_code == 200:
            if response["content-type"].startswith("text/html"):
                response.content = tidy_html(response.content)
        return response
