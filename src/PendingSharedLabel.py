from google.appengine.ext import db
from google.appengine.api import users 
from google.appengine.ext import webapp
import Label
import HTMLparser


class PendingSharedLabel(db.Model):
        inviting_user = db.UserProperty()
        invited_user = db.UserProperty()
        label_name = db.StringProperty()
        time_mail_sent = db.DateTimeProperty(auto_now_add=True)
        Id = db.StringProperty() # this will actually be the key to the DB
        

# RC = -2 == email address not valid
# RC = -3 == new_user already has this label
# RC = -4 == no results where found  
# RC = -5 == too many results
# RC = -7 == no connection to DB
        
def get_single_pending(invited_user, pending_id):
    query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 "+
                    "AND pending_id = :2 ", 
                    invited_user, pending_id)
    
    num_results = query.count(10)
    if (num_results > 1):
        return -5 
    if (num_results == 0):
        return -4
    return query.fetch(2)[0]

def get_all_users_PendingSharedLabel(user):
    try:
        query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 ",user) 
        pending_list = []   
        for pending_label in query:
            pending_list.append(pending_label)
        return pending_list
    except Exception:
        return -7

def remove_PendingSharedLabel(invited_user, pending_id):
    try:
        query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 " + 
                            "AND Id = :2",
                            invited_user, pending_id)
        count = 0
        for dbfollow in query:
            dbfollow.delete()
            count += 1
        return 0
    except Exception:
        return -7


    
# RC = -4 == no results where found for label_name and user
def acceptPendingSharedLabel(invited_user, pending_id):
    try:
        query = db.GqlQuery("SELECT * FROM PendingSharedLabel WHERE invited_user = :1 "+ 
                        "AND Id = :2 ", 
                        invited_user, pending_id)
    except Exception:
        return -7   
     
    num_results = query.count(10)
    if (num_results == 0):
        return -4
    for pending_obj in query:
        rc = Label.execute_label_sharing_after_approved(pending_obj.inviting_user,pending_obj.label_name,pending_obj.invited_user)
        if (rc != True):
            return rc
        try:
            pending_obj.delete()
        except Exception:
            return -7
        
    return 0
    
# RC = -3 == new_user already has this label
# RC = -4 == no results where found  
# RC = -5 == too many results
# RC = -6 == inviter_user has no label with the name label_name
def pending_share_preview_as_HTMLparser(invited_user, pending_id):
    pending_obj = get_single_pending(invited_user, pending_id)
    if not isinstance(pending_obj, PendingSharedLabel):
        return pending_obj
    
    article_objects_list = Label.get_articles_list_with_label(pending_obj.inviting_user, pending_obj.label_name)
    if (article_objects_list == -3):
        return -3
    if (article_objects_list == -4):
        return -6
    
    html_parser = HTMLparser.HTMLparser(url=None, html=None)
    html_parser.results =  article_objects_list
    html_parser.numOfResults = len(article_objects_list)
    return html_parser
    
    