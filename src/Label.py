from google.appengine.ext import db
import pickle
import ArticleData
from google.appengine.api import users 
from google.appengine.api import mail
from django.utils import simplejson
import JSONConvertors
import HTMLparser
import PendingSharedLabel

# RC = -2 == email address not valid
# RC = -3 == new_user already has this label
# RC = -4 == no results where found for label_name and user 
# RC = -7 == no connection to DB
# creates a pending in the DB

class Label(db.Model):
    users_list = db.ListProperty(users.User) 
    label_name = db.StringProperty()
    comment  = db.TextProperty()
    serialized_article  = db.TextProperty()
    article_key = db.StringProperty()
    is_shared = db.BooleanProperty()
    creator = db.UserProperty()
    
# returns False on failure
def update_comment(user, label_name, article_key, comment_content):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 " +
                    "AND article_key = :3", 
                    user, label_name, article_key)
    # results = q.fetch(10)
    # this is supposed to be only one result but who knows...
    for label in query:
        label.comment = str(comment_content)
        label.put()
        
    return True
    

def add_label_to_article(label_name, user,list_of_articleData_objects):
    # check if label exists. 
    # if not, update the creator. if yes, take his name
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
    
    if (query.count(2) == 0):
        # true when this is the first time a label for this user is called this way
        is_new_label = True 
    else:
        is_new_label= False
        label = query.fetch(1)[0]
        creator = label.creator
        users_list = label.users_list
        is_shared = label.is_shared
 
    for article in list_of_articleData_objects:
        new_label = Label()
        new_label.label_name = label_name
        new_label.comment = ""
        new_label.serialized_article = pickle.dumps(article)
        new_label.article_key = article.key
        
        if is_new_label:
            new_label.users_list = [user]
            new_label.creator = user
            new_label.is_shared = False
        else: 
            new_label.users_list = users_list
            new_label.is_shared = is_shared
            new_label.creator = creator
        try:
            new_label.put()
        except Exception:
            return -7
        
    return True

# Input: user and json object that is a list [article_obj, label_name]
def add_label_JSON_INPUT(user, json_article_labelname_list):
    my_list = simplejson.loads(json_article_labelname_list)
    label_name = my_list[1]
    article_json_string = my_list[0]
    
    article_data_decoder = JSONConvertors.ArticleDataDecoder()
    article_data_obj = article_data_decoder.decode(article_json_string)     
    article_data_obj_list = [article_data_obj]
    return add_label_to_article(label_name, user, article_data_obj_list)
    
# RC = -4 == no results where found for label_name and user    
def is_shared_label(user, label_name):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 " +
                    user, label_name)
    if (query.count(2) == 0):
        return -4
    else:
        label = query.fetch(1)[0]
        return label.is_shared
        
    
def get_labels_dict_JSON(user):
    q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1", user)
    labels_list = q.fetch(1000)
    num_dict = {}
    is_shared_dict = {}
    for label in labels_list:
        if (num_dict.has_key(label.label_name)):
            num_dict[label.label_name] += 1
        else:
            num_dict[label.label_name] = 1
        
        is_shared_dict[label.label_name] = label.is_shared
    
    final_list = []
    for key, value in num_dict.items():
        d = {}
        d['label_name'] = key
        d['number'] = value
        d['is_shared'] = is_shared_dict[key]
        final_list.append(d)
    
    return simplejson.dumps(final_list)
    
    
    
         
def remove_label_from_article(user, label_name,article_key):
    q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 " +
                    "AND article_key = :3", 
                    user, label_name, article_key)
    results = q.fetch(10)
    db.delete(results)
    
def delete_label(user,label_name):
    try: 
        q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 ", 
                        user, label_name)
        results = q.fetch(1000)
        db.delete(results)
        return True
    
    except Exception:
        return False
    
    
def rename_label(user,old_label_name, new_label_name):
    try: 
        query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 ", 
                        user, old_label_name)
        # here I am assuming there in only one label with this name for this user
        for label_object in query:
            label_object.label_name = new_label_name
            label_object.put()
    except Exception:
        False


  
    
def get_articles_list_with_label(user,label_name):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
    article_objects_list = []
    for label_object in query:
        article_objects_list.append(pickle.loads(str(label_object.serialized_article)))
     
    return article_objects_list
 
#####
## This function is called when user presses a certain label
## and then he gets all the articles he has tagged on that label
####
def get_articles_list_with_label_as_HTMLParser_JSON(user, label_name):
    article_objects_list = get_articles_list_with_label(user, label_name)
    
    html_parser = HTMLparser.HTMLparser(url=None, html=None)
    html_parser.results =  article_objects_list
    html_parser.numOfResults = len(article_objects_list)
    
    my_htmlparser_encoder = JSONConvertors.HTMLparserEncoder()
    as_json =my_htmlparser_encoder.encode(html_parser)
    
    return as_json

def get_articles_list_with_label_as_HTMLParser(user, label_name):
    article_objects_list = get_articles_list_with_label(user, label_name)
    
    html_parser = HTMLparser.HTMLparser(url=None, html=None)
    html_parser.results =  article_objects_list
    html_parser.numOfResults = len(article_objects_list)
    
    return html_parser
    
    
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

def get_list_of_label_users(user,label_name):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
    label = query.fetch(1)[0]
    return label.users_list
    
#####################################

