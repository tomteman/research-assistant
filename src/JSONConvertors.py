#from json import *
import json
import ArticleData
import HTMLparser
import ArticleURLandTitle
from urllib import quote
import Label
from django.utils import simplejson
from google.appengine.api import users

####
## use default method if you intentto later on wrap the data with json.dumps
## and encode if this is the final wrap
#### 

class ArticleURLandTitleEncoder(simplejson.JSONEncoder):
    """  a custom JSON encoder for ArticleURLandTitle objs """
    def default(self, obj):
        if not isinstance (obj, ArticleURLandTitle.ArticleURLandTitle):
            print 'You cannot use the JSON custom ArticleDataEncoder for a non-ArticleURLandTitleEncoder obj.'
            return
        json_dict = {}
        json_dict['articleTitle'] = obj.articleTitle
        json_dict['articleURL'] = obj.articleURL
        json_dict['hasLink'] = obj.hasLink  # false if CITATION
        
        return json_dict
    
    def encode(self,obj):
        return json.dumps(self.default(obj))
        #return self.default(obj)
    

class ArticleDataEncoder(simplejson.JSONEncoder):
    """  a custom JSON encoder for ArticleData objs """
    def default(self, obj):
        if not isinstance (obj, ArticleData.ArticleData):
            print 'You cannot use the JSON custom ArticleDataEncoder for a non-ArticleDataEncoder obj.'
            return
        my_article_URL_and_title_encoder = ArticleURLandTitleEncoder()
        json_dict = {}
        json_dict['key'] = obj.key
        json_dict['BibTexURL'] = obj.BibTexURL
        
        # list of ArticleURLandTitle objs
        json_dict['HTML_urlList'] = []
        for article_url_and_title in obj.HTML_urlList:
            json_dict['HTML_urlList'].append(my_article_URL_and_title_encoder.default(article_url_and_title))
          
        json_dict['HTML_author_year_pub'] = obj.HTML_author_year_pub
        json_dict['HTML_abstract'] = quote(obj.HTML_abstract, "")  
        json_dict['BibTex_dict'] = obj.BibTex_dict
        json_dict['citationsURL'] = obj.citationsURL
        json_dict['citationsID'] = obj.citationsID
        json_dict['citationsNUM'] = obj.citationsNUM
        json_dict['related_articlesURL'] = obj.related_articlesURL
        json_dict['related_articlesID'] = obj.related_articlesID
        json_dict['all_versionsURL'] = obj.all_versionsURL
        json_dict['all_versionsID'] = obj.all_versionsID
        json_dict['cacheURL'] = obj.cacheURL
        json_dict['cacheID'] = obj.cacheID
        json_dict['articleTitle'] = obj.articleTitle
        json_dict['articleTitleQuoted'] = obj.articleTitleQuoted
        json_dict['articleURL'] = obj.articleURL
        
        return json_dict
    
    def encode(self,obj):
        return json.dumps(self.default(obj))
        #return self.default(obj)
    
class HTMLparserEncoder(simplejson.JSONEncoder):
    # """a custom JSON encoder for HTMLparser objs """
    def default(self, obj):
        if not isinstance (obj, HTMLparser.HTMLparser):
            print 'You cannot use the JSON custom HTMLparserEncoder for a non-HTMLparser obj.'
            return
    
        my_article_data_encoder = ArticleDataEncoder()
        json_dict = {}
        json_dict['url'] = obj.url
        #json_dict['html'] = obj.html
        
        json_dict['results'] = []
        for article_data in obj.results:
            json_dict['results'].append(my_article_data_encoder.default(article_data))
            
        json_dict['noResultsFlag'] = obj.noResultsFlag
        json_dict['refinedSearchNoResultsFlag'] = obj.refinedSearchNoResultsFlag  # flag indicating if refined search (search within citation) yielded no results
        json_dict['numOfResults'] = obj.numOfResults
        json_dict['didYouMeanFlag'] = obj.didYouMeanFlag
        json_dict['didYouMeanHTML'] = obj.didYouMeanHTML
        json_dict['didYouMeanURL'] = obj.didYouMeanURL
        json_dict['didYouMeanKeywords'] = obj.didYouMeanKeywords
    
        return json_dict
    
    def encode(self,obj):
        return json.dumps(self.default(obj))
        #return self.default(obj)



class LabelEncoder(simplejson.JSONEncoder):
    # """a custom JSON encoder for Label objs """
    def default(self, obj):
        if not isinstance (obj, Label.Label):
            print 'You cannot use the JSON custom LabelEncoder for a non-Label obj.'
            return
    
        json_dict = {}
        
        my_user_encoder = UserEncoder()
        json_dict['users_list'] = []
        for my_user in obj.users_list:
            json_dict['users_list'].append(my_user_encoder.default(my_user))
            
        #users_list = db.ListProperty(users.User) 
        json_dict['label_name'] = obj.label_name
        json_dict['comment']  = obj.comment
        json_dict['serialized_article']  = obj.serialized_article
        json_dict['article_key'] = obj.article_key
        json_dict['is_shared'] = obj.is_shared
    
        return json_dict
    
    def encode(self,obj):
        return json.dumps(self.default(obj))
        #return self.default(obj)
    
    
class UserEncoder(simplejson.JSONEncoder):
    # """a custom JSON encoder for Label objs """
    def default(self, obj):
        if not isinstance (obj, users.User):
            print 'You cannot use the JSON custom UserEncoder for a non-users.User obj.'
            return
    
        json_dict = {}
        json_dict['user_email'] = obj.email()
        json_dict['user_id'] = obj.user_id()
        json_dict['user_nickname'] = obj.nickname()        
        
    
        return json_dict
    
    def encode(self,obj):
        return json.dumps(self.default(obj))
        #return self.default(obj)
   
