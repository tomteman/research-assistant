from google.appengine.ext import db
import pickle
import ArticleData
from google.appengine.api import users 
from google.appengine.api import mail
from django.utils import simplejson
import JSONConvertors
import HTMLparser
import PendingSharedLabel
import RA_User
import string
import urllib
import sys

# RC = -2 == email address not valid
# RC = -3 == new_user already has this label
# RC = -4 == no results where found for label_name and user 
# RC = -7 == no connection to DB
# creates a pending in the DB
def force_utf8(string):
    if type(string) == str:
        return string
    return string.encode('utf-8')

def force_unicode(string):
    if type(string) == unicode:
        return string
    return string.decode('utf-8')
class Label(db.Model):
    users_list = db.ListProperty(users.User) 
    label_name = db.StringProperty()
    comment  = db.TextProperty()
    serialized_article  = db.TextProperty()
    article_key = db.StringProperty()
    is_shared = db.BooleanProperty()
    creator = db.UserProperty()
    article_abstract_title_author = db.StringProperty(multiline=True)
    
# returns False on failure
def update_comment(user, label_name, article_key, comment_content):
    try:
        query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 " +
                        "AND article_key = :3", 
                        user, label_name, article_key)
        # results = q.fetch(10)
        # this is supposed to be only one result but who knows...
        for label in query:
            label.comment = str(comment_content)
            label.put()
    except Exception:
        return -7
    return 1
    

def add_label_to_article(label_name, user,list_of_articleData_objects):
    # check if label exists. 
    # if not, update the creator. if yes, take his name
    try:
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

            s = unicode(pickle.dumps(article), errors='ignore')
            new_label.serialized_article = db.Text(s)
           # new_label.serialized_article = pickle.dumps(article)
            
            
            title = force_utf8(article.get_article_title()) 
            abstract = force_utf8(article.get_HTML_abstract()) 
            author_year = force_utf8(article.get_HTML_author_year_pub())
            temp = title + abstract + author_year
            
            temp_utf = force_utf8(temp)    
            temp_trunc = temp_utf[:500]  
              
            se = unicode(temp_trunc, errors='ignore')
            new_label.article_abstract_title_author = se
            #new_label.article_abstract_title_author = "asas"
            new_label.article_key = article.key
#            
            if is_new_label:
                new_label.users_list = [user]
                new_label.creator = user
                new_label.is_shared = False
            else: 
                new_label.users_list = users_list
                new_label.is_shared = is_shared
                new_label.creator = creator
            new_label.put()
            
    except Exception:
        msg = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
        return msg # str(type(temp))
        #return -7

        
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
    try:
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
        
        label_names_list = num_dict.keys()
        label_names_list.sort(key=string.lower)
        final_list = []
        for labelname in label_names_list:
            d = {}
            d['label_name'] = labelname
            d['number'] = num_dict[labelname]
            d['is_shared'] = is_shared_dict[labelname]
            final_list.append(d)
        
        return simplejson.dumps(final_list)
    except Exception:
        return -7
    
    
    
    
         
def remove_label_from_article(user, label_name,article_key):
    try:
        q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 " +
                        "AND article_key = :3", 
                        user, label_name, article_key)
        results = q.fetch(10)
        db.delete(results)
    except Exception:
        return -7
    
def delete_label(user,label_name):
    try: 
        q = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 ", 
                        user, label_name)
        results = q.fetch(1000)
        db.delete(results)
        return 1
    
    except Exception:
        return -7
    
# ASSUMPTIONS: in this function i assume the label_name is of a private label (NOT SHARED)    
def rename_label(user,old_label_name, new_label_name):
    try: 
        query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 ", 
                        user, old_label_name)
        # here I am assuming there in only one label with this name for this user
        for label_object in query:
            label_object.label_name = new_label_name
            label_object.put()
        return True
    except Exception:
        return -7
    

# ASSUMPTIONS: in this function i assume the label_name is of a shared label 
def duplicate_label_to_private(user, label_name):
    # check this label really exists
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
    if (query.count(2) == 0):
        return -4
    
    # determine new label name (choose a name the user doesn't have)
    new_label_name = label_name + "_1"
    while (True):
        temp_query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 ", 
                        user, new_label_name)
        if (temp_query.count(2) == 0):
            break
        new_label_name = new_label_name + "_1"
    for label in query:
        new_label = Label()
        new_label.users_list = [user]
        new_label.label_name = new_label_name
        new_label.comment = label.comment
        new_label.serialized_article = label.serialized_article
        new_label.article_key = label.article_key
        new_label.is_shared = False
        new_label.creator = user
        new_label.article_abstract_title_author = label.article_abstract_title_author
        try:
            new_label.put()
        except Exception:
            return -7
    return new_label_name
    
    
    
def get_articles_list_with_label(user,label_name):
    try:
        query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 ", 
                        user, label_name)
        article_objects_list = []
        for label_object in query:
            article_objects_list.append(pickle.loads(str(label_object.serialized_article)))
    except Exception:
        return -7
    return article_objects_list
 
