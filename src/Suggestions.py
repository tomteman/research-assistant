#import itertools
from google.appengine.ext import db
import RA_User
from google.appengine.api import users 
import pickle
import HTMLparser
import sys

###############
# once a day a cron will run the function generate_users_sets_dict
# this function goes over all labels, and creates this dictionary

# than, same cron goes over all users in the system and for each one
# in Table RA_User if last_time_updated_suggestions is over a week ago
# run create_and_upload_all_relevant_suggestions_to_DB

def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield set(pool[i] for i in indices)
        
class Suggestion(db.Model):
    
        user = db.UserProperty()
        suggesting_users_list = db.ListProperty(users.User) 
        
        suggested_article_key = db.StringProperty()
        suggested_serialized_article = db.TextProperty()
        
        is_removed = db.BooleanProperty() 
        rank = db.IntegerProperty()
        
        date_created = db.DateTimeProperty(auto_now_add=True)
        num_users = db.IntegerProperty()
        num_common_articles = db.IntegerProperty() # number of common articles of main_user with suggesting subset
        
        def calculate_rank(self):
            if self.is_removed:
                self.rank =  -1
            
            self.rank = self.num_common_articles + self.num_users
            return self.rank
        
##################################################################
##################################################################
        

class Suggestion_mechanism:
    def __init__(self, main_user, all_users_sets_dict):
        
        self.main_user = main_user
        self.all_users_sets_dict = all_users_sets_dict
        
        self.all_users_sets_dict_no_main_user = {}
        for key, value in all_users_sets_dict.items():
            if (key != main_user):
                self.all_users_sets_dict_no_main_user[key] = value 
            
        
        self.relevant_users_list = None
        self.MIN_NUM_OF_ARTICLES_IN_COMMON_WITH_RELEVANT_USER = 3
        self.MAX_NUM_OF_USER_SUBSET = 10
        self.ra_user_obj = None
        
    
    # returns list of users with at least MIN_NUM_OF_ARTICLES_IN_COMMON_WITH_RELEVANT_USER
    #  articles in common with user
    def create_relevant_users_list(self, main_user):
        main_user_set = self.all_users_sets_dict[self.main_user]
        relevant_users_list = []
        for user, user_set in self.all_users_sets_dict_no_main_user.items():
            common = main_user_set.intersection(user_set)
            if len(common) >= self.MIN_NUM_OF_ARTICLES_IN_COMMON_WITH_RELEVANT_USER:
                # insert this user to relevance list
                relevant_users_list.append(user)
        return relevant_users_list
            
        
        
    def create_and_upload_all_relevant_suggestions_to_DB(self):
       
        self.ra_user_obj = RA_User.get_RA_User_obj(self.main_user)
        current_list_of_suggested_article_keys = self.ra_user_obj.list_of_suggested_article_keys
        
        main_user_set = self.all_users_sets_dict[self.main_user]
        self.relevant_users_list = self.create_relevant_users_list(self.main_user)
        if self.main_user in self.relevant_users_list:
            self.relevant_users_list.remove(self.main_user)
        
        
        for users_subset_size in reversed(range(2, self.MAX_NUM_OF_USER_SUBSET)):
            
            for subset_of_users in combinations(self.relevant_users_list, users_subset_size):

                # common = intersection of articles of main_user and all others in subset
                common_articles_set = self.get_common_article_keys(self.main_user, subset_of_users)
                
                if len(common_articles_set) >= self.MIN_NUM_OF_ARTICLES_IN_COMMON_WITH_RELEVANT_USER:
                    common_article_keys_of_others = self.get_common_article_keys(list(subset_of_users)[0], set(list(subset_of_users)[1:]))
                    
                    if len(common_article_keys_of_others) >=1: 
                            new_articles_to_suggest = common_article_keys_of_others.difference(main_user_set)
                         
                            for sugg_article_key in new_articles_to_suggest:
                                if (not sugg_article_key in current_list_of_suggested_article_keys):
                                    # create a new suggestion          
                                    suggestion = Suggestion()
                                    suggestion.user = self.main_user
                                    suggestion.suggesting_users_list = list(subset_of_users)
                                    suggestion.suggested_article_key = sugg_article_key
                                    suggestion.is_removed = False
                                    suggestion.num_users = users_subset_size
                                    suggestion.num_common_articles = len(common_articles_set)
                                     
                                    suggestion.suggested_serialized_article = get_serialized_article(sugg_article_key,subset_of_users )
                                    if suggestion.suggested_serialized_article == None: 
                                        # could not find this article serialized. probably deleted by all suggesting users
                                        suggestion.delete()
                                        continue
                    
                                    suggestion.suggestion_rank = suggestion.calculate_rank()
                                    current_list_of_suggested_article_keys.append(sugg_article_key)
                                     
                                    try:
                                        suggestion.put()
                                        self.ra_user_obj.list_of_suggested_article_keys = current_list_of_suggested_article_keys
                                        self.ra_user_obj.put()
                                    except Exception:
                                        return -7
        return True
        
    
 
    def update_suggestion(self):
        pass
    
    def get_common_article_keys(self, main_user, subset_of_users):
        main_user_set = self.all_users_sets_dict[main_user]
        if len(subset_of_users) < 1:
            return set()
        
        first_user = list(subset_of_users)[0]
        new_set = main_user_set.intersection(self.all_users_sets_dict_no_main_user[first_user])
        for user in list(subset_of_users)[1:]:
            new_set = new_set.intersection(self.all_users_sets_dict_no_main_user[user])
            
        return new_set
    
    
