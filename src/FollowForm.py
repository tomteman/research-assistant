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
        t = get_template('addFollow.html')
        c = Context()
        c['Title'] = 'Research-assistant about project'
      
        c['formAction'] = "/FollowFormDone"

        bibTexKey = self.request.get('bibTexKey')
        bibTex = parseBibTexItems(bibTexKey)
        bibTexData = bibTex.values()[0]
        if bibTexData.has_key('author'):
            if isinstance(bibTexData['author'], types.ListType ):
                author = bibTexData['author'][0]
#TODO:    Handle multiple authors
        else:
            author = ""
        if bibTexData.has_key('title'):
            title = bibTexData['title'][1:len(bibTexData['title'])-1]
        else: 
            title = ""
        if bibTexData.has_key('journal'):
            journal = bibTexData['journal']
        else: 
            journal = ""
        
        keywords = self.request.get('SearchTerm')
        
        c['followName'] = "Name Your Follow"
        c['articleName'] = title
        c['articleAuthors'] = author
        c['articleJournal'] = journal
        c['keywords'] = keywords
        
        
        #    c['results'] = keyword
        self.response.out.write(t.render(c))   
        
        
