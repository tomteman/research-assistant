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
import PendingSharedLabel
from django.utils import simplejson


         
       
class ShowPendings(webapp.RequestHandler):
    def get(self):

        t = get_template('showPendings.html')
        c = Context()
        
        user = users.get_current_user()
        MyPendings = PendingSharedLabel.get_all_users_PendingSharedLabel(user)
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        
        c['users'] = users
        c['users'] = users
        c['MyPendings']=MyPendings;
        self.response.out.write(t.render(c))   
        
    
    def post(self):
        
        pending_id=self.request.get("pending_id")
        action_type=self.request.get("action_type")
        invited_user = users.get_current_user()
        
        if (action_type == "accept"):
            res = PendingSharedLabel.acceptPendingSharedLabel(invited_user, pending_id)
            
        elif (action_type == "reject"):
            res = PendingSharedLabel.remove_PendingSharedLabel(invited_user, pending_id)
            
        elif (action_type == "preview"):
            res = PendingSharedLabel.pending_share_preview_as_HTMLparser(invited_user, pending_id)
            
        self.response.out.write(simplejson.dumps(res))
        
        
        