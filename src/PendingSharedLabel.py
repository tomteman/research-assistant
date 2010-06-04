from google.appengine.ext import db
from google.appengine.api import users 
from google.appengine.ext import webapp
import Label

class PendingSharedLabel(db.Model):
        inviting_user = db.UserProperty()
        invited_user = db.UserProperty()
        invited_user_email_addr = db.StringProperty()
        label_name = db.StringProperty()
        time_mail_sent = db.DateTimeProperty(auto_now_add=True)
        Id = db.StringProperty() # this will actually be the key to the DB
        
        
def get_single_pending(invited_user, pending_id):
    query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 "+
                    "AND pending_id = :2 ", 
                    invited_user, pending_id)
    
    num_results = query.count(10)
    if (num_results > 1):
        return -4 
    if (num_results == 0):
        return -5
    return query.fetch(2)[0]

def get_all_users_PendingSharedLabel(user):
    query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 ",user) 
    pending_list = []   
    for pending_label in query:
        pending_list.append(pending_label)
    return pending_list

def remove_PendingSharedLabel(invited_user, pending_id):
    query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 " + 
                        "AND Id = :2",
                        invited_user, pending_id)
    count = 0
    for dbfollow in query:
        dbfollow.delete()
        count += 1
    return count


    
# RC = -4 == no results where found for label_name and user
def acceptPendingSharedLabel(invited_user, pending_id):
    query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 "+ 
                    "AND Id = :2 ", 
                    invited_user, pending_id)
    
    num_results = query.count(10)
    if (num_results == 0):
        return -4
    for pending_obj in query:
        rc = Label.execute_label_sharing_after_approved(pending_obj.inviting_user,pending_obj.label_name,pending_obj.invited_user)
        if (rc != True):
            return rc
        pending_obj.delete()
    return True
    