from google.appengine.ext import webapp
from google.appengine.api import users
import Label

class GetAllLabels(webapp.RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        if (self.request.get('Type') == 'All'):
            str = Label.get_label_object_list_for_user_JSON(user)
            #str = """[ {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "lea label", "article_key": "S5jpm321qq0J"}, {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "new roman label", "article_key": "JY7LVcMdJO8J"}, {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "lea label", "article_key": "JY7LVcMdJO8J"}]"""
            self.response.out.write(str)
        elif (self.request.get('Type') == 'Unique'):
            str = Label.get_labels_dict_JSON(user)
            #str = """[{"label_name": "new roman label", "number": "1"}, {"label_name": "lea label", "number": "2"}]"""
            self.response.out.write(str)
            
            
class UpdateLabelDB(webapp.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        Label.add_label_JSON_INPUT(user,self.request.body)
        
        
class UpdateArticleLabelDB(webapp.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        article_key = self.request.get('article_key')
        comment_content =self.request.get('comment_content')
        Label.update_comment(user, label_name, article_key, comment_content)

class RemoveLabelDB(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        label_name = self.request.get('label_name')
        article_key = self.request.get('article_key')
        Label.remove_label_from_article(user, label_name, article_key)
        
        
        
        
        
        
        
        
        
        