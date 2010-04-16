import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import parser
                            #local imports
import GeneralFuncs
#import FollowForm
from FollowForm import  *
from getHTML import *
from SearchParams import *
from HTMLparser import *
import string

import ArticleData
from ArticleData import Article

INTERNET = True

class MainPage(webapp.RequestHandler):
    def get(self):   
        
        self.response.out.write("""
          <html>
          <head><title>Research Assistant</title></head>
          <body>
          """)
                                #set up the html stuff
        self.response.out.write("""
        <form action="/search" method="post">
                <div><textarea name="SearchTerm" rows="1" cols="60"></textarea></div>
                <div><input type="submit" value="Search"></div>
                </form>
            </body></html>
        """)


    
class SearchResultsPage(webapp.RequestHandler):
    def post(self):
        
        self.response.out.write(""" 
            <html>
            <head><title>Search Results</title></head>
            <body>
        """)
                
        keyword = self.request.get('SearchTerm')
        search = SearchParams(keyword, "", "", "", "", "", 2, "", "", 2009, "", "1.", "on", "", "1", "", "")
        searchURL = search.constructURL()

        if (not INTERNET):
            article1 = ArticleData.Article()
            article2 = ArticleData.Article()
             
            results = {"key1": article1, "key2" : article2} 
        else:
            #results = GeneralFuncs.url2ArticleDict("http://scholar.google.co.il/scholar?q=stolowicz&hl=en&btnG=Search&as_sdt=2001&as_sdtp=on")
            results = GeneralFuncs.url2ArticleDict(searchURL)
#        
        for k,v in results.items():
            
           #generate articles html

            title = str(v.get_article_title())
            year = str(v.get_year())
            current_url = "<form action=\"/addFollow/" + title + "/" + year + "\" method=\"get\">"
            
            self.response.out.write(current_url)
            self.response.out.write("""<div name=""")
            self.response.out.write(k)
            self.response.out.write(""">""")
            
            self.response.out.write("""<a href=\"http://scholar.google.com""" + v.get_citations_url() +"\">")
            self.response.out.write("""<b>Title:</b>""" + title + "</a></div>""")
                        
            self.response.out.write("""<a href=\"http://scholar.google.com""" + v.get_citations_url() + "\"> Cite <br></a>")
            self.response.out.write("""<b>Year Published: </b>""" + year + "</a>""")
            
            self.response.out.write("""<div><br\><input style="background-color:lightgreen" type="submit" value="Add Follow on this Article"></div></form>""")
    
                               # footer html Stuff
        self.response.out.write("""
            </body>
            </html>
            """)

#class FollowFormDone():
    
    
    

#----------------------------    Classes end Here   ------------------------

application = webapp.WSGIApplication([('/', MainPage), 
                                      ('/search', SearchResultsPage)
                                      ,(r'/addFollow/(.*)/(.*)', FollowForm)
                                      ,('/FollowFormDone', FollowFormDone)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
