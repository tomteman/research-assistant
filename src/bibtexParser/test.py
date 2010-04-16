from bibtexParser.parser import parse_string
from StringIO import StringIO

data = '''@article{mm09,
    author = {Max Mustermann},
    title = {The story of my life},
    year = {2009},
    journal = {Life Journale}
}'''

bibliography = parse_string(data)
article = bibliography['mm09']
print article
