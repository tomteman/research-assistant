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
            #str = """[ {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "lea label", "article_key": "S5jpm321qq0J"}, {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "new roman label", "article_key": "JY7LVcMdJO8J"}, {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "lea label", "article_key": "JY7LVcMdJO8J"}]"""
            self.response.out.write(str)
        elif (self.request.get('Type') == 'Unique'):
            str = Label.get_labels_dict_JSON(user)
            #str = """[{"label_name": "new roman label", "number": "1"}, {"label_name": "lea label", "number": "2"}]"""
            self.response.out.write(str)
            
            
class UpdateLabelDB(webapp.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        Label.add_label_JSON_INPUT(user,self.request.body)
        
        
class UpdateArticleLabelDB(webapp.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        article_key = self.request.get('article_key')
        comment_content =self.request.get('comment_content')
        Label.update_comment(user, label_name, article_key, comment_content)


class RemoveLabelDB(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        article_key = self.request.get('article_key')
        Label.remove_label_from_article(user, label_name, article_key)
        
    def get(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        Label.delete_label(user,label_name)
        
        self.response.out.write(simplejson.dumps(label_name))
        
            


        

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
                

        
        
        
        
        
        