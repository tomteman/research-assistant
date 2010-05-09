#QM = "\""
# -*- coding: cp1255 -*-
import GeneralFuncs
from ArticleData import *
import datetime
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import os
from google.appengine.ext.webapp import template

#test

DEBUG = False

# TODO: check how to do enum for update_frequency, max_results_in_update etc.
# TODO: change defaults in the __init__ function




# see results in http://localhost:8080/

# TODO : decide which fields should be required
class DBFollow(db.Model):
    user = db.UserProperty()
    follow_name = db.StringProperty()
    search_params_str = db.TextProperty()
    update_frequency = db.StringProperty(choices=set(["day","week","monthly"]))
    max_results_in_update = db.IntegerProperty(choices=set([10,20,50]))
    num_of_updates = db.IntegerProperty()
    num_of_successful_updates = db.IntegerProperty()
    time_first_created = db.DateTimeProperty()
    time_last_updated = db.DateTimeProperty()
    pastResultsKeysList_str = db.TextProperty()
    url = db.TextProperty()
    
class Follow:
    def __init__(self, 
                 user = None, 
                 user_nickname = None,
                 user_id = None,
                 follow_name = None, 
                 search_params = None, 
                 update_frequency = "weekly", 
                 num_of_update_requests = 0, 
                 num_of_meaningful_updates = 0,
                 time_first_created = None, # This field is filled in DBFollow when upoaded
                 time_last_updated = None,  # This field is filled in DBFollow when upoaded
                 time_last_modified_by_user = None,

                 pastResultsKeysList = [], 
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
        self.time_last_modified_by_user = time_last_modified_by_user
        
# Getters and Setters
# TODO - add all necessary

    def get_pastResultsDict(self):
        return self.pastResultsDict
    def get_last_updated(self):
        return self.last_updated
    def get_updateFrequency(self):
        return self.search_params.update_frequency
    def get_name(self):
        return self.name
    def get_url(self):
        return self.url
    def get_searchParams(self):
        return self.search_params

   #Other Methods:
   # TODO: When tom writes the part that returns details from a key, you can make this function better.
    def create_email_message(self, diff_list):
        message = "Hello Dear " + self.username + "!\n"
        message = message + "This is a new update on your follow named: " + self.follow_name + "\n"
        message = message + "There are " + str(len(diff_list)) + " new articles: \n\n"
        for key in diff_list:
            # TODO: change this back to what it was when TOM changes function
            # printArticle to __str__
            message = message + "key: " + key + "\n\n"
            #message = message + article.printArticle()
            #message = message + "\t\t****************************************\n\n"
        message = message + "To remove this follow please press HERE\n\n"
        message = message + "©  This update brought to you by RESEARCH ASSISTANT\n"
        return message
        
            
    # update_follow:
    #   Checks if there are new articles for this follow's url"
    #   if so: sends mail, updates the date and the saved 
    def update_follow(self):
        
        
        # OLD DICTIONARY
        old_dict = self.get_pastResultsDict()
        if (old_dict == None): 
            print "update_follow: get_pastResultsDict returned is empty. Quiting..." #TODO: raise exception
        
        # NEW DICTIONARY
        if (self.url == None): 
            print "update_follow: Couldn't get url for this follow. Quiting..." #TODO: raise exception
       
        # TODO: change this part when Tom changes his part.
        # TODO: this part is only because for now we need to show difference between two URLS
        if (len(old_dict) != 0):
            #new_dict = {}
            new_dict = old_dict.copy()
            article1 = ArticleData()
            article1.set_key("new added article")
            new_dict[article1.get_key()] = article1

        else: 
            new_dict = GeneralFuncs.url2ArticleDict(self.url)
            if (new_dict == None): 
                print "update_follow: Dict returned by url2ArticleDict is empty. Quiting..." #TODO: raise exception
        my_str = str(new_dict)
        
        #diff_dict = GeneralFuncs.compareDicts(old_dict, new_dict)
        diff_list = GeneralFuncs.compareKeysLists(old_dict.keys(), new_dict.keys())
        if (len(diff_list) == 0):
            print "update_follow: No difference From last result was found\n"
        else:
            # TODO: add here try and catch on the email sending, and only afterwards update follow and add to DB
            email_message = self.create_email_message(diff_list)
            GeneralFuncs.sendEmail("lea.stolo@gmail.com", email_message)
            
            self.last_updated = datetime.datetime.now()

            # Add the new articles to the saved dictionary
            for key in diff_list:
                if self.pastResultsDict.has_key(key):
                    print "update_follow: There was some problems here.\n The Diff dictionary has a key that already exists in the pastResultsDict\n"       
                    # TODO - change this print to some exception or something. 
                else:
                    self.pastResultsDict[key] = ""
                    #self.pastResultsDict[key] = diff_dict[key]

        print "Done Follow Updating."

#    def upload_follow_to_DB(self):

    def convert2DBFollow(self):
        db_follow = DBFollow()
        #db_follow.user = self.username
        db_follow.follow_name = self.follow_name
        db_follow.search_params_str = str(self.search_params)  # db.TextProperty()
        # TODO: check if self.update_frequency is indeed one of the options
        db_follow.update_frequency = self.update_frequency #db.StringProperty(choices=set(["daily","weekly","monthly"]))
        db_follow.max_results_in_update = self.max_results_in_update #db.IntegerProperty(choices=set([10,20,50]))
        
        db_follow.num_of_updates = self.num_of_updates #db.IntegerProperty()
        db_follow.num_of_successful_updates = self.num_of_successful_updates #db.IntegerProperty()
        
        # TODO: Resolve this
        #db_follow.time_first_created = db.DateTimeProperty()
        #db_follow.time_last_updated = db.DateTimeProperty()
        db_follow.pastResultsKeysList_str = str(self.pastResultsKeysList) #db.TextProperty()
        db_follow.url = self.get_url() #db.TextProperty()
        
        return db_follow
    
#    def convert_DBFollow2Follow(db_fllow):
#        
#        new_follow = Follow()
#        new_follow.username = db_fllow.user.nickname()
#        new_follow.follow_name = db_fllow.follow_name
#        
#        new_follow.search_params = eval(db_fllow.search_params_str)  # db.TextProperty()
#        # TODO: check if self.update_frequency is indeed one of the options
#        new_follow.update_frequency = db_fllow.update_frequency #db.StringProperty(choices=set(["daily","weekly","monthly"]))
#        new_follow.max_results_in_update = db_fllow.max_results_in_update #db.IntegerProperty(choices=set([10,20,50]))
#        
#        new_follow.num_of_updates = db_fllow.num_of_updates #db.IntegerProperty()
#        new_follow.num_of_successful_updates = db_fllow.num_of_successful_updates #db.IntegerProperty()
#        
#        # TODO: Resolve this
#        #db_follow.time_first_created = db.DateTimeProperty()
#        #db_follow.time_last_updated = db.DateTimeProperty()
#        new_follow.pastResultsKeysList_str = str(db_fllow.pastResultsKeysList) #db.TextProperty()
#        new_follow.url = db_fllow.get_url() #db.TextProperty()
#        
    
        



