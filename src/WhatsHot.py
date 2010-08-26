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
from Suggestions import get_list_of_suggested_article_ordered
import Label
import JSONConvertors
import HTMLparser
import pickle
from django.utils import simplejson
import PendingSharedLabel


class RemoveSuggested(webapp.RequestHandler):
    def get(self):
        user= users.get_current_user()
        
        
        
class ShowHot(webapp.RequestHandler):

    def get(self):
        t = get_template('search.html')
        c = Context()
        user = users.get_current_user()
        
        htmlParser = get_list_of_suggested_article_ordered(user)
        results = htmlParser.results
        my_html_parser_encoder = JSONConvertors.HTMLparserEncoder()
        resultsJSON = my_html_parser_encoder.encode(htmlParser)
        c['suggestFlag'] = 1
        c['users'] = users
        c['results'] = results
        c['resultsJSON'] = resultsJSON
        c['formAction'] = '/AddFollow'
        c['showlabel'] = True
        self.response.out.write(t.render(c))