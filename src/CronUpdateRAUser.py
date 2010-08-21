from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import wsgiref.handlers
import RA_User


# go over all labels in DB, and update all fields:
#        if new user - create one: user = db.UserProperty()
#        list_of_labeled_article_keys = db.StringListProperty()
class CronUpdateRAUserTable(webapp.RequestHandler):
    def get(self):
        all_users_article_sets_dict = {}
        try:
            query_labels = db.GqlQuery("SELECT * FROM Label")
            for label in query_labels:
                for user in label.users_list:
                    if user in all_users_article_sets_dict.keys():
                        if (not label.article_key in all_users_article_sets_dict[user]):
                            all_users_article_sets_dict[user].append(label.article_key)
                    else:
                        all_users_article_sets_dict[user] = [label.article_key]
            
            query_RA_User = db.GqlQuery("SELECT * FROM RA_User")
            
            users_RA_Users_dict = {}   
            for ra_user in query_RA_User:
                users_RA_Users_dict[ra_user.user] = ra_user
            
            for user in all_users_article_sets_dict.keys():
                if user in users_RA_Users_dict.keys():
                    curr_ra_user = users_RA_Users_dict[user]
                    curr_ra_user.list_of_labeled_article_keys = all_users_article_sets_dict[user]
                else: 
                    curr_ra_user = RA_User.RA_User()
                    curr_ra_user.user = user
                    curr_ra_user.friends_emails = []
                    curr_ra_user.list_of_labeled_article_keys = all_users_article_sets_dict[user]
                    curr_ra_user.list_of_suggested_article_keys = []
                
                curr_ra_user.put()
    
        except Exception:
            return -7
        return True

application = webapp.WSGIApplication([('/update_ra_user_table_cron', CronUpdateRAUserTable)], 
                                      debug=True)
def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
