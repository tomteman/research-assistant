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
import DBFollow
from django.utils import simplejson
import GlobalVariables
import SearchParams
         
       
class MyFollows(webapp.RequestHandler):
    def get(self):

        t = get_template('myFollows.html')
        c = Context()
        
        user = users.get_current_user()
        follows = DBFollow.get_all_users_dbfollows(user)
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        
        c['users'] = users
        c['users'] = users
        c['myFollows']=follows;
        
        
        self.response.out.write(t.render(c))   
        
        
    def post(self):
        
        name=self.request.get("name_to_remove")
        action_type=self.request.get("action_type")
        user = users.get_current_user()
        
        if (action_type == "remove"):
            count = DBFollow.remove_DBFollow(user, name)
            if (count == 0):
                self.response.out.write(simplejson.dumps(count))
            else:    
                self.response.out.write(simplejson.dumps("1"))
        else:
            sParams = DBFollow.getSearchParamsObj(user, name)
            sParams.year_start=""
            GlobalVariables.GLOBAL_searchParams = sParams
            self.response.out.write(simplejson.dumps("true"))
        
        
        