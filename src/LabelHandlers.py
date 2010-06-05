from google.appengine.ext import webapp
from google.appengine.api import users

import os
import types
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from django.template import Template,Context
from django.conf import settings 
from django.template.loader import get_template

import Label
import JSONConvertors
import HTMLparser
import pickle
from django.utils import simplejson


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
        label_name = self.request.get('Id')
        htmlParser = Label.get_articles_list_with_label_as_HTMLParser(user, label_name)
        results = htmlParser.results
        my_html_parser_encoder = JSONConvertors.HTMLparserEncoder()
        resultsJSON = my_html_parser_encoder.encode(htmlParser)
        c['users'] = users
        c['results'] = results
        c['resultsJSON'] = resultsJSON
        c['formAction'] = '/AddFollow'
        
        self.response.out.write(t.render(c))
                

        
class ShareLabel(webapp.RequestHandler):
    
    def get(self):
        inviting_user = users.get_current_user()
        label_name = self.request.get('Id')
        new_user_email = "romalabunsky@gmail.com"

        Label.share_label_request(inviting_user, label_name, new_user_email)        
        
        
        
        