def get_articlekey_labellist_dict(user):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 ", user)
    articlekey_labellist_dict = {}
    for label in query:
        articlekey_labellist_dict[label.article_key] = label
    return articlekey_labellist_dict

def get_label_object_list_for_user_JSON(user):
     query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 ", user)
     my_label_encoder = JSONConvertors.LabelEncoder()
     labellist_JSON  = []
     
     for label in query:
         labellist_JSON.append(my_label_encoder.default(label))
    
     return simplejson.dumps(labellist_JSON)
     
def get_articlekey_labellist_dict_JSON(user):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 ", user)
    
    my_label_encoder = JSONConvertors.LabelEncoder()
    articlekey_labellist_dict_JSON = {}
    
    for label in query:
        articlekey_labellist_dict_JSON[label.article_key] = my_label_encoder.default(label)
        
    return simplejson.dumps(articlekey_labellist_dict_JSON)

###################################
##########3 Sharing Labels:

# RC = -2 == email address not valid
# RC = -3 == new_user already has this label
# RC = -4 == no results where found for label_name and user 
# RC = -7 == problems connecting to db
# creates a pending in the DB
def share_label_request(inviting_user, label_name, new_user_email, notify=True):
    # Varify new_user_email
    if not mail.is_email_valid(new_user_email):
        return -2
    
    # check if this label really exists
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    inviting_user, label_name)
    
    num_results = query.count(10)
    if (num_results == 0):
        return -4
    
    # check if the invited user already has this label
    new_user = users.User(new_user_email)
    one_label_object = query.fetch(2)[0]
    if new_user in one_label_object.users_list:
            return -3 
    
    # create pending in DB and notify the invited user
    pending_obj = PendingSharedLabel.PendingSharedLabel()
    pending_obj.inviting_user = inviting_user
    pending_obj.invited_user = new_user
    pending_obj.label_name= label_name
    Id = inviting_user.nickname()+":" + new_user.nickname() + ":" +label_name
    pending_obj.Id = Id
    try:
        key = pending_obj.put()
    except Exception:
        return -7
    
    if notify:
        notify_user_on_shared_label(inviting_user, new_user, label_name, key)
    return True
    
# RC = -4 == no results where found for label_name and user
def execute_label_sharing_after_approved(old_user,label_name, new_user):
    # get the current label object
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                "AND label_name = :2 ", 
                old_user, label_name)

    labels = query.fetch(1000)
    if ((labels == None) or (len(labels)== 0)):
        return -4
    
    for label_object in labels:
        label_object.is_shared = True
        if not new_user in label_object.users_list:
            label_object.users_list.append(new_user)
            label_object.put()
    
    return True
   
def is_new_user_to_RA(user):
    query1 = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 ", user)
    query2 = db.GqlQuery("SELECT * FROM DBFollow WHERE users_list = :1 ", user)
    if ((query1.count(5) == 0) and (query2.count(5) == 0)):
        return  True
    else:
        return False
    
def notify_user_on_shared_label(old_user, new_user, label_name, key):
    # is this user first time in ResearchAssistant (is not in DB)
#    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
#                    "AND label_name = :2 ", 
#                    new_user, label_name)
#    
    html_msg = "<html><body>"
    html_msg = html_msg + "<b>Hello Dear " + new_user.nickname() + ",</b><br><br>"
    html_msg = html_msg + "<b>" + old_user.nickname() + "</b> has shared a Research Assistant Label with you! <br>"
    html_msg = html_msg + "Label is named: <font color=\"red\" ><b>" + str(label_name) +  "</b></font></br><br>"
    
    is_new_user = is_new_user_to_RA(new_user)
    html_msg = html_msg + "To see the label details and accept/reject press: "
    html_msg = html_msg + """<a href =\"http://research-assistant.appspot.com/?page=MyPendingLabels\" <font color=\"6633cc\">this link</font></a><br>"""
    if (is_new_user):
        html_msg = html_msg + "<i>(If you do not have a Google account, you will be prompted to create one)</i><br>"
 
    
    if (is_new_user):
        html_msg = html_msg + """<br><hr size="3" width="100%" align="left" color="009999"></hr><br>"""
        html_msg = html_msg + "Research Assistant is a new online tool which enables you to keep track on all articles! <br>"
        html_msg = html_msg + "You are welcome to: <br>"
        html_msg = html_msg + "<ul><li> Label articles and write comments on them<br>"
        html_msg = html_msg + "<li>Get email updates on new articles of interest<br>"
        html_msg = html_msg + "<li>Collaborate! - Share Labels with you colleagues<br>"
        html_msg = html_msg + "<li>Search within articles citing a specific article</ul>"
        html_msg = html_msg + "....And much more!<br><br>"
        html_msg = html_msg + "We invite you to visit our site and view a short video "
        html_msg = html_msg + "<a href =\"research-assistant.appspot.com/\" <font color=\"6633cc\"> here" + "</font></a><br><br>"
    
    html_msg = html_msg + """<br><hr size="3" width="100%" align="left" color="009999"></hr><br>"""
    html_msg = html_msg + "<br>&copy; brought to you by <a href=http://research-assistant.appspot.com/> Research Assistant</a><br>"
    html_msg = html_msg + "</body></html>"
    plain_msg = "Hello Hello"
    mail.send_mail(sender="Research Assistant Team <tau.research.assistant@gmail.com>",
                  to=new_user.email(),
                  subject=old_user.nickname() + " has shared a Research Assistant Label with you",
                  body=plain_msg, 
                  html=html_msg)
        
