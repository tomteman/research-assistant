import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from django.template import Template,Context
from django.conf import settings 
from django.template.loader import get_template

                            #local imports
import GeneralFuncs
#import FollowForm
from FollowForm import  *
from getHTML import *
from SearchParams import *
from HTMLparser import *

import Follow
import string

class FollowFormDone(webapp.RequestHandler):
    def post(self):
         
        # = self.request.get()
        forms = ("follow_name", "ch_keywords", "keywords",
                  "ch_author", "author", "ch_journal", "journal",
                 "ch_citing", "update_frequency" )
        
       
        vars = {}
        for form in forms:
            vars[form] = self.request.get(form)
           
        keywords = vars["keywords"] if vars['ch_keywords'] =="on" else ""
        author = vars["author"] if vars["ch_author"] else ""              
        journal = vars["journal"] if vars["ch_journal"] else ""
        
        #citing =  if vars["ch_citing"] else ""
                       
        s_params = SearchParams(keywords = keywords,  author=author, journal=journal)
                                    #cites = sites_param)

            
        follow = Follow.Follow(  user = "", user_nickname="", user_id="", follow_name=vars["follow_name"],
                               search_params=s_params, update_frequency=vars["update_frequency"])
            
           
            
          #       first_created = first_created, last_updated = "", pastResultsDict="", url = None)
        
        
#        db_follow = follow.convert2DBFollow()
#        db_follow.put()
#                       

        t = get_template('followFormDone.html')
        c = Context()
        c['Title'] = 'Research-assistant about project'
        c['formAction'] = "/"
        self.response.out.write(t.render(c))    
        
        
        
        
        
        
#                       class FollowFormDone(webapp.RequestHandler):
#    def post(self):
#        self.response.out.write("""<html>
#                                <head><title>Done Filling Follow Form </title></head>
#                                <body><b>Thank you for sending the follow!</b><br><br>
#                                We Will Soon send you some interesting updates!</body></html>""")
#
#        forms = ("follow_name","regular_update","ch_keywords","keywords",
#                 "ch_all_words","all_words","ch_exact_phrase", "exact_phrase",
#                  "ch_within_the_words","within_the_words", "ch_author", "author",
#                  "ch_journal", "journal","ch_one_of_the_words","one_of_the_words",
#                 "citation_update","ch_citing", "citing", "ch_keywords_citing",
#                 "keywords_citing", "update_frequency" )
#        
#       
#        vars = {}
#        for form in forms:
#            vars[form] = self.request.get(form)
#           
#        keywords = vars["keywords"] if vars['ch_keywords'] =="on" else ""
#        all_words = vars["all_words"] if vars['ch_all_words'] == "on" else "" 
#        exact_phrase = vars["exact_phrase"] if vars["ch_exact_phrase"] == "on" else "" 
#        one_of_the_words = vars["one_of_the_words"] if vars["ch_one_of_the_words"] == "on" else ""
#        within_the_words = vars["within_the_words"] if vars["within_the_words"] == "on" else ""
#        author = vars["author"] if vars["ch_author"] else ""              
#        journal = vars["journal"] if vars["ch_journal"] else ""
#        
#        #cites_param = cites if cites!=None else ""
#        
#        
#               
#        s_params = SearchParams.SearchParams(keywords = keywords, all_words = all_words,
#                                            exact_phrase = exact_phrase, one_of_the_words=one_of_the_words,
#                                            within_the_words=within_the_words, author=author, journal=journal)
#                                            #cites = sites_param)
#        
#        first_created = lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date()
#
#        follow = Follow.Follow( username = "", follow_name = vars["follow_name"], search_params=s_params, 
#                                update_frequency = vars["update_frequency"],
#                                num_of_updates = 0, num_of_successful_updates = 0,url=None)
#          #       first_created = first_created, last_updated = "", pastResultsDict="", url = None)
#        
#        
#        db_follow = follow.convert2DBFollow()
#        db_follow.put()
      
        # TODO: change this thing. It is not supposed to be here
        #follow.update_follow()
        #follow.put()
        
#        self.response.out.write("""<html>
#                                <head><title>Done Filling Follow Form </title></head>
#                                <body>Thank you for sending the follow! 
#                                We Will Soon send you some interesting updates!</body></html>""")
#
#        forms = ("follow_name","regular_update","ch_keywords","keywords",
#                 "ch_all_words","all_words","ch_exact_phrase", "ch_within_words",
#                 "within_words", "ch_author", "author", "ch_journal", "journal",
#                 "citation_update","ch_citing", "citing", "ch_keywords_citing",
#                 "keywords_citing", "update_frequency" )
#        
#        #self.request.get('article_lea')
#        #self.response.out.write(str('article_lea'))
#        vars = {}
#        for form in forms:
#            vars[form] = self.request.get(form)
#        
#        s_params = SearchParams.SearchParams(vars["keywords"])
#        # Fill this object
#        
#       # s_params.set_keywords(vars["keywords"])
#        
#        first_created = lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date()
#
#        follow = Follow.Follow( username = "", follow_name = vars["follow_name"], search_params=s_params, 
#                 update_frequency = vars["update_frequency"],
#                 num_of_updates = 0, num_of_successful_updates = 0,url=None)
#          #       first_created = first_created, last_updated = "", pastResultsDict="", url = None)
#        
#        
#        db_follow = follow.convert2DBFollow()
#        db_follow.put()
#        # TODO: change this thing. It is not supposed to be here
#        #follow.update_follow()
#        #follow.put()
#          
#        self.response.out.write(str(follow.get_searchParams()))                
        
        
        
       