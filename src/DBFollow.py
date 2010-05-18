from google.appengine.api import mail
from google.appengine.ext import db
from Follow import *
import pickle
import HTMLparser
#import ResearchExceptions
import GeneralFuncs

class DBFollow(db.Model):
    user = db.UserProperty()
    user_id = db.StringProperty()
    follow_name = db.StringProperty()
    search_params_str = db.TextProperty()#multiline=True)
    update_frequency = db.StringProperty()#(choices=set(["Daily","Weekly","Monthly"]))
    num_of_update_requests = db.IntegerProperty()
    num_of_meaningful_updates = db.IntegerProperty()
    time_first_created = db.DateTimeProperty(auto_now_add=True)
    time_last_updated = db.DateTimeProperty()
    time_last_modified_by_user = db.DateTimeProperty()
    pastResultsKeysList = db.StringListProperty()
    url = db.TextProperty()
    #num_of_articles_added_last_update = db.IntegerProperty()
    total_num_of_articles = db.IntegerProperty()
    
    def convert2Follow(self):
    
        new_follow = Follow()
        new_follow.user = self.user
        if (self.user != None):
            new_follow.user_nickname = self.user.nickname()
        new_follow.user_id = self.user_id
        new_follow.follow_name = self.follow_name
        new_follow.search_params = pickle.loads(self.search_params_str)  # db.TextProperty()
        new_follow.update_frequency = self.update_frequency #db.StringProperty(choices=set(["daily","weekly","monthly"]))
        new_follow.num_of_update_requests = self.num_of_update_requests #db.IntegerProperty()
        new_follow.num_of_meaningful_updates = self.num_of_meaningful_updates #db.IntegerProperty()
        new_follow.time_first_created = self.time_first_created
        new_follow.time_last_updated = self.time_last_updated
        new_follow.time_last_modified_by_user = self.time_last_modified_by_user
        #new_follow.num_of_articles_added_last_update = self.num_of_articles_added_last_update
        new_follow.total_num_of_articles = self.total_num_of_articles
        new_follow.pastResultsKeysList = self.pastResultsKeysList
        new_follow.url = self.url
        
        return new_follow
    
    def remove_DBFollow(self):
        pass
        #if self.is_saved():
        #    self.delete()

    # Update method. This is he method used for all updates, except the first one, 
    # which is done with Follow.first_upload
    def update_DBfollow(self):
        
        # GET OLD ARTICLE KEYS FROM DB
        self.num_of_update_requests += 1   
        search_params_object = pickle.loads(str(self.search_params_str))
        
        # GET NEW ARTICLE KEYS FROM QUERY
        new_resultsList = HTMLparser.getAllResultsFromURLwithProxy(search_params_object)
        #if (new_resultsList == None):
        #    raise ResearchExceptions.InputError("In update follow", "Function: HTMLparser.getResultsFromURL(self.url) returned None\n")  
        new_resultsKeys = []
        for article in new_resultsList:
            new_resultsKeys.append(article.get_key())
        
        # Check if There are new articles  
        diff_list = GeneralFuncs.compareKeysLists(self.pastResultsKeysList, new_resultsKeys)
        
        num_new_articles = len(diff_list)
        self.total_num_of_articles += num_new_articles

        # Update the user on changes, and update the DB
        if (num_new_articles != 0):
            # TODO: add here try and catch on the email sending, and only afterwards update follow and add to DB
            email_message = self.create_email_message(diff_list, new_resultsList)
            
            # Add the new articles to the saved dictionary
            for key in diff_list:
                self.pastResultsKeysList.append(key)
                
            self.num_of_meaningful_updates += 1
        
        # In any case, update the Follow in DB
        self.time_last_updated = datetime.datetime.now()
        
        try:
            self.put()
        except Exception:
            print "Could not put to DB"
            # TODO: change this
        
        return True
    
       #Other Methods:
   # TODO: When tom writes the part that returns details from a key, you can make this function better.
    def create_email_message(self, diff_list, new_resultsList):
        message = "Hello Dear Lea Stolowicz\n" #self.user.nickname() + "!\n"
        #message = ""
        message = message + "This is a new update on your follow named: LALALA" #+ self.follow_name + "\n"
        message = message + "There are " + str(len(diff_list)) + " new articles: \n\n"
        
        # create list of new articels: 
        new_articles_list = []
        for article in new_resultsList:
            if (new_resultsList.count(article.get_key()) != 0):
                new_articles_list.append(article)
                
        for article in new_articles_list:
            for article_URLandTitle in article.get_HTML_urlList():
                message = message + "Article Title: " + article_URLandTitle.get_article_title() + "\n\n"
                if article_URLandTitle.get_has_link():
                    message = message + article_URLandTitle.get_article_url()
            message = message + "\t\t****************************************\n\n"
        
        message = message + "To remove this follow please press HERE\n\n"
        message = message + "This update brought to you by RESEARCH ASSISTANT\n"
        
        mail.send_mail(sender="Research Assistant Team <lea.stolo@gmail.com>",
                      to="lea.stolo@gmail.com", #self.user.email(),
                      subject="You Have a new Scholar Update!",
                      body=message)
        #print message
        return message

        