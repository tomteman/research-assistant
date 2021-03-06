from google.appengine.ext import webapp
from google.appengine.api import users

import os
import types
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from django.template import Template,Context
from django.conf import settings 
from django.template.loader import get_template
import PendingSharedLabel

import Label
import JSONConvertors
import HTMLparser
import pickle
from django.utils import simplejson
import PendingSharedLabel


class GetAllLabels(webapp.RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        if (self.request.get('Type') == 'All'):
            str = Label.get_label_object_list_for_user_JSON(user)
            self.response.out.write(str)
        elif (self.request.get('Type') == 'Unique'):
            str = Label.get_labels_dict_JSON(user) 
            self.response.out.write(str)
            
            
class UpdateLabelDB(webapp.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        res = Label.add_label_JSON_INPUT(user,self.request.body)
        self.response.out.write(simplejson.dumps(res))
        
        
class UpdateArticleLabelDB(webapp.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        article_key = self.request.get('article_key')
        comment_content =self.request.get('comment_content')
        res = Label.update_comment(user, label_name, article_key, comment_content)
        self.response.out.write(simplejson.dumps(res))

class RemoveLabelDB(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        article_key = self.request.get('article_key')
        res = Label.remove_label_from_article(user, label_name, article_key)
        self.response.out.write(simplejson.dumps(res))
        
    def get(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        res = Label.delete_label(user,label_name)
        if (not res):
            self.response.out.write(simplejson.dumps(""))
        else:    
            self.response.out.write(simplejson.dumps(label_name))
          
            
class RenameLabelDB(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        new_name = self.request.get('new_name')
        res = Label.rename_label(user, label_name, new_name)
        if (res != True):
            self.response.out.write(simplejson.dumps(""))
        else:    
            self.response.out.write(simplejson.dumps(label_name + "_|_" + new_name))
          

            


        
class ShowArticlesByLabel(webapp.RequestHandler):
    
    def get(self):
        t = get_template('search.html')
        c = Context()
        user = users.get_current_user()
        if self.request.get('action_type') == "ShowLabel":
            label_name = self.request.get('Id') 
            htmlParser = Label.get_articles_list_with_label_as_HTMLParser(user, label_name)
            
        elif self.request.get('action_type') == "ShowPending":
            label_name = self.request.get('pending_id')
            htmlParser = PendingSharedLabel.pending_share_preview_as_HTMLparser(user, label_name)
            if (isinstance( htmlParser, int)):
                self.response.out.write("an error occurred")
                return     
        
        results = htmlParser.results    
        my_html_parser_encoder = JSONConvertors.HTMLparserEncoder()
        resultsJSON = my_html_parser_encoder.encode(htmlParser)      
        c['users'] = users
        c['hidden_label_name'] = label_name
        c['results'] = results
        c['resultsJSON'] = resultsJSON
        c['formAction'] = '/AddFollow'
        c['showlabel'] = True
        c['showlabelsearch'] = True
        self.response.out.write(t.render(c))
                

        

class ShareLabel(webapp.RequestHandler):
    
    def post(self):
        inviting_user = users.get_current_user()
        label_name = self.request.get('label_name')
        new_user_email = self.request.get('user_name')
        res = Label.share_label_request(inviting_user , label_name, new_user_email, True)
        self.response.out.write(simplejson.dumps(res)) 


class GetSharedLabelUsers(webapp.RequestHandler):
    
    def post(self):
        label_name = self.request.get('label_name')
        user = users.get_current_user()
        res = Label.get_emails_of_users_on_this_shared_label(user, label_name)
        self.response.out.write(res) 

class RemoveFromSharedLabelDB(webapp.RequestHandler):
    def post(self):
        label_name = self.request.get('label_name')
        user = users.get_current_user()
        res = Label.remove_user_from_shared_label(user, label_name)
        self.response.out.write(simplejson.dumps(res)) 

class DuplicateSharedLabelToPrivate(webapp.RequestHandler):
    def post(self):
        label_name = self.request.get('label_name')
        user = users.get_current_user()
        res = Label.duplicate_label_to_private(user, label_name)
        self.response.out.write(res)

class SearchInLabel(webapp.RequestHandler):
    def post(self):
        t = get_template('search.html')
        c = Context()
        user = users.get_current_user()
        search_term = self.request.get('SearchTerm')
        label_name = self.request.get('hidden_label_name')
        htmlParser = Label.search_in_labels_return_HTMLparser(user, label_name, search_term)
        results = htmlParser.results
        if len(results) == 0:
            self.response.out.write("No results found")
            return
        my_html_parser_encoder = JSONConvertors.HTMLparserEncoder()
        resultsJSON = my_html_parser_encoder.encode(htmlParser)
        c['users'] = users
        c['results'] = results
        c['resultsJSON'] = resultsJSON
        c['formAction'] = '/AddFollow'
        c['showlabel'] = True
        c['showlabelsearch'] = False
        self.response.out.write(t.render(c))
                
class SendLabel(webapp.RequestHandler):
    def post(self):
        inviting_user = users.get_current_user()
        label_name = self.request.get('label_name')
        new_user_email = self.request.get('user_name')
        res = Label.get_label_by_email(inviting_user , new_user_email, label_name)
        self.response.out.write(simplejson.dumps(res))
        

        
        
        
