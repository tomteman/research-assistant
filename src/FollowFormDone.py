import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from django.template import Template,Context
from django.conf import settings 
from django.template.loader import get_template
from google.appengine.ext import db
from SearchParams import *
import Follow
import GlobalVariables

from django.utils import simplejson
#### return values:for self.response.out.write(simplejson.dumps(-2)) 
### -1 Follow already exists
### -2 Cannot connect to DB / for some reason global follow results where None
### otherwise we return the number of results


class Submit(webapp.RequestHandler):
    def post(self):
         
        # = self.request.get()
        forms = ("follow_name", "ch_keywords", "keywords",
                  "ch_author", "author", "ch_journal", "journal",
                 "ch_citing", "citing_num", "update_frequency" ,"article")
        
       
        vars = {}
        for form in forms:
            vars[form] = self.request.get(form)
           
        keywords = vars["keywords"] if vars['ch_keywords'] else ""
        author = vars["author"] if vars["ch_author"] else ""              
        journal = vars["journal"] if vars["ch_journal"] else ""      
        citationsID =  vars["citing_num"] if vars["ch_citing"] else ""
        citesTitle =  vars["article"] if vars["ch_citing"] else ""
                       
        s_params = SearchParams(keywords = keywords,  
                                author=author, 
                                journal=journal,
                                num_of_results = 100, 
                                citationsID = citationsID, 
                                citesArticleName = citesTitle)
 
        user = users.get_current_user()
        if (user != None):
            user_nickname = user.nickname()
            user_id = user.user_id()
        else:   ##TODO - log in redirection
            user_nickname = None
            user_id = None
      
        GlobalVariables.GLOBAL_current_follow = Follow.Follow(user = user, 
                               user_nickname=user_nickname, 
                               user_id=user_id, 
                               follow_name=vars["follow_name"],
                               search_params=s_params, 
                               update_frequency=vars["update_frequency"])
        
        GlobalVariables.GLOBAL_current_follow.create_follow_name_from_search_params()
        if (GlobalVariables.GLOBAL_current_follow.check_if_already_exists(user,GlobalVariables.GLOBAL_current_follow.follow_name )):
            self.response.out.write(simplejson.dumps(-1))
        else: # if this is indeed a new follow
            num_of_query_results = GlobalVariables.GLOBAL_current_follow.first_follow_query()
            if not ((num_of_query_results == 0 ) or (num_of_query_results == 1000)):
                success = GlobalVariables.GLOBAL_current_follow.first_upload()
                if not success:
                    self.response.out.write(simplejson.dumps(-2))
            GlobalVariables.GLOBAL_searchParams = s_params        
            self.response.out.write(simplejson.dumps(num_of_query_results))
     

class FirstUpload(webapp.RequestHandler):
    def post(self):
     
        if (GlobalVariables.GLOBAL_current_follow.pastResultsKeysList != None):
            GlobalVariables.GLOBAL_current_follow.create_follow_name_from_search_params()
            success = GlobalVariables.GLOBAL_current_follow.first_upload()
            if success:
                self.response.out.write(simplejson.dumps(1))
                GlobalVariables.GLOBAL_searchParams = GlobalVariables.GLOBAL_current_follow.search_params
            else: 
                self.response.out.write(simplejson.dumps(-2))
        else:
            self.response.out.write(simplejson.dumps(-2))
            
        
        
        
        
            
class FollowFormDone(webapp.RequestHandler):
     
    def get(self):                  
        t = get_template('followFormDone.html')
        c = Context()
        c['Title'] = 'Research-assistant about project'
        if (users.get_current_user()):
            c['logout'] = users.create_logout_url(self.request.uri)
        else:
            c['login'] = users.create_login_url(self.request.uri)
        c['users'] = users

        self.response.out.write(t.render(c))        
