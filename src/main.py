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
from HTMLparser import getResultsFromURL, HTMLparser, getResultsFromURLwithProxy

from django.template import Context
from django.conf import settings 
from django.template.loader import get_template
from django import forms
from getHTML import getHTML

# Django settings configuration : currently for setting the templates directory
settings._target = None
ROOT_PATH = os.path.dirname(__file__)
settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,TEMPLATE_DIRS=[ROOT_PATH+'/templates'])

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
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users
#       show it to the world!!!
        self.response.out.write(t.render(c))
#global variable for search parameters        
searchParams = SearchParams()
numOfResults = 0

class Search(webapp.RequestHandler):
#Create the search results page
#TODO: 1.add next and previous buttons + page numbers in between
#      2.make sure user is signed in on 'addFollow' button
#      3.add citing: and relaTED: and allversions:
    def post(self):
        global searchParams
        global numOfResults
        
       
        if (self.request.arguments().count('SearchTerm')):
            keywords = self.request.get('SearchTerm')
            searchParams = SearchParams(keywords = keywords)
        else:
            ###Advanced search###
            
            keywords = self.request.get('all_of_the_words')
            exact_phrase = self.request.get('exact_phrase')
            one_of_the_words = self.request.get('one_of_the_words')
            without_the_words = self.request.get('without_the_words')
            occurence = self.request.get('occurence')
            author = self.request.get('author')
            journal = self.request.get('journal')
            year_start = self.request.get('year_start')
            year_finish = self.request.get('year_finish')
            searchParams = SearchParams(keywords = keywords, exact_phrase = exact_phrase, without_the_words=without_the_words,
                                   one_of_the_words = one_of_the_words, occurence=occurence, author=author, journal=journal,
                                   year_start=year_start, year_finish=year_finish  )
        
        searchURL = searchParams.constructURL()
        parserStruct = getResultsFromURLwithProxy(searchURL)
        numOfResults = parserStruct.get_numOfResults() 
        results = parserStruct.get_results()
        t = get_template('search.html')
        c = Context()
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users
        c['results'] = results
        c['formAction'] = '/AddFollow'
        c['keyword'] = keywords
        c['numOfResults'] =  """Displaying results """ + str(searchParams.start_from) + """ - """ + str(searchParams.start_from + searchParams.num_of_results) + " of " + str(numOfResults)
        self.response.out.write(t.render(c))
#get function for handling links on the search page(citedby, related articles, etc.)    
    def get(self):
        global searchParams
        t = get_template('search.html')
        c = Context()
        if self.request.get('Type')=='CitedBy':
            searchParams = SearchParams()
            searchParams.cites = self.request.get('Id')
            searchURL = searchParams.constructURL()
            c['CitedBy']='CitedBy'
            c['infoLine'] = """Articles Citing:<b><a href="/Search?Id="""+ self.request.get('AllVer') +"""&Type=AllVersions">"""+self.request.get('Title')+"</b></a>"+"<br><br><br>"
            c['numOfResults'] =  """Displaying results """ + str(searchParams.start_from) + """ - """ + str(searchParams.start_from + searchParams.num_of_results) + " of "
                    
        elif self.request.get('Type')=='RelatedArticles':
            searchParams = SearchParams()
            searchParams.relatedArticles = self.request.get('Id')
            searchURL = searchParams.constructURL()
            c['infoLine'] = """Articles Related To:<b><a href="/Search?Id="""+ self.request.get('AllVer') +"""&Type=AllVersions">"""+self.request.get('Title')+"<br><br><br>"
        
        elif self.request.get('Type')=='AllVersions':
            searchParams = SearchParams()
            searchParams.allVersions = self.request.get('Id')
            searchURL = searchParams.constructURL()
        
        elif self.request.get('Type')=='Import2BibTex':
            searchParams = SearchParams()
            searchParams.bibTex = self.request.get('Id')
            searchURL = searchParams.constructURL()
            bibTexHTML = getHTML(searchURL)
            bibTexHTML.getHTMLfromURL()
            self.response.out.write(bibTexHTML.get_html())
            return
        elif self.request.get('Type')=='Next':
            searchParams.updateStartFrom(searchParams.start_from+10)
            searchURL = searchParams.constructURL()
            c['numOfResults'] =  """Displaying results """ + str(searchParams.start_from) + """ - """ + str(searchParams.start_from + searchParams.num_of_results) + " of "
            
        elif self.request.get('Type')=='Back':
            searchParams.updateStartFrom(searchParams.start_from-10)
            searchURL = searchParams.constructURL()
            c['numOfResults'] =  """Displaying results """ + str(searchParams.start_from) + """ - """ + str(searchParams.start_from + searchParams.num_of_results) + " of "
        
        parserStruct = getResultsFromURLwithProxy(searchURL) 
        results = parserStruct.get_results()
        c['results'] = results
        c['numOfResults']+= str(parserStruct.get_numOfResults())
        c['formAction'] = '/AddFollow'
        c['keyword'] = searchParams.keywords
        self.response.out.write(t.render(c))
        
        
class DisplayTag(webapp.RequestHandler):
#Create the about us page    
    def get(self):
        t = get_template('displayTag.html')
        c = Context()
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users

        self.response.out.write(t.render(c)) 
        
        

class About(webapp.RequestHandler):
#Create the about us page    
    def get(self):
        t = get_template('About.html')
        c = Context()
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users

        self.response.out.write(t.render(c))

class Profile(webapp.RequestHandler):
#Create the about us page    
    def get(self):
        t = get_template('profile.html')
        c = Context()
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users

        self.response.out.write(t.render(c))


class AdvancedSearch(webapp.RequestHandler):
#Create the about us page    
    def get(self):
        t = get_template('advancedSearch.html')
        c = Context()
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users

        self.response.out.write(t.render(c))        
        
        
    
    

#----------------------------    Classes end Here   ------------------------

application = webapp.WSGIApplication([('/', MainPage)
                                      ,('/Search',Search )
                                      ,('/AddFollow', AddFollow)
                                      ,('/FollowFormDone', FollowFormDone)
                                      ,('/DisplayTag', DisplayTag)
                                      ,('/About', About)
                                      ,('/Profile', Profile)
                                      ,('/AdvancedSearch', AdvancedSearch)],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
