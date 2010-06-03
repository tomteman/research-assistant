from google.appengine.ext import db
import pickle
import ArticleData
from google.appengine.api import users 
from google.appengine.api import mail
from django.utils import simplejson
import JSONConvertors
import HTMLparser

class Label(db.Model):
     users_list = db.ListProperty(users.User) 
     label_name = db.StringProperty()
     comment  = db.TextProperty()
     serialized_article  = db.TextProperty()
     article_key = db.StringProperty()
     is_shared = db.BooleanProperty()
    
def update_comment(user, label_name, article_key, comment_content):
    pass

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

# Input: user and json object that is a list [article_obj, label_name]
def add_label_JSON_INPUT(user, json_article_labelname_list):
    my_list = simplejson.loads(json_article_labelname_list)
    label_name = my_list[1]
    article_json_string = my_list[0]
    
    article_data_decoder = JSONConvertors.ArticleDataDecoder()
    article_data_obj = article_data_decoder.decode(article_json_string)     # """{"HTML_urlList":[{"articleTitle":"Supercoil sequencing: a fast and simple method for sequencing plasmid <b>DNA</b>","articleURL":"http://www.liebertonline.com/doi/abs/10.1089/dna.1985.4.165","hasLink":true}],"BibTex_dict":{},"related_articlesID":"lar?q=related:S5jpm321qq0J:scholar.google.com/&amp;hl=en&amp;as_sdt=200","HTML_author_year_pub":"EY CHEN, PH Seeburg - <b>DNA</b>, 1985 - liebertonline.com","cacheID":"","related_articlesURL":"http://scholar.google.com/scholar?q=related:lar?q=related:S5jpm321qq0J:scholar.google.com/&amp;hl=en&amp;as_sdt=200:scholar.google.com/&hl=en&num=10&as_sdt=2000","all_versionsURL":"http://scholar.google.com/scholar?cluster=12514014065693661259&hl=en&num=10&as_sdt=2000","HTML_abstract":"%3Cbr%3E%3Cb%3E...%3C%2Fb%3E%20LABORATORY%20METHODS%20Supercoil%20Sequencing%3A%20A%20Fast%20and%20Simple%20Method%20for%20Sequencing%3Cbr%3E%0A%0APlasmid%20%3Cb%3EDNA%3C%2Fb%3E%20ELLSON%20Y.%20CHEN%20and%20PETER%20H.%20SEEBURG%204%5CBSTRACT%20A%20method%20for%20obtaining%3Cbr%3E%0Asequence%20information%20directly%20from%20plasmid%20%3Cb%3EDNA%3C%2Fb%3E%20is%20presented.%20The%20procedure%20in-%20%3Cb%3E...%3C%2Fb%3E%20%0A%3Cbr%3E","all_versionsID":"12514014065693661259","BibTexURL":"http://scholar.google.com/scholar.bib?q=info:S5jpm321qq0J:scholar.google.com/&output=citation&hl=en&as_sdt=2000&ct=citation&cd=0","articleTitleQuoted":"Supercoil+sequencing%3A+a+fast+and+simple+method+for+sequencing+plasmid+%3Cb%3EDNA%3C%2Fb%3E","key":"S5jpm321qq0J","citationsURL":"http://scholar.google.com/scholar?cites=12514014065693661259&hl=en&num=10&as_sdt=2000","articleTitle":"Supercoil sequencing: a fast and simple method for sequencing plasmid <b>DNA</b>","citationsID":"12514014065693661259","articleURL":"http://www.liebertonline.com/doi/abs/10.1089/dna.1985.4.165","cacheURL":"","citationsNUM":"1932"}""")
    article_data_obj_list = [article_data_obj]
    add_label(label_name, user, article_data_obj_list)
    
    

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
        
   

    
