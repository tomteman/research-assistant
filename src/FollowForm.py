import os
import types
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from django.template import Template,Context
from django.conf import settings 
from django.template.loader import get_template
from ArticleData import ArticleData, parseBibTexItems
         
       
class AddFollow(webapp.RequestHandler):
    def post(self):
       
        bibTexKey = self.request.get('bibTexKey')
        title = self.request.get('Title')
        author_year_pub = self.request.get("AuthorYearPub")
        
        unvalid_bibtex = 0
        try:
            bibTex = parseBibTexItems(bibTexKey)
            bibTexData = bibTex.values()[0]
        except Exception:
            unvalid_bibtex = 1
        
        author_year_pub = get_author_year_pub_from_HTML(author_year_pub)
        
        if ((not unvalid_bibtex) and bibTexData.has_key('author')):
            try:
                authors = bibTexData['author']
            except Exception: 
                authors = author_year_pub[0]     
        else:
            authors = author_year_pub[0] if author_year_pub[0] else ""
      
        
        if ((not unvalid_bibtex) and bibTexData.has_key('journal')):
            try:
                journal = bibTexData['journal']
            except Exception: 
                journal = author_year_pub[1]     
        else:
            journal = author_year_pub[1] if author_year_pub[1] else ""    
                
      
            
        keywords = self.request.get('SearchTerm')
        numCitations = self.request.get('CitesID')
        t = get_template('addFollow.html')
        c = Context()
        c['Title'] = 'Research-assistant about project'
        c['formDoneAction'] = '/FollowFormDone'
        c['followName'] = "Name Your Follow"
        c['articleName'] = title
        c['many_authors'] = isinstance(authors, types.ListType )
        c['authors'] = authors
        c['articleJournal'] = journal
        c['keywords'] = keywords
        c['numCitations'] = numCitations
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users
        
        self.response.out.write(t.render(c))   
        
        
   
def get_author_year_pub_from_HTML(author_year_pub):
        author_year_pub = author_year_pub.split('-')
        authors = author_year_pub[0]
        authors_lst = authors.split(",")
        for author in authors_lst:
            if (author.find("...") != -1): 
                authors_lst.remove(author)
            
        pub_year = author_year_pub[1].split(",")
        pub = None
        year = None
        if len(pub_year) == 1:
            year = pub_year[0]
            try:
                year = int(year)
            except Exception:
                year = None      
            
            if len(pub_year) == 2:
                pub = pub_year[0]
                year = pub_year[1]     
                if (pub.find("...") != -1 ):
                    pub = None        
            
        return [authors, pub, year]   
        
        
