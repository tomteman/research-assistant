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
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#local imports
from ShowPendings import ShowPendings
import LabelHandlers
from LabelHandlers import *
import JSONConvertors
from FollowForm import AddFollow
from FollowFormDone import FollowFormDone
from FollowFormDone import Submit
from FollowFormDone import FirstUpload 
from SearchParams import *
from HTMLparser import getResultsFromURL, HTMLparser, getResultsFromURLwithProxy, getResultsFromURL_OFFLINE
from django.template import Context
from django.conf import settings 
from django.template.loader import get_template
from django import forms
from getHTML import getHTML
from MyFollows import MyFollows
import GlobalVariables
from django.utils import simplejson
from urllib2 import quote

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

def mockResults(results):
        
   # str = """{"noResultsFlag": false, "didYouMeanFlag": false, "url": "http://scholar.google.com/scholar?as_yhi=&as_subj=&btnG=Search+Scholar&as_sauthors=&as_sdt=1.&as_publication=&as_vis=0&as_eq=&as_epq=&start=0&as_oq=&num=10&hl=en&as_occt=any&as_q=%22The+Languages+of+Art%3A+How+Representational+and+Abstract+Painters+Conceptualize+Their+Work+in+Terms+of+Language%22&as_ylo=&as_sdtp=on", "results": [{"HTML_urlList": [{"articleTitle": "<b>The Languages of Art</b>: <b>How Representational and Abstract Painters Conceptualize Their Work in Terms of Language</b>", "articleURL": "http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1552577", "hasLink": true}, {"articleTitle": "TAU full text", "articleURL": "http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=A&amp;aulast=Comment&amp;atitle=The+Languages+of+Art:+How+Representational+and+Abstract+Painters+Conceptualize+Their+Work+in+Terms+of+Language&amp;title=Poetics+Today&amp;volume=30&amp;issue=3&amp;date=2009&amp;spage=517&amp;issn=0333-5372", "hasLink": true}], "BibTex_dict": {}, "related_articlesID": "", "HTML_author_year_pub": "A Comment - Poetics Today, 2009 - papers.ssrn.com", "cacheID": "", "related_articlesURL": "", "all_versionsURL": "", "HTML_abstract": "%3Cbr%3EAbstract%3A%20Representational%20and%20nonrepresentational%20%28abstract%29%20artists%20exhibit%20different%20conceptual%20%3Cbr%3E%0Aprocesses%20when%20they%20describe%20their%20work.%20Data%20from%20ekphrastic%20texts%20written%20by%20artists%20to%20accompany%20%3Cbr%3E%0Atheir%20artwork%20show%20that%2C%20although%20both%20kinds%20of%20painters%20refer%20metaphorically%20to%20their%20art%20%3Cb%3E%20...%3C%2Fb%3E%20%3Cbr%3E", "all_versionsID": "", "BibTexURL": "http://scholar.google.com/scholar.bib?q=info:cV_9r3F4PGUJ:scholar.google.com/&output=citation&hl=en&as_sdt=2000&ct=citation&cd=0", "articleTitleQuoted": "%3Cb%3EThe+Languages+of+Art%3C%2Fb%3E%3A+%3Cb%3EHow+Representational+and+Abstract+Painters+Conceptualize+Their+Work+in+Terms+of+Language%3C%2Fb%3E", "key": "cV_9r3F4PGUJ", "citationsURL": "", "articleTitle": "<b>The Languages of Art</b>: <b>How Representational and Abstract Painters Conceptualize Their Work in Terms of Language</b>", "citationsID": "", "articleURL": "http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1552577", "cacheURL": "", "citationsNUM": ""}, {"HTML_urlList": [{"articleTitle": "<b>The Languages of Art</b>: <b>How Representational and Abstract Painters Conceptualize Their Work in Terms of Language</b>", "articleURL": "http://poeticstoday.dukejournals.org/cgi/content/abstract/30/3/517", "hasLink": true}, {"articleTitle": "TAU full text", "articleURL": "http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=K&amp;aulast=Sullivan&amp;atitle=The+Languages+of+Art:+How+Representational+and+Abstract+Painters+Conceptualize+Their+Work+in+Terms+of+Language&amp;id=doi:10.1215/03335372-2009-004&amp;title=Poetics+Today&amp;volume=30&amp;issue=3&amp;date=2009&amp;spage=517&amp;issn=0333-5372", "hasLink": true}], "BibTex_dict": {}, "related_articlesID": "lar?q=related:pcEFGD5UVYIJ:scholar.google.com/&amp;hl=en&amp;as_sdt=200", "HTML_author_year_pub": "K Sullivan - Poetics Today, 2009 - Duke Univ Press", "cacheID": "", "related_articlesURL": "http://scholar.google.com/scholar?q=related:lar?q=related:pcEFGD5UVYIJ:scholar.google.com/&amp;hl=en&amp;as_sdt=200:scholar.google.com/&hl=en&num=10&as_sdt=2000", "all_versionsURL": "http://scholar.google.com/scholar?cluster=9391505223618773413&hl=en&num=10&as_sdt=2000", "HTML_abstract": "%3Cbr%3EAbstract%20Representational%20and%20nonrepresentational%20%28abstract%29%20artists%20exhibit%20differ-%20ent%20conceptual%20%3Cbr%3E%0Aprocesses%20when%20they%20describe%20their%20work.%20Data%20from%20ekphrastic%20texts%20written%20by%20artists%20to%20accompany%20%3Cbr%3E%0Atheir%20artwork%20show%20that%2C%20although%20both%20kinds%20of%20painters%20refer%20metaphorically%20to%20their%20art%20%3Cb%3E%20...%3C%2Fb%3E%20%3Cbr%3E", "all_versionsID": "9391505223618773413", "BibTexURL": "http://scholar.google.com/scholar.bib?q=info:pcEFGD5UVYIJ:scholar.google.com/&output=citation&hl=en&as_sdt=2000&ct=citation&cd=0", "articleTitleQuoted": "%3Cb%3EThe+Languages+of+Art%3C%2Fb%3E%3A+%3Cb%3EHow+Representational+and+Abstract+Painters+Conceptualize+Their+Work+in+Terms+of+Language%3C%2Fb%3E", "key": "pcEFGD5UVYIJ", "citationsURL": "", "articleTitle": "<b>The Languages of Art</b>: <b>How Representational and Abstract Painters Conceptualize Their Work in Terms of Language</b>", "citationsID": "", "articleURL": "http://poeticstoday.dukejournals.org/cgi/content/abstract/30/3/517", "cacheURL": "", "citationsNUM": ""}], "didYouMeanHTML": "", "didYouMeanKeywords": "", "didYouMeanURL": "", "refinedSearchNoResultsFlag": false, "numOfResults": "2"}"""
    my_html_parser_encoder = JSONConvertors.HTMLparserEncoder()
    str = my_html_parser_encoder.encode(results) 
    
    return str

