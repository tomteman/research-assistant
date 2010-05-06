#import cgi
#from google.appengine.ext.webapp import template
#from google.appengine.ext import db
#import GeneralFuncs
#from getHTML import *
#import string
#import ArticleData
#from ArticleData import Article
#from string import Template

import os


from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#local imports

from FollowForm import AddFollow
from FollowFormDone import FollowFormDone 
from SearchParams import *
from HTMLparser import getResultsFromURL

from django.template import Context
from django.conf import settings 
from django.template.loader import get_template

# Django settings configuration : currently for setting the templates directory
settings._target = None
ROOT_PATH = os.path.dirname(__file__)
settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,TEMPLATE_DIRS=[ROOT_PATH+'/templates'])

INTERNET = True

class MainPage(webapp.RequestHandler):
#create the main page for the application.
#TODOs: 
#       2. add sign in button.
    
    def get(self):
#       load the basic template 
        t = get_template('index.html')
#       add custom content
#TODO: Define default values/ required fields. 
        c = Context()
        c['login'] = users.create_login_url(self.request.uri)
        c['formAction'] = '/Search'
#       show it to the world!!!
        self.response.out.write(t.render(c))


    
class Search(webapp.RequestHandler):
#Create the search results page
#TODO: 1.add next and previous buttons + page numbers in between
#      2.make sure user is signed in on 'addFollow' button
    def post(self):
                     
        keyword = self.request.get('SearchTerm')
        search = SearchParams(keyword)
#        if self.request.get.has_key('back'):
#            search.start_from -= 10
#        if self.request.get.has_key('next'):
#            search.start_from += 10 
#        
        searchURL = search.constructURL()
        
        parserStruct = getResultsFromURL(searchURL) 
        results = parserStruct.get_results()
        t = get_template('search.html')
        c = Context()
        c['results'] = results
        c['formAction'] = '/AddFollow'
        c['keyword'] = keyword
        self.response.out.write(t.render(c))


class About(webapp.RequestHandler):
#Create the about us page    
    def get(self):
        t = get_template('About.html')
        c = Context()
        self.response.out.write(t.render(c))
    
    

#----------------------------    Classes end Here   ------------------------

application = webapp.WSGIApplication([('/', MainPage)
                                      ,('/Search', Search)
                                      ,('/AddFollow', AddFollow)
                                      ,('/FollowFormDone', FollowFormDone)
                                      ,('/About',About)],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
