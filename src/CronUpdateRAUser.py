from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import wsgiref.handlers
import RA_User
from Suggestions import *
import Label


# go over all labels in DB, and update all fields:
#        if new user - create one: user = db.UserProperty()
#        list_of_labeled_article_keys = db.StringListProperty()
class CronUpdateRAUserTable(webapp.RequestHandler):
    def get(self):
        all_users_article_sets_dict = {}
        self.fill_all_users_article_sets_dict_from_label_table(all_users_article_sets_dict)
        self.update_RA_User(all_users_article_sets_dict)
        self.create_suggestions_for_users(all_users_article_sets_dict)
        
        
    
    def fill_all_users_article_sets_dict_from_label_table(self, all_users_article_sets_dict):        
        query_labels = db.GqlQuery("SELECT * FROM Label")
        for label in query_labels:
            for user in label.users_list:
                if user in all_users_article_sets_dict.keys():
                    if (not str(label.article_key) in all_users_article_sets_dict[user]):
                        all_users_article_sets_dict[user].add(str(label.article_key))
                else:
                    all_users_article_sets_dict[user] = set()
                    all_users_article_sets_dict[user].add(str(label.article_key))
                        
        return True
    
    def update_RA_User(self, all_users_article_sets_dict):    
        query_RA_User = db.GqlQuery("SELECT * FROM RA_User")
        
        users_RA_Users_dict = {}   
        for ra_user in query_RA_User:
            users_RA_Users_dict[ra_user.user] = ra_user
        
        for user in all_users_article_sets_dict.keys():
            if user in users_RA_Users_dict.keys():
                curr_ra_user = users_RA_Users_dict[user]
                curr_ra_user.list_of_labeled_article_keys = list(all_users_article_sets_dict[user])
            else: 
                curr_ra_user = RA_User.RA_User()
                curr_ra_user.user = user
                curr_ra_user.friends_emails = []
                curr_ra_user.list_of_labeled_article_keys = list(all_users_article_sets_dict[user])
                curr_ra_user.list_of_suggested_article_keys = []
            
            curr_ra_user.put()
        return True
    
    def create_suggestions_for_users(self, all_users_article_sets_dict):
        for user in all_users_article_sets_dict.keys():
            sugg_mec = Suggestion_mechanism(user, all_users_article_sets_dict)
            sugg_mec.create_and_upload_all_relevant_suggestions_to_DB()
        
        return True
            
application = webapp.WSGIApplication([('/update_ra_user_table_cron', CronUpdateRAUserTable)], 
                                      debug=True)
def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