class Search(webapp.RequestHandler):
#Create the search results page
#TODO: 1.add next and previous buttons + page numbers in between
#      2.make sure user is signed in on 'addFollow' button
#      3.add citing: and relaTED: and allversions:
    
    
    def post(self):
#        GlobalVariables.GLOBAL_searchParams
#        GlobalVariables.GLOBAL_numOfResults

        if self.request.get('Type') == "Refine":
            GlobalVariables.GLOBAL_searchParams.author = self.request.get('author')
            GlobalVariables.GLOBAL_searchParams.keywords = quote(self.request.get('keywords'))
            keywords = GlobalVariables.GLOBAL_searchParams.keywords

        
        elif (self.request.arguments().count('SearchTerm')):
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
        #parserStruct = getResultsFromURL_OFFLINE(searchURL)
        parserStruct = getResultsFromURLwithProxy(searchURL)
        
        GLOBAL_numOfResults = parserStruct.get_numOfResults() 
        results = parserStruct.get_results()
        if parserStruct.isRefinedSearchNoResultsFlag():
            t = get_template('noResults.html')
            c = Context()
            c['refined_search_no_results'] = True
            c['text'] = "Sorry, we couldn't find any results that match Your search"
            self.response.out.write(t.render(c))
            return
        if parserStruct.isNoResultsFlag():
            t = get_template('noResults.html')
            c = Context()
            c['noResultsKeywords'] = parserStruct.didYouMeanKeywords
            c['noResultsHTML'] = parserStruct.didYouMeanHTML
            self.response.out.write(t.render(c))
            return
        else:
            t = get_template('search.html')
            c = Context()
            if (users.get_current_user()):
                c['logout'] = users.create_logout_url(self.request.uri)
            else:
                c['login'] = users.create_login_url(self.request.uri)
        numResultsDec =int(str(parserStruct.get_numOfResults()).replace(",","")  )
        numResults = parserStruct.get_numOfResults()
        if ((numResultsDec - (GlobalVariables.GLOBAL_searchParams).start_from)< (GlobalVariables.GLOBAL_searchParams).num_of_results):
            c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str(numResults) + " of " + str(numResults)
        else:
            c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str((GlobalVariables.GLOBAL_searchParams).start_from + (GlobalVariables.GLOBAL_searchParams).num_of_results) + " of " + str(numResults)
        
        c['users'] = users
        c['resultsJSON'] = mockResults(parserStruct)
        c['results'] = results
        c['formAction'] = '/AddFollow'
        c['keyword'] = keywords
        #c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str((GlobalVariables.GLOBAL_searchParams).start_from + (GlobalVariables.GLOBAL_searchParams).num_of_results) + " of " + str(GLOBAL_numOfResults)
        if parserStruct.didYouMeanFlag:
            c['didYouMean'] = """Did You Mean: <a href = /Search?Id=""" + parserStruct.didYouMeanKeywords + """&Type=DidYouMean>""" + parserStruct.didYouMeanHTML + """</a>"""
        self.response.out.write(t.render(c))        
