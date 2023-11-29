# Artificial Intelligence and the Web - Project 1: Search Engine
This is the search engine of group 78, Felix Japtok (977397), Eva Kuth (979896) and Elias Harjes()
### Included features
* Searchhistory of the last 10 searched queries
* Searching for single or multiple word queries
    + for multiple word queries only websites where all words from the query are found will be listed
    + occurences will be added up so for searching "unicorn platypus" there will be 7 occurences on page 6 (4 from unicorn, 3 from platypus)
* Recommendations for queries if nothing was found for the last given query
    + recommendations are based on the created index: the nearest word (by Levenshtein distance) from the index will be recommended
    + if no recommendations are found "Please try another query" will be displayed instead of a recommendation
* Improved presentation of search results 
    + show the total number of links found for the given query
    + ordering of the found links based on occurences of the query
    + results are presented in small boxes:
        - clickable title of the found page
        - link to the website found (links can clip outside the box for extremely long links)
        - count of how many times the query occured on the given website
        - small context window showing in which context the query is mentioned on the found website