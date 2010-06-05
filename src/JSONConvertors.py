import ArticleData
import HTMLparser
import ArticleURLandTitle
import urllib 
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
            print 'You cannot use the JSON custom ArticleDataEncoder for a non-ArticleURLandTitle obj.'
            return
        json_dict = {}
        json_dict['articleTitle'] = obj.articleTitle
        json_dict['articleURL'] = obj.articleURL
        json_dict['hasLink'] = obj.hasLink  # false if CITATION
        
        return json_dict
    
    def encode(self,obj):
        return simplejson.dumps(self.default(obj))
        #return self.default(obj)
        
class ArticleURLandTitleDecoder(simplejson.JSONEncoder):
    """  a custom JSON decoder for ArticleURLandTitle objs """
    def decode (self, json_string):
        article_url_and_data_dict = json_string #simplejson.loads(json_string)
        article_url_and_data_obj = ArticleURLandTitle.ArticleURLandTitle()
        article_url_and_data_obj.set_article_title(article_url_and_data_dict['articleTitle'])
        article_url_and_data_obj.set_article_url(article_url_and_data_dict['articleURL'])
        article_url_and_data_obj.set_has_link(article_url_and_data_dict['hasLink'])
        return article_url_and_data_obj
    


class ArticleDataDecoder(simplejson.JSONDecoder):
    def decode (self, json_string):
        # use json's generic decode capability to parse the serialized string
        # into a python dictionary.
        article_data_dict = json_string # simplejson.loads(json_string) - 
                                        # if you want to return this for other uses, you should call from "add_label" 
                                        # with simplejson.dumps
                                        # example: instead of:
                                                    # article_data_obj = article_data_decoder.decode(article_json_string)
                                                    # write: article_data_obj = article_data_decoder.decode(simplejson.dumps(article_json_string))  
        article_url_and_data_decoder = ArticleURLandTitleDecoder()
        old_html_url_list = article_data_dict['HTML_urlList']
        new_html_url_list = []
        for article_url_and_data_string in old_html_url_list:
            new_html_url_list.append(article_url_and_data_decoder.decode(article_url_and_data_string))
            
        article_data = ArticleData.ArticleData()
        article_data.set_key(article_data_dict['key'])
        article_data.set_bib_tex_url(article_data_dict['BibTexURL'])
        article_data.set_HTML_urlList(new_html_url_list)
        article_data.set_HTML_author_year_pub(article_data_dict['HTML_author_year_pub'])
        article_data.set_HTML_abstract(urllib.unquote(article_data_dict['HTML_abstract']))
        article_data.set_bib_tex_dict(article_data_dict['BibTex_dict'])
        article_data.set_citations_url(article_data_dict['citationsURL'])
        article_data.set_citations_ID(article_data_dict['citationsID'])
        article_data.set_citations_NUM(article_data_dict['citationsNUM'])
        article_data.set_related_articles_url(article_data_dict['related_articlesURL'])
        article_data.set_related_articls_ID(article_data_dict['related_articlesID'])
        article_data.set_all_versions_url(article_data_dict['all_versionsURL'])
        article_data.set_all_versions_ID(article_data_dict['all_versionsID'])
        article_data.set_cache_url(article_data_dict['cacheURL'])
        article_data.set_cache_ID(article_data_dict['cacheID'])
        article_data.set_articleTitle(article_data_dict['articleTitle'])
        article_data.set_articleTitleQuoted(article_data_dict['articleTitleQuoted'])
        article_data.set_articleURL(article_data_dict['articleURL'])
                                               
        
        return article_data
        


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
        json_dict['HTML_abstract'] = urllib.quote(obj.HTML_abstract, "")  
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
        return simplejson.dumps(self.default(obj))
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
        return simplejson.dumps(self.default(obj))
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
        ### currently i'm not passing the article_abstract_title_author
    
        return json_dict
    
    def encode(self,obj):
        return simplejson.dumps(self.default(obj))
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
        return simplejson.dumps(self.default(obj))
        #return self.default(obj)
   