#####
## This function is called when user presses a certain label
## and then he gets all the articles he has tagged on that label
####
#def get_articles_list_with_label_as_HTMLParser_JSON(user, label_name):
#    article_objects_list = get_articles_list_with_label(user, label_name)
#    if (type(article_objects_list) == "int"):
#        return article_objects_list
#    
#    html_parser = HTMLparser.HTMLparser(url=None, html=None)
#    html_parser.results =  article_objects_list
#    html_parser.numOfResults = len(article_objects_list)
#    
#    my_htmlparser_encoder = JSONConvertors.HTMLparserEncoder()
#    as_json =my_htmlparser_encoder.encode(html_parser)
#    
#    return as_json

def get_articles_list_with_label_as_HTMLParser(user, label_name):
    article_objects_list = get_articles_list_with_label(user, label_name)
    if (type(article_objects_list) is int):
        return article_objects_list
    
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

def get_list_of_label_users(user,label_name):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    user, label_name)
    if (query.count(2) == 0 ):
        return -4
    else:
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
# RC = -3 == new_user already has this label, notify inviting user that the invited user has a shared label of the same name
# RC = -4 == no results where found for label_name and user
# RC = -6 ==  the user is trying to share some thing with himself
# RC = -7 == problems connecting to db
# creates a pending in the DB
def share_label_request(inviting_user, label_name, invited_user_email, notify=True):
    # Varify new_user_email
    if (inviting_user.email() == invited_user_email):
        return -6
    
    if not mail.is_email_valid(invited_user_email):
        return -2
    invited_user = users.User(invited_user_email)
    # check if this label really exists at the inviting user
    query_inviting = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    inviting_user, label_name)
    
    num_results = query_inviting.count(10)
    if (num_results == 0):
        return -4
    
    # check if the invited user already has a label with the same name that is shared
    query_invited = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2 ", 
                    invited_user, label_name)    
    if (query_invited.count(1) != 0):
        one_label_object = query_invited.fetch(2)[0]
        if ((invited_user in one_label_object.users_list) and (one_label_object.is_shared == True)):
                return -3 
    
    # create pending in DB and notify the invited user
    pending_obj = PendingSharedLabel.PendingSharedLabel()
    pending_obj.inviting_user = inviting_user
    pending_obj.invited_user = invited_user
    pending_obj.label_name= label_name
    Id = inviting_user.nickname()+":" + invited_user.nickname() + ":" +label_name
    pending_obj.Id = Id
    try:
        key = pending_obj.put()
    except Exception:
        return -7
    
    if notify:
        return notify_user_on_shared_label(inviting_user, invited_user, label_name, key)
    
    return 1
    
# RC = -4 == no results where found for label_name and user
def execute_label_sharing_after_approved(inviting_user,label_name, invited_user):
    # check if the invited user already has a label with the same name
    # if yes, and that label is private - rename it
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                "AND label_name = :2 ", 
                invited_user, label_name)
    
    if (query.count(2) != 0):
        label = query.fetch(1000)[0]
        if (label.is_shared == False):
            rename_label(invited_user, label.label_name, label.label_name + "_1")
    
    # get the current label object
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                "AND label_name = :2 ", 
                inviting_user, label_name)

    labels = query.fetch(1000)
    if ((labels == None) or (len(labels)== 0)):
        return -4
    
    count_labels_added = 0
    for label_object in labels:
        if not invited_user in label_object.users_list:
            label_object.is_shared = True
            label_object.users_list.append(invited_user)
            try:
                label_object.put()
                count_labels_added += 1
            except Exception: 
                return -7
            
    
    return count_labels_added
   
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
    html_msg = html_msg + """<a href =\"http://research-assistant.appspot.com/?page=ShowPendings\" <font color=\"6633cc\">this link</font></a><br>"""
    if (is_new_user):
        html_msg = html_msg + "<i>(If you do not have a Google account, you will be prompted to create one)</i><br>"
 
    
    if (is_new_user):
        html_msg = html_msg + get_html_message_for_new_user()
    
    html_msg = html_msg + """<br><hr size="3" width="100%" align="left" color="009999"></hr><br>"""
    html_msg = html_msg + "<br>&copy; brought to you by <a href=http://research-assistant.appspot.com/> Research Assistant</a><br>"
    html_msg = html_msg + "</body></html>"
    plain_msg = "Hello Hello"
    try: 
        mail.send_mail(sender="Research Assistant Team <tau.research.assistant@gmail.com>",
                      to=new_user.email(),
                      subject=old_user.nickname() + " has shared a Research Assistant Label with you",
                      body=plain_msg, 
                      html=html_msg)
    except Exception:
        return -8
    return  1
        

