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
        bibTex = parseBibTexItems(bibTexKey)
        bibTexData = bibTex.values()[0]
        
        if bibTexData.has_key('author'):
                authors = bibTexData['author']

        else:
            author = ""
      
        if bibTexData.has_key('title'):
            title = bibTexData['title'][1:len(bibTexData['title'])-1]
            if len(title) > 80:
                title = " ".join(title.split()[0:10]) + "..."
        else: 
            title = ""
        
        if bibTexData.has_key('journal'):
            journal = bibTexData['journal']
        else: 
            journal = ""
        
        keywords = self.request.get('SearchTerm')
        numCitations = self.request.get('NumCites')
        t = get_template('addFollow.html')
        c = Context()
        c['Title'] = 'Research-assistant about project'
        c['formDoneAction'] = '/FollowFormDone'
        c['followName'] = "Name Your Follow"
        c['articleName'] = title
        c['articleAuthors'] = authors
        c['many_authors'] = isinstance(bibTexData['author'], types.ListType )
        c['authors'] = authors
        c['articleJournal'] = journal
        c['keywords'] = keywords
        c['citing_num'] = numCitations
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users
        
        self.response.out.write(t.render(c))   
        
        
