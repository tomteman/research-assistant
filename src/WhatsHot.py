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
from Suggestions import get_list_of_suggested_article_ordered_by_rank
from Suggestions import get_list_of_suggested_article_ordered_by_date
from Suggestions import remove_suggestion
from Suggestions import get_num_of_suggestions_for_user

import Label
import JSONConvertors
import HTMLparser
import pickle
from django.utils import simplejson
import PendingSharedLabel


class removeSuggestedFromDB(webapp.RequestHandler):
    def post(self):
        user= users.get_current_user()
        Id = self.request.get('Id')
        res = remove_suggestion(user, Id)
        self.response.out.write(res)

        
        
        
class ShowHot(webapp.RequestHandler):

    def get(self):
        
        c = Context()
        user = users.get_current_user()
        
        htmlParser = get_list_of_suggested_article_ordered_by_rank(user)
        numOfSuggestions = get_num_of_suggestions_for_user(user)
        if (numOfSuggestions == 0):
            t = get_template('noResults.html')
            c['noSuggestions'] = 1

        else:
            t = get_template('search.html')
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