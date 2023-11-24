from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, AndGroup
import os

query = "I think I am wrng"
queries = query.split()

myindex = open_dir("indexdir")
with myindex.searcher() as searcher:
    corrected = searcher.correct_query(query, qstring)