from SearchParams import *
from ArticleData import ArticleData
import datetime
import string
import HTMLparser
from DBFollow import DBFollow
import pickle
import urllib

class Follow:
    def __init__(self, 
                 user = None, 
                 user_nickname = None,
                 user_id = None,
                 follow_name = None, 
                 search_params = None, 
                 update_frequency = "weekly",
                 is_empty_query = False, # this is filled with True when user added a follow 
                                         # and was prompt that the search params he gave result in a url that 
                                         # currently gives no answer.
                                         # If he approves, this is filled with True.
                 num_of_update_requests = 0, 
                 num_of_meaningful_updates = 0,
                 time_first_created = None, # This field is filled in DBFollow when upoaded
                 time_last_updated = None,  # This field is filled in DBFollow when upoaded
                 total_num_of_articles = 0,       
                 pastResultsKeysList = None, 
                 url = None):
        
        self.user = user
        self.user_nickname = user_nickname
        self.user_id = user_id
        self.follow_name = follow_name
        self.search_params = search_params
        self.pastResultsKeysList = pastResultsKeysList
        self.url = url
        self.update_frequency = update_frequency
        self.num_of_update_requests = num_of_update_requests
        self.num_of_meaningful_updates = num_of_meaningful_updates
        self.time_first_created = time_first_created
        self.time_last_updated = time_last_updated
        #self.num_of_articles_added_last_update = num_of_articles_added_last_update,
        self.total_num_of_articles = total_num_of_articles,
    
    def create_follow_name_from_search_params(self):
        if self.search_params == None:
            return False
        self.follow_name = ""
        # if it is citing an article:
        if (self.search_params.citesArticleName != None and (len(self.search_params.citesArticleName) > 0)):
            if (len(self.search_params.author) > 0):
                self.follow_name += "author: " +  urllib.unquote_plus(self.search_params.author) + " + "
            if (len(self.search_params.keywords) > 0):
                self.follow_name += "keyword: " +  urllib.unquote_plus(self.search_params.keywords) + " + "
            self.follow_name += "Documents citing: " 
            self.follow_name += urllib.unquote_plus(self.search_params.citesArticleName)
        else:
            if (len(self.search_params.keywords) != 0):
                self.follow_name += "keywords: " + urllib.unquote_plus(self.search_params.keywords)
            if (len(self.search_params.author) != 0):
                self.follow_name += " author: " + urllib.unquote_plus(self.search_params.author)
            if (len(self.search_params.journal)!= 0):
                self.follow_name += " journal : " + urllib.unquote_plus(self.search_params.journal)
            if (len(self.search_params.year_start) != 0):
                self.follow_name += " From Year : " + urllib.unquote_plus(self.search_params.year_start)
        
        return True
    
    # Return value: number of results found 
    def first_follow_query(self):
        
        results = HTMLparser.getAllResultsFromURLwithProxy(self.search_params)
        #results = resultsObject.get_results() # results is a list of articles
        self.total_num_of_articles = len(results)
        
        self.pastResultsKeysList = []
        
        for article in results:
            self.pastResultsKeysList.append(article.get_key())
        
        return len(results)
        
    
    # Before this method, run first_follow_query
    # this method does not care if query is empty. 
    # It assumed this was checked before
    def first_upload(self):
        
        if (self.url == None):
            self.url = self.search_params.constructURL()
        # convert to DBFollow and insert time fields 
        db_follow = self.convert2DBFollow()
        db_follow.time_last_updated = datetime.datetime.now()

        try: 
            db_follow.put()
        except Exception:
           return False
       
        return True
        
   
    def convert2DBFollow(self):
        
        db_follow = DBFollow()
        db_follow.user = self.user
        db_follow.user_nickname = self.user_nickname
        db_follow.follow_name = self.follow_name
        
        db_follow.search_params_str = pickle.dumps(self.search_params)
        db_follow.update_frequency = self.update_frequency #db.StringProperty(choices=set(["daily","weekly","monthly"]))
        db_follow.num_of_update_requests = self.num_of_update_requests #db.IntegerProperty()
        db_follow.num_of_meaningful_updates = self.num_of_meaningful_updates #db.IntegerProperty()
        db_follow.time_last_updated = self.time_last_updated
        db_follow.pastResultsKeysList = self.pastResultsKeysList # StringListProperty()
        db_follow.total_num_of_articles = self.total_num_of_articles
        db_follow.url = self.url #db.TextProperty()
        
        return db_follow