# ASSUMPTIONS: in this function i assume the label_name is of a shared label 
def get_emails_of_users_on_this_shared_label(user, label_name):
    try:
        query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                    "AND label_name = :2",  
                     user, label_name)
    except Exception:
        return -7
    
    if (query.count(2) == 0):
        return -4
    label = query.fetch(2)[0]
    emails_str = ""
    for user_obj in label.users_list:
        emails_str = emails_str + str(user_obj.email()) + "<br>"
    
    return emails_str  

# ASSUMPTIONS: in this function i assume the label_name is of a shared label 
def remove_user_from_shared_label(user, label_name):
    try:
        query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                   "AND label_name = :2",  
                   user, label_name)
    except Exception:
        return -7
    if (query.count(1) == 0):
        return -4
    
    # check in case this is the last user on this label
    label = query.fetch(2)[0]
    if (len(label.users_list) == 1): # last user on this Label. 
        for label in query:
            try:
                label.remove()
            except Exception:
                return -7
    # this is not the last user, but after remove, there is only one more user 
    # so this will no longer be a shared label
    elif (len(label.users_list) == 2): 
        for label in query:
            label.users_list.remove(user)
            label.is_shared = False
            try:
                label.put()
            except Exception:
                return -7
    # this is not the last user, and after removing him there are still more users.
    # so this stays shared
    else: 
        for label in query:
            label.users_list.remove(user)
            try:
                label.put()
            except Exception:
                return -7
    return 1    
    
#####################################
######### SEARCH IN LABEL ###########
#####################################

def search_in_labels_return_HTMLparser(user, label_name, search_term):
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                "AND label_name = :2",  
                user, label_name)
    
    article_objects_list = []
    for label_object in query:
        if (label_object.article_abstract_title_author.lower().find(search_term.lower())  != -1):
            article_objects_list.append(pickle.loads(str(label_object.serialized_article)))
    
    html_parser = HTMLparser.HTMLparser(url=None, html=None)
    html_parser.results =  article_objects_list
    html_parser.numOfResults = len(article_objects_list)
    
    return html_parser

def search_in_labels_return_HTMLparser_JSON(user, label_name, search_term):
    plain_msg = ""
    query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                "AND label_name = :2",  
                user, label_name)
    
    article_objects_list = []
    for label_object in query:
        if (label_object.article_abstract_title_author.lower().find(search_term.lower())  != -1):
            article_objects_list.append(pickle.loads(str(label_object.serialized_article)))
    
    html_parser = HTMLparser.HTMLparser(url=None, html=None)
    html_parser.results =  article_objects_list
    html_parser.numOfResults = len(article_objects_list)
    
    my_htmlparser_encoder = JSONConvertors.HTMLparserEncoder()
    as_json = my_htmlparser_encoder.encode(html_parser)
    
    return as_json


def get_label_by_email(sending_user, target_user_email, label_name):
    new_user = users.User(target_user_email)
    plain_msg = " "
    try: 
        ## GET ALL ARTICLED
        query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                        "AND label_name = :2 ", 
                        sending_user, label_name)
        article_objects_list = []
        for label_object in query:
            article_objects_list.append(pickle.loads(str(label_object.serialized_article)))
    
        # PREFIX
        html_msg = "<html><body>"
        html_msg = html_msg + "<b>Hello Dear " + str(target_user_email) + ",</b><br>"
        html_msg = html_msg + "Following are all articles labeled by " + sending_user.nickname() + " as \""
        html_msg = html_msg + "<font color=\"red\" ><b>" + str(label_name) +  "</b></font>\"</br><br><br><br>"
        
    
        # BUILD CONTENT
        for article_obj in article_objects_list:
            if (len(article_obj.get_article_url()) > 0):
                html_msg = html_msg + "<a href =\"" + article_obj.get_article_url() +""""<font color="6633cc">""" + article_obj.get_article_title() + "</font></a><br>"
            else: 
                html_msg = html_msg + """<b><font color="#6633cc">""" + article_obj.get_article_title() + "</b></font><br>"
            html_msg = html_msg + """<font color="#00cc66">""" + article_obj.get_HTML_author_year_pub() + "</font>"
            html_msg = html_msg + article_obj.get_HTML_abstract() + "<br>"
            html_msg = html_msg + """<hr size="3" width="100%" align="left" color="009999"></hr><br>"""
    
    
        # JUST FOR NEW USERS
        is_new_user = is_new_user_to_RA(new_user)
        if (is_new_user):
            html_msg += get_html_message_for_new_user()
        
        html_msg = html_msg + "<br>&copy; brought to you by <a href=http://research-assistant.appspot.com/> Research Assistant</a><br>"
        html_msg = html_msg + "</body></html>"
        
        # SEND MESSAGE
        mail.send_mail(sender="Research Assistant Team <tau.research.assistant@gmail.com>",
                  to=new_user.email(),
                  subject="Articles labeled by " + sending_user.nickname() + " as \"" + label_name + "\"", 
                  body=plain_msg, 
                  html=html_msg)
    except Exception: 
        msg = "bla"
        msg = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
        return msg
    
    return True


def get_html_message_for_new_user():
    html_msg = ""
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
    return html_msg