#################################################
######### GENERAL FUNCS #########################
#################################################
        
def get_serialized_article(article_key, subset_of_users):
    is_ok = False # turns True when found a serialized article to return
    
    for user_name in subset_of_users:
        if (not is_ok): 
            try:
                query = db.GqlQuery("SELECT * FROM Label WHERE users_list = :1 "+
                                "AND article_key = :2", 
                                user_name, article_key)
                
                if (query.count(2) == 0):
                    continue
                
                results = query.fetch(10)
                label_obj =  results[0]
                serilized_article = label_obj.serialized_article
                is_ok = True
            except Exception:
                return None
        
        if is_ok: 
            return serilized_article
        else:
            return None
            
            
            

    
       
def get_users_article_sets_dict():
    pass

def sort_list_of_suggestions_by_rank(list_of_suggestions):
    return sorted(list_of_suggestions, key=lambda sugg: sugg.rank, reverse=True)

def sort_list_of_suggestions_by_date(list_of_suggestions):
    return sorted(list_of_suggestions, key=lambda sugg: sugg.date_created, reverse=True)
    
# return the articles in the following order:
# created last week first -ordered within by rank
# after that all the rest - ordered by rank
# igonre suggestions that where already deleted 
def get_list_of_suggested_article_ordered_by_rank(user_name):
    suggestions_list = []
    final_articles_list = []
    query = db.GqlQuery("SELECT * FROM Suggestion WHERE user = :1", user_name)
        # results = q.fetch(10)
        # this is supposed to be only one result but who knows...
    for sugg in query:
        if (not sugg.is_removed):
            suggestions_list.append(sugg)    
    
    for sugg in sort_list_of_suggestions_by_rank(suggestions_list):
        final_articles_list.append(pickle.loads(str(sugg.suggested_serialized_article)))
    
    html_parser = HTMLparser.HTMLparser(url=None, html=None)
    html_parser.results = final_articles_list
    html_parser.numOfResults = len(final_articles_list)
    return html_parser

# return the articles in the following order:
# created last week first -ordered within by rank
# after that all the rest - ordered by rank
# igonre suggestions that where already deleted 
def get_list_of_suggested_article_ordered_by_date(user_name):
    suggestions_list = []
    final_articles_list = []
    query = db.GqlQuery("SELECT * FROM Suggestion WHERE user = :1", user_name)
        # results = q.fetch(10)
        # this is supposed to be only one result but who knows...
    for sugg in query:
        if (not sugg.is_removed):
            suggestions_list.append(sugg)    
    
    for sugg in sort_list_of_suggestions_by_date(suggestions_list):
        final_articles_list.append(pickle.loads(str(sugg.suggested_serialized_article)))
    
    html_parser = HTMLparser.HTMLparser(url=None, html=None)
    html_parser.results = final_articles_list
    html_parser.numOfResults = len(final_articles_list)
    return html_parser


def get_num_of_suggestions_for_user(user_name):
    query = db.GqlQuery("SELECT * FROM Suggestion WHERE user = :1", user_name)
    return query.count()

# this function turns the is_removed to True but leaves the suggestion
# in the DB so that the user wont get the same suggestion again
def remove_suggestion(user_name, article_key):
    try:
        query = db.GqlQuery("SELECT * FROM Suggestion WHERE user = :1 " + 
                            "AND suggested_article_key = :2 ", user_name, article_key)
        if (query.count(1) == 0):
            return -4
        
        suggestion = query.fetch(2)[0]
        suggestion.is_removed = True
        suggestion.put()
    except Exception: 
        msg = "error. lea."
        msg = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
        return msg # str(type(temp))
    return True
    
    
