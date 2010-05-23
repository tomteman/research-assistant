from google.appengine.ext import db
import pickle
import ArticleData
from google.appengine.api import users 
from google.appengine.api import mail

class Label(db.Model):
     users_list = db.ListProperty(users.User) 
     label_name = db.StringProperty()
     Comment  = db.TextProperty()
     serialized_article  = db.TextProperty()
     article_key = db.StringProperty()
     is_shared = db.BooleanProperty()
    
 

def add_label(label_name, user,list_of_articleData_objects):
    # TODO: should we check that this label does not exist already?
    # because if we dont check, user can add twice, and when he removes it will 
    # not be removed
    for article in list_of_articleData_objects:
        new_label = Label()
        new_label.label_name = label_name
        new_label.users_list = [user]
        new_label.comment = ""
        new_label.serialized_article = pickle.dumps(article)
        new_label.article_key = article.key
        new_label.is_shared = False
        new_label.put()
    return True
    
    

def get_labels_dict(user):
    q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1", user)
    labels_list = q.fetch(1000)
    new_dict = {}
    for label in labels_list:
        if (new_dict[label.label_name] == None):
            new_dict[label.label_name] = 1
        else:
            new_dict[label.label_name] += 1
    return new_dict
         
    pass
def remove_label_from_article(user, label_name,article_key):
    q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 " +
                    "AND article_key = :3", 
                    user, label_name, article_key)
    results = q.fetch(10)
    db.delete(results)
    
def delete_label(user,label_name):
    q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
    results = q.fetch(1000)
    db.delete(results)

def rename_label(user,old_label_name, new_label_name):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, old_label_name)
    # here I am assuming there in only one label with this name for this user
    for label_object in query:
        label_object.label_name = new_label_name
        label_object.put()
    
def share_label(user,label_name, new_users_list, notify=True):
    # get the current label object
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
    label_object = query.fetch(1000)
    for label_object in query:
        label_object.is_shared = True
        for new_user in new_users_list:
            if new_user not in label_object.users_list:
                label_object.users_list.append(new_user)
                if notify:
                    notify_user_on_shared_label(user, new_user, label_name)
        label_object.put()
   
def notify_user_on_shared_label(old_user, new_user, label_name):
    # is this user first time in ResearchAssistant (is not in DB)
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    new_user, label_name)
    
    html_msg = "<html><body>"
    html_msg = html_msg + "<b>Hello Dear " + new_user.nickname() + "</b><br><br>"
    html_msg = html_msg + "<b>" + old_user.nickname() + "</b> has shared with you a ResearchAssistant Label named: <b>" + str(label_name) +  "</b><br>"
    html_msg = html_msg + "here comes a link to the label<br><br>"
    html_msg = html_msg + "If you are new to ResearchAssitant, we invite you to visit our site and view a short video "
    html_msg = html_msg + "<a href =\"research-assistant.appspot.com/\" <font color=\"6633cc\"> here" + "</font></a><br>"
    html_msg = html_msg + "&copy; brought to you by <a href=http://research-assistant.appspot.com/> RESEARCH ASSISTANT</a><br>"
    html_msg = html_msg + "</body></html>"
    plain_msg = "Hello Hello"
    mail.send_mail(sender="Research Assistant Team <tau.research.assistant@gmail.com>",
                  to=new_user.email(),
                  subject="A new Research Assistant Label was shared with you",
                  body=plain_msg, 
                  html=html_msg)
    # create dictionary of new articles to report
  
    
def get_articles_list_with_label(user,label_name):
     query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
     article_objects_list = []
     for label_object in query:
        article_objects_list.append(pickle.loads(str(label_object.serialized_article)))
     
     return article_objects_list
 
def get_articles_keys_list_with_label(user,label_name):
     query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
     article_keys_list = []
     for label_object in query:
         article = pickle.loads(str(label_object.serialized_article))
         article_keys_list.append(article.key)
     
     return article_keys_list

def get_number_of_articles_with_label(user, label_name):
    pass
    #def Add_comment???


    
