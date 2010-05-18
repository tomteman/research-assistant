# -*- coding: cp1255 -*-
#QM = "\""

################### Lea:  TODO for next time:

# Check the follow on 8081 :) http://localhost:8081/_ah/admin/datastore?kind=DBFollow
# some problem with the pickle #search_params_str = db.StringProperty(multiline=True)


from SearchParams import *
from ArticleData import ArticleData
import datetime
import string
import HTMLparser
from DBFollow import DBFollow
import pickle
# TODO: change defaults in the __init__ function
# TODO : decide which fields should be required


    
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
                 #num_of_articles_added_last_update = 0,
                 time_first_created = None, # This field is filled in DBFollow when upoaded
                 time_last_updated = None,  # This field is filled in DBFollow when upoaded
                 time_last_modified_by_user = None,
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
        self.time_last_modified_by_user = time_last_modified_by_user
    
    def create_follow_name_from_search_params(self):
        if self.search_params == None:
            return False
        self.follow_name = ""
        # if it is citing an article:
        if (self.search_params.citesArticleName != None and (len(self.search_params.citesArticleName) > 0)):
            if (len(self.search_params.author) > 0):
                self.follow_name += "author: " +  self.search_params.author + " + "
            if (len(self.search_params.keywords) > 0):
                self.follow_name += "keyword: " +  self.search_params.keywords + " + "
            self.follow_name += "Documents citing: " 
            self.follow_name += self.search_params.citesArticleName
        else:
            if (len(self.search_params.keywords) != 0):
                self.follow_name += "keywords: " + self.search_params.keywords
            if (len(self.search_params.author) != 0):
                self.follow_name += "author: " + self.search_params.author
            if (len(self.search_params.journal)!= 0):
                self.follow_name += "journal : " + self.search_params.journal
            if (len(self.search_params.year_start) != 0):
                self.follow_name += "From Year : " + self.search_params.year_start
        
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
        db_follow.time_last_modified_by_user = datetime.datetime.now()

        #try: 
        db_follow.put()
        #except Exception:
        #   print "In first upload: Could not upload to DB\n"
        return True
        
   
# TODO: make everything here in try and catch, so if convert fails, it will write something instead in the field.
# In case it is a critical value - inform...
    def convert2DBFollow(self):
        
        db_follow = DBFollow()
        db_follow.user = self.user
        db_follow.user_nickname = self.user_nickname
        db_follow.follow_name = self.follow_name
        #db_follow.search_params_str = db.Text(marshal.dumps(self.search_params))  # db.TextProperty()
        
        db_follow.search_params_str = pickle.dumps(self.search_params)
        db_follow.update_frequency = self.update_frequency #db.StringProperty(choices=set(["daily","weekly","monthly"]))
        db_follow.num_of_update_requests = self.num_of_update_requests #db.IntegerProperty()
        db_follow.num_of_meaningful_updates = self.num_of_meaningful_updates #db.IntegerProperty()
        db_follow.time_last_updated = self.time_last_updated
        db_follow.time_last_modified_by_user = self.time_last_modified_by_user
        db_follow.pastResultsKeysList = self.pastResultsKeysList # StringListProperty()
        #db_follow.num_of_articles_added_last_update = self.num_of_articles_added_last_update
        db_follow.total_num_of_articles = self.total_num_of_articles
        db_follow.url = self.url #db.TextProperty()
        #db_follow.time_first_created - is filled automatically
        
        return db_follow