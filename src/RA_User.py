from google.appengine.ext import db
from google.appengine.api import users 
from google.appengine.ext import webapp


class RA_User(db.Model):
        user = db.UserProperty()
        label_name_to_local_name = db.StringProperty() #serialized dictionary
        local_name_to_label_name = db.StringProperty() #serialized dictionary (opposite to label_name_to_local_name) 
        friends_emails = db.StringListProperty()

# RC = -2 == email address not valid
# RC = -3 == new_user already has this label
# RC = -4 == no results where found  
# RC = -5 == too many results
# RC = -7 == no connection to DB
def get_RA_User_obj(user):
    query = db.GqlQuery("SELECT * FROM RA_User WHERE user = :1 ",user)
    num_res = query.count(10)
    if (num_res == 0):
        return -4
    elif (num_res > 1):
        return -5
    else:
        return query.fetch(1)[0]

def get_friends_emails_list(user):
    return (get_RA_User_obj(user)).friends_emails
    