from google.appengine.ext import webapp

class GetAllLabels(webapp.RequestHandler):
    
    def get(self):
        if (self.request.get('Type') == 'All'):
            str = """[ {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "lea label", "article_key": "S5jpm321qq0J"}, {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "new roman label", "article_key": "JY7LVcMdJO8J"}, {"comment": "", "is_shared": false, "users_list": [{"user_id": "173248248688531220104", "user_nickname": "lea.stolo", "user_email": "lea.stolo@gmail.com"}], "serialized_article": "moshe levi", "label_name": "lea label", "article_key": "JY7LVcMdJO8J"}]"""
            self.response.out.write(str)
        elif (self.request.get('Type') == 'Unique'):
            str = """[{"label_name": "new roman label", "number": "1"}, {"label_name": "lea label", "number": "2"}]"""
            self.response.out.write(str)
            
            
class UpdateLabelDB(webapp.RequestHandler):
    
    def post(self):
        pass
        #add_label_JSON(users.get_current_user(),self.request.body)
        