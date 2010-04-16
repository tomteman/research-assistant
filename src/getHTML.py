import urllib2
import hashlib
import random

class getHTML:
    def __init__(self, url):
        self.url = url
        self.html = ""

    def get_url(self):
        return self.url


    def get_html(self):
        return self.html


    def set_url(self, value):
        self.__url = value


    def set_html(self, value):
        self.html = value

    def del_url(self):
        del self.url


    def del_html(self):
        del self.html


    def getHTMLfromURL(self):
        google_id = hashlib.md5(str(random.random())).hexdigest()[:16]
        HEADERS = {'User-Agent' : 'Mozilla/5.0', 'Cookie' : 'GSP=ID=%s:CF=4' % google_id }
        request = urllib2.Request(self.url, headers=HEADERS)
        response = urllib2.urlopen(request)
        html = response.read()
        html.decode('ascii', 'ignore')
        self.html = html

