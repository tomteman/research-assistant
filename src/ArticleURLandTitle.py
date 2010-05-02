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
        self.hasLink = True
        
        
    def get_article_title(self):
        return self.__articleTitle


    def get_article_url(self):
        return self.__articleURL


    def get_has_link(self):
        return self.__hasLink


    def set_article_title(self, value):
        self.__articleTitle = value


    def set_article_url(self, value):
        self.__articleURL = value


    def set_has_link(self, value):
        self.__hasLink = value


    def del_article_title(self):
        del self.__articleTitle


    def del_article_url(self):
        del self.__articleURL


    def del_has_link(self):
        del self.__hasLink

    articleTitle = property(get_article_title, set_article_title, del_article_title, "articleTitle's docstring")
    articleURL = property(get_article_url, set_article_url, del_article_url, "articleURL's docstring")
    hasLink = property(get_has_link, set_has_link, del_has_link, "hasLink's docstring")
