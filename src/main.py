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
import re


from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#local imports

from FollowForm import AddFollow
from FollowFormDone import FollowFormDone
from FollowFormDone import Submit
from FollowFormDone import FirstUpload 
from SearchParams import *
from HTMLparser import getResultsFromURL, HTMLparser, getResultsFromURLwithProxy

from django.template import Context
from django.conf import settings 
from django.template.loader import get_template
from django import forms
from getHTML import getHTML
from MyFollows import MyFollows
import GlobalVariables
from django.utils import simplejson

# Django settings configuration : currently for setting the templates directory
settings._target = None
ROOT_PATH = os.path.dirname(__file__)
settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,TEMPLATE_DIRS=[ROOT_PATH+'/templates'])

def removeComma(str):
    p = re.compile(r',')
    return p.sub('',str)

class MainPage(webapp.RequestHandler):
#create the main page for the application.
#TODOs: 
#       2. add sign in button.
    
    def get(self):
#       load the basic template 
        t = get_template('base.html')
#       add custom content
#TODO: Define default values/ required fields. 
        c = Context()
        
        page=self.request.get('page')
        if (page != ""):
            page = "/" + page;
        else:
            page = "/Index"   
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users
        c['currPage'] = page
#       show it to the world!!!
        self.response.out.write(t.render(c))
        
        



class Index(webapp.RequestHandler):
    def get(self):
        t = get_template('index.html')
        c = Context()
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users
#       show it to the world!!!
        self.response.out.write(t.render(c))




class Search(webapp.RequestHandler):
#Create the search results page
#TODO: 1.add next and previous buttons + page numbers in between
#      2.make sure user is signed in on 'addFollow' button
#      3.add citing: and relaTED: and allversions:
    def post(self):
#        GlobalVariables.GLOBAL_searchParams
#        GlobalVariables.GLOBAL_numOfResults
        if (self.request.arguments().count('SearchTerm')):
            keywords = self.request.get('SearchTerm')
            GlobalVariables.GLOBAL_searchParams = SearchParams(keywords = keywords)
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
            GlobalVariables.GLOBAL_searchParams = SearchParams(keywords = keywords, exact_phrase = exact_phrase, without_the_words=without_the_words,
                                   one_of_the_words = one_of_the_words, occurence=occurence, author=author, journal=journal,
                                   year_start=year_start, year_finish=year_finish  )
        
        searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
        parserStruct = getResultsFromURLwithProxy(searchURL)
        GLOBAL_numOfResults = parserStruct.get_numOfResults() 
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
        c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str((GlobalVariables.GLOBAL_searchParams).start_from + (GlobalVariables.GLOBAL_searchParams).num_of_results) + " of " + str(GLOBAL_numOfResults)
        self.response.out.write(t.render(c))        
#get function for handling links on the search page(citedby, related articles, etc.)    
    def get(self):
#        GlobalVariables.GLOBAL_searchParams
#        GlobalVariables.GLOBAL_numOfResults
        t = get_template('search.html')
        c = Context()
        
        if self.request.get('Type')=='FollowResults':
            (GlobalVariables.GLOBAL_searchParams).updateStartFrom(0)
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            
        if self.request.get('Type')=='CitedBy':
            GlobalVariables.GLOBAL_searchParams = SearchParams()
            (GlobalVariables.GLOBAL_searchParams).citationsID = self.request.get('Id')
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            c['CitedBy']='CitedBy'
            c['infoLine'] = """Articles Citing:<b><a href="/Search?Id="""+ self.request.get('AllVer') +"""&Type=AllVersions">"""+self.request.get('Title')+"</b></a>"+"<br><br><br>"
                    
        elif self.request.get('Type')=='RelatedArticles':
            GlobalVariables.GLOBAL_searchParams = SearchParams()
            (GlobalVariables.GLOBAL_searchParams).relatedArticles = self.request.get('Id')
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            c['infoLine'] = """Articles Related To : <b><a href="/Search?Id="""+ self.request.get('AllVer') +"""&Type=AllVersions">"""+self.request.get('Title')+"</b></a>"+"<br><br><br>"
        
        elif self.request.get('Type')=='AllVersions':
            GlobalVariables.GLOBAL_searchParams = SearchParams()
            (GlobalVariables.GLOBAL_searchParams).allVersions = self.request.get('Id')
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            c['infoLine'] = """All Versions Of : <b><a href="/Search?Id="""+ self.request.get('Id') +"""&Type=AllVersions">"""+self.request.get('Title')+"</b></a>"+"<br><br><br>"
        
        elif self.request.get('Type')=='Import2BibTex':
            GlobalVariables.GLOBAL_searchParams = SearchParams()
            (GlobalVariables.GLOBAL_searchParams.bibTex) = self.request.get('Id')
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            bibTexHTML = getHTML(searchURL)
            bibTexHTML.getHTMLfromURL()
            self.response.out.write(bibTexHTML.get_html())
            return
        
        elif self.request.get('Type')=='Next':
            (GlobalVariables.GLOBAL_searchParams).updateStartFrom((GlobalVariables.GLOBAL_searchParams).start_from+10)
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            
        elif self.request.get('Type')=='Back':
            (GlobalVariables.GLOBAL_searchParams).updateStartFrom((GlobalVariables.GLOBAL_searchParams).start_from-10)
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            
        
        else:
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
             
        parserStruct = getResultsFromURLwithProxy(searchURL) 
        results = parserStruct.get_results()
        numResults = parserStruct.get_numOfResults()
        numResultsDec =int(removeComma(parserStruct.get_numOfResults()))
        
        if ((numResultsDec - (GlobalVariables.GLOBAL_searchParams).start_from)< (GlobalVariables.GLOBAL_searchParams).num_of_results):
            c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str(numResults) + " of "
        else:
            c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str((GlobalVariables.GLOBAL_searchParams).start_from + (GlobalVariables.GLOBAL_searchParams).num_of_results) + " of "
        c['users'] = users
        c['results'] = results      
        c['numOfResults']+= str(numResults)
        c['formAction'] = '/AddFollow'
        c['keyword'] = (GlobalVariables.GLOBAL_searchParams).keywords
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
                                      ,('/Index', Index)
                                      ,('/Search',Search )
                                      ,('/AddFollow', AddFollow)
                                      ,('/FollowFormDone', FollowFormDone)
                                      ,('/DisplayTag', DisplayTag)
                                      ,('/About', About)
                                      ,('/Submit', Submit)
                                      ,('/FirstUpload', FirstUpload)
                                      ,('/MyFollows', MyFollows)
                                      ,('/AdvancedSearch', AdvancedSearch)],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
