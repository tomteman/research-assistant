'''
Created on Apr 30, 2010

@author: tomteman
'''

class ArticleURLandTitle:
    '''
    classdocs
    '''


    def __init__(self):
        self.articleTitle = ""
        self.articleURL = ""
        self.hasLink = True  # false if CITATION
        
        
    def get_article_title(self):
        return self.articleTitle


    def get_article_url(self):
        return self.articleURL


    def get_has_link(self):
        return self.hasLink


    def set_article_title(self, value):
        self.articleTitle = value


    def set_article_url(self, value):
        self.articleURL = value


    def set_has_link(self, value):
        self.hasLink = value


    def del_article_title(self):
        del self.articleTitle


    def del_article_url(self):
        del self.articleURL


    def del_has_link(self):
        del self.hasLink