#get function for handling links on the search page(citedby, related articles, etc.)    
    def get(self):
#        GlobalVariables.GLOBAL_searchParams
#        GlobalVariables.GLOBAL_numOfResults
        t = get_template('search.html')
        c = Context()
        

        if self.request.get('Type')=='DidYouMean':
            searchParams = SearchParams(keywords = self.request.get('Id'))
            searchURL = searchParams.constructURL()

        elif self.request.get('Type')=='FollowResults':
            (GlobalVariables.GLOBAL_searchParams).updateStartFrom(0)
            searchURL = (GlobalVariables.GLOBAL_searchParams).constructURL()
            
        elif self.request.get('Type')=='CitedBy':

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
        
        #parserStruct = getResultsFromURL_OFFLINE(searchURL) 
        parserStruct = getResultsFromURLwithProxy(searchURL) 
        results = parserStruct.get_results()
        
        numResults = parserStruct.get_numOfResults()
        #numResultsDec =int(removeComma(parserStruct.get_numOfResults()))
        numResultsDec =int(str(parserStruct.get_numOfResults()).replace(",","")  )
            
        if ((numResultsDec - (GlobalVariables.GLOBAL_searchParams).start_from)< (GlobalVariables.GLOBAL_searchParams).num_of_results):
            c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str(numResults) + " of "
        else:
            c['numOfResults'] =  """Displaying results """ + str((GlobalVariables.GLOBAL_searchParams).start_from) + """ - """ + str((GlobalVariables.GLOBAL_searchParams).start_from + (GlobalVariables.GLOBAL_searchParams).num_of_results) + " of "
        if parserStruct.didYouMeanFlag:
            c['didYouMean'] = """Did You Mean: <a href = /Search?Id=""" + parserStruct.didYouMeanKeywords + """&Type=DidYouMean>""" + parserStruct.didYouMeanHTML + """</a>"""
            
        c['users'] = users
        c['results'] = results
        c['resultsJSON'] = mockResults(parserStruct)      
        c['numOfResults']+= str(numResults)
        c['formAction'] = '/AddFollow'
        c['keyword'] = (GlobalVariables.GLOBAL_searchParams).keywords
        self.response.out.write(t.render(c))
        
        
class DisplayTag(webapp.RequestHandler):
    @login_required  
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



class getCurrentUser(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.out.write(user.email())





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
                                      ,('/AdvancedSearch', AdvancedSearch)
                                      ,('/UpdateLabelDB', UpdateLabelDB)
                                      ,('/UpdateArticleLabelDB',UpdateArticleLabelDB)
                                      ,('/RemoveLabelDB',RemoveLabelDB)
                                      ,('/ShowArticlesByLabel',ShowArticlesByLabel)
                                      ,('/ShowPendings', ShowPendings)
                                      ,('/RenameLabelDB',RenameLabelDB)
                                      ,('/getCurrentUser',getCurrentUser)
                                      ,('/ShareLabel',ShareLabel)
                                      ,('/GetAllLabels',GetAllLabels)
                                      ,('/SearchInLabel',SearchInLabel)
                                      ,('/GetSharedLabelUsers',GetSharedLabelUsers)
                                      ,('/DuplicateSharedLabelToPrivate',DuplicateSharedLabelToPrivate)
                                      ,('/RemoveFromSharedLabelDB',RemoveFromSharedLabelDB)],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
