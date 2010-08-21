from google.appengine.ext import db
from google.appengine.api import users 
from google.appengine.ext import webapp


class RA_User(db.Model):
        user = db.UserProperty()
        friends_emails = db.StringListProperty()
        last_time_updated_suggestions = db.DateTimeProperty()
        list_of_labeled_article_keys = db.StringListProperty()
        list_of_suggested_article_keys = db.StringListProperty()


def get_RA_User_obj(user):
    try:
        query = db.GqlQuery("SELECT * FROM RA_User WHERE user = :1 ", user)
            
        if (query.count(2) == 0):
            return -7
            
        ra_user_obj = query.fetch(2)[0]
        return ra_user_obj
    except Exception:
        return -7


def get_friends_emails_list(user):
    return (get_RA_User_obj(user)).friends_emails
    