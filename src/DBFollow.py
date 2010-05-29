from google.appengine.api import mail
from google.appengine.ext import db
import Follow
import pickle
import HTMLparser
#import ResearchExceptions
import GeneralFuncs
import datetime

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
    pastResultsKeysList = db.StringListProperty()
    url = db.TextProperty()
    #num_of_articles_added_last_update = db.IntegerProperty()
    total_num_of_articles = db.IntegerProperty()
    
    def convert2Follow(self):
    
        new_follow = Follow.Follow()
        new_follow.user = self.user
        if (self.user != None):
            new_follow.user_nickname = self.user.nickname()
        new_follow.user_id = self.user_id
        new_follow.follow_name = self.follow_name
        new_follow.search_params = pickle.loads(str(self.search_params_str))  # db.TextProperty()
        new_follow.update_frequency = self.update_frequency #db.StringProperty(choices=set(["daily","weekly","monthly"]))
        new_follow.num_of_update_requests = self.num_of_update_requests #db.IntegerProperty()
        new_follow.num_of_meaningful_updates = self.num_of_meaningful_updates #db.IntegerProperty()
        new_follow.time_first_created = self.time_first_created
        new_follow.time_last_updated = self.time_last_updated
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
            email_message = self.create_email_message(diff_list, new_resultsList, diff_list)
            
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
    
    def create_email_message(self, diff_list, all_resultsList, diff_keys_list):
        html_msg = "<html><body>"
        plain_msg = ""
        plain_msg = "Hello Dear Lea Stolowicz,\n" #self.user.nickname() + "!\n"
        html_msg = html_msg + "<b>Hello Dear " + self.user.nickname() + "</b><br>"
        #plain_msg = ""
        plain_msg = plain_msg + "There is a new update on your follow named: \n" + self.follow_name + "\n"
        html_msg = html_msg + "There are " + str(len(diff_list)) + " new articles on your follow&trade; named: <br><b>" + self.follow_name + "</b><br><br><br>"
        plain_msg = plain_msg + "There are " + str(len(diff_list)) + " new articles: \n\n"
        
        # create dictionary of new articles to report
        tmp_dict = {}
        for article in all_resultsList:
            tmp_dict[article.get_key()] = article
        
        count = 0
        for key in diff_keys_list:
            if (count < 50):
                count +=1
                article = tmp_dict[key]
                plain_msg = plain_msg + "\n" + unicode(article.get_article_title(), "utf-8") + "\n\n"
                if (len(article.get_article_url()) > 0):
                    plain_msg = plain_msg + article.get_article_url() + "\n\n"
                plain_msg = plain_msg + "\t\t****************************************\n\n"
                
                if (len(article.get_article_url()) > 0):
                    html_msg = html_msg + "<a href =\"" + article.get_article_url() +""""<font color="6633cc">""" + unicode(article.get_article_title(), "utf-8") + "</font></a><br>"
                else: 
                    html_msg = html_msg + """<b><font color="#6633cc">""" + unicode(article.get_article_title(), "utf-8") + "</b></font><br>"
                html_msg = html_msg + """<font color="#00cc66">""" + unicode(article.get_HTML_author_year_pub(), "utf-8") + "</font>"
                #html_msg = html_msg + unicode(article.get_HTML_abstract(),errors='replace') + "<br>"
                html_msg = html_msg + unicode(article.get_HTML_abstract(),"utf-8") + "<br>"
                
                html_msg = html_msg + """<hr size="3" width="100%" align="left" color="009999"></hr><br>"""
        
        plain_msg = plain_msg + "To remove this follow please press HERE\n\n"
        plain_msg = plain_msg + "This update brought to you by RESEARCH ASSISTANT\n"
        
        html_msg = html_msg + "To remove this follow please press HERE<br><br>"
        html_msg = html_msg + "&copy; This update brought to you by <a href=http://research-assistant.appspot.com/> RESEARCH ASSISTANT</a><br>"
        
        
        
        html_msg = html_msg + "</body></html>"
        mail.send_mail(sender="Research Assistant Team <tau.research.assistant@gmail.com>",
                      to=self.user.email(),
                      subject="You Have a new Scholar Update!",
                      body=plain_msg, 
                      html=html_msg)
        #print plain_msg
        return plain_msg

def get_all_users_dbfollows(user):
    query = db.GqlQuery("SELECT * FROM DBFollow WHERE user = :1 ",user) 
    dbfollows_list = []
    for dbfollow in query:
        dbfollows_list.append(dbfollow)
    return dbfollows_list

def remove_DBFollow(user, follow_name):
    query = db.GqlQuery("SELECT * FROM DBFollow WHERE user = :1 " + 
                        "AND follow_name = :2",
                        user, follow_name)
    count = 0
    for dbfollow in query:
        dbfollow.delete()
        count += 1
    return count

        #if self.is_saved():
        #    self.delete()
        