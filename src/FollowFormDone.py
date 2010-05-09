import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from django.template import Template,Context
from django.conf import settings 
from django.template.loader import get_template


from SearchParams import *

import Follow
import string

class FollowFormDone(webapp.RequestHandler):
    def post(self):
         
        # = self.request.get()
        forms = ("follow_name", "ch_keywords", "keywords",
                  "ch_author", "author", "ch_journal", "journal",
                 "ch_citing", "citing_num", "update_frequency" )
        
       
        vars = {}
        for form in forms:
            vars[form] = self.request.get(form)
           
        keywords = vars["keywords"] if vars['ch_keywords'] else ""
        author = vars["author"] if vars["ch_author"] else ""              
        journal = vars["journal"] if vars["ch_journal"] else ""
        
        cites =  vars["citing_num"] if vars["ch_citing"] else ""
                       
        s_params = SearchParams(keywords = keywords,  author=author, journal=journal,
                                num_of_results = 100, cites = cites )
 
        user = users.get_current_user()
        if (user != None):
            user_nickname = user.nickname()
            user_id = user.user_id()
        else:   ##TODO - log in redirection
            user_nickname = None
            user_id = None
      
        follow = Follow.Follow(user = user, user_nickname=user_nickname, user_id=user_id, follow_name=vars["follow_name"],
                               search_params=s_params, update_frequency=vars["update_frequency"], url = s_params)
            
           
        try: 
            follow.first_upload()
        except:
            #ResearchExceptions.InputError: #as detail:
            pass   
                        

        t = get_template('followFormDone.html')
        c = Context()
        c['Title'] = 'Research-assistant about project'
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users

        self.response.out.write(t.render(c))    
        
         
        
        
        
       