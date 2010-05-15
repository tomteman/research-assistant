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
        HEADERS = {'User-Agent' : 'Firefox/3.6.3', 'Cookie' : 'GSP=ID=%s:CF=4' % google_id }
        request = urllib2.Request(self.url, headers=HEADERS)
        response = urllib2.urlopen(request)
        html = response.read()
        html.decode('ascii', 'ignore')
        self.html = html
        
    def getHTMLfromURLwithProxy(self, host, port):
        google_id = hashlib.md5(str(random.random())).hexdigest()[:16]
        HEADERS = {'User-Agent' : 'Firefox/3.6.3', 'Cookie' : 'GSP=ID=%s:CF=4' % google_id }
        proxy_info = {
            'host' : host,
            'port' : port
            }
        proxy_support = urllib2.ProxyHandler({"http" : \
                                              "http://%(host)s:%(port)d" % proxy_info})
        opener = urllib2.build_opener(proxy_support)

        # install it
        urllib2.install_opener(opener)

        # use it
        request = urllib2.Request(self.url, headers=HEADERS)
        response = urllib2.urlopen(request)
        html = response.read()
        html.decode('ascii', 'ignore')
        self.html = html
        
