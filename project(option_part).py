from bs4 import BeautifulSoup
import requests
import re
import csv
import pandas as pd 
import numpy as np 
from selenium import webdriver 
import sqlite3
import ssl
import urllib.request, urllib.parse, urllib.error
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import collections
from math import*


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

def merge(lst1,lst2):
    return [a + [b[1]] for (a, b) in zip(lst1, lst2)]

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean,"", text)


def GetIMDBMovieNames():
    url_imdb = 'http://www.imdb.com/chart/top'
    response = requests.get(url_imdb)
    soup = BeautifulSoup(response.text, 'lxml')
    movies = soup.select('td.titleColumn')
    final_movies = movies[:50]
    print(len(final_movies))
    imdb = []
    i = 0
    for index in range(0, len(final_movies)):
        i = i + 1
        movie_string = movies[index].get_text()
        movie = (' '.join(movie_string.split()).replace('.', ''))
        movie_title = movie[len(str(index))+1:-7]
        imdb.append(movie_title)
    return imdb  



def GetIMDBMovieReviewLinks():
    url_imdb = 'https://www.imdb.com/chart/top'
    response = requests.get(url_imdb)
    soup = BeautifulSoup(response.text, 'lxml')
    movie_links = soup.select('td.titleColumn a')
    imdb_top_5_links = movie_links[:50]
    imdb_movie_links = []
    for a in imdb_top_5_links:
        links = a.attrs.get('href')
        movie_links = 'https://www.imdb.com'+links+'reviews?ref_=tt_urv'
        imdb_movie_links.append(movie_links)
    return imdb_movie_links

def GetIMDBMovieReviews():
    review_list = []
    for url in GetIMDBMovieReviewLinks():
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            review_tag = soup.find_all('div', class_ = 'text show-more__control')
            top_50 = review_tag[:50]
            for j in top_50:
                review_list.append(remove_html_tags(str(j)).replace('\n',''))
    return review_list
                


def GetIMDBMovieReviewWords():
    movie_reviews = GetIMDBMovieReviews()
    for i in range(0,len(movie_reviews)):
        reviews = str(movie_reviews[i])
        reviews = remove_html_tags(reviews)
        review2 = re.sub(r'[^\w\s]','',reviews.strip().lower())
        text_token = word_tokenize(review2)
        moview_review_words = [word for word in text_token if not word in stopwords.words()]
    return moview_review_words 



def IMDB_Dictionary(my_list): 
   count = {} 
   for i in my_list:    
    count[i] = count.get(i, 0) + 1
   return count 

#____________________________________________________________________RottenTomatoes_________________________________________________________________________________________


def GetRottenTomatoesMovieNames():
   
    url_imdb = 'https://www.rottentomatoes.com/top/bestofrt/'
    response = requests.get(url_imdb)
    soup = BeautifulSoup(response.text, 'lxml')
    movies = soup.select('table.table a')
    final_movies = movies[:50]
    imdb = []
    i = 0 
    
    for index in range(0, len(final_movies)):
        
        i = i + 1
        movie_string = movies[index].get_text()
        movie = (' '.join(movie_string.split()).replace('.', ''))
        data = [i,movie]
        imdb.append(data)
    return imdb  

def GetRottenTomatoesMovieLinks():
    url_imdb = 'https://www.rottentomatoes.com/top/bestofrt/'
    response = requests.get(url_imdb)
    soup = BeautifulSoup(response.text, 'lxml')
  
    movie_links = soup.select('table.table a')
    imdb_top_5_links = movie_links[:50]
    movie_links = []
    i = 0
    for a in imdb_top_5_links:
        i = i + 1
        links = a.attrs.get('href')
        url = 'https://www.rottentomatoes.com'+links+'/reviews?type=user'
        movie_links.append(url)
    return movie_links    

def GetRottenTomatoesMovieReviews():
    review_list = []
    for url in GetRottenTomatoesMovieLinks():
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            container = soup.find_all('p', class_ = 'audience-reviews__review js-review-text clamp clamp-8 js-clamp')
            top_50 = container[:50]
            for j in top_50:
                review_list.append( remove_html_tags(str(j)).replace('\n',''))
    return review_list
               


def GetRottenTomatoesMovieReviewWords():
    movie_reviews = GetRottenTomatoesMovieReviews()
    for i in range(0,len(movie_reviews)):
        reviews = str(movie_reviews[i])
        review2 = re.sub(r'[^\w\s]','',reviews.strip().lower())
        text_token = word_tokenize(review2)
        moview_review_words = [word for word in text_token if not word in stopwords.words()]
    return moview_review_words 



def RottenTomatoes_Dictionary(my_list): 
   count = {} 
   for i in my_list: 
    count[i] = count.get(i, 0) + 1
   return count     









#____________________________________________________________________METACRITIC___________________________________________________________________________________________________#

def get_name(movie):
    name = movie.find('h3').text
    return(name)



def get_link(movie):
    tag = movie.find('a', class_ = 'title')
    link = tag.get('href', None)
    movie_link = 'https://www.metacritic.com'+ link
    movie_page = requests.get(movie_link, headers = headers)
    movie_soup = BeautifulSoup(movie_page.content, "html.parser")
    movie_tag = movie_soup.find_all('a', class_ = 'see_all boxed oswald') 
    user_review_tag = movie_tag[1] 
    review_url = user_review_tag.get('href', None)
    if not review_url.endswith('user-reviews'):
        full_link = 'No user review yet.'
    else:
        full_link = 'https://www.metacritic.com'+ review_url
    return(full_link)   



def get_reviews(movie):
    review_link = get_link(movie)
    if not review_link ==  'No user review yet.':
        review_page = requests.get(review_link, headers = headers)
        review_soup = BeautifulSoup(review_page.content, "html.parser")
        review_tag = review_soup.find_all('div', class_ = 'summary')
        top_50 = review_tag[:50]
        review_list = []
        for j in top_50:
            try:
                review = j.select('span.blurb blurb_expanded')[0].text
            except:
                review = j.select('div.review_body')[0].text
            review_list.append(review)
    else:
        review_list = 'nothing here'
    return(review_list)



def review_words(review):
    review2 = re.sub(r'[^\w\s]','',review.strip().lower())
    text_token = word_tokenize(review2)
    review3 = [word for word in text_token if not word in stopwords.words()]
    return(review3)    


def Metacrtitc_Review_Words():
    url = 'https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc'
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.content, "html.parser")
    container = soup.find_all('td', class_ = 'clamp-summary-wrap')
    movies = container[:50]
    all_words = []
    n = 0
    for movie in movies:
        review_list = get_reviews(movie)
        if type(review_list) is list:
            for review in review_list:
                all_words.extend(review_words(review))
        else:
            continue
    return all_words    
           
           
      
     
       

def Metactritic_Dictionary(my_list): 
   count = {} 
   for i in my_list: 
    count[i] = count.get(i, 0) + 1
   return count       

#____________________________________________________________________Calculate Cosine Similarity_____________________________________________________________________#


def union(dict1, dict2):
    return dict(list(dict1.items()) + list(dict2.items()))
    #return dict(itertools.chain.from_iterable(dct.items() for dct in dicts))   ## For n - dictionaries (#add *dict as parameter)

    


def Cosine_Similarity():
    
    imdb = IMDB_Dictionary(GetIMDBMovieReviewWords())
    rottentomatoes = RottenTomatoes_Dictionary(GetRottenTomatoesMovieReviewWords())
    metacritic = Metactritic_Dictionary(Metacrtitc_Review_Words())

    imdb_U_rottentomatoes = union(imdb,rottentomatoes)
    rottentomatoes_U_metactritic = union(rottentomatoes,metacritic)

    genre={'Website1_2': imdb_U_rottentomatoes,
           'Website2_3': rottentomatoes_U_metactritic}

    def square_rooted(x):

        return round(sqrt(sum([a*a for a in x])),3)

    def cosine_similarity(x,y):
        input1 = {}
        input2 = {}
        vector2 = []
        vector1 =[]

        if len(x) > len(y):
            input1 = x
            input2 = y
        else:
            input1 = y
            input2 = x

        vector1 = list(input1.values())
        for k in input1.keys():    
            if k in input2:
                vector2.append(float(input2[k]))
            else :
                vector2.append(float(0))
        numerator = sum(a*b for a,b in zip(vector2,vector1))
        denominator = square_rooted(vector1)*square_rooted(vector2)
        return round(numerator/float(denominator),3)


    print("Cosine Similarity between IMDB and ROTTEN_TOMATOES")
    print (cosine_similarity(genre['IMDB'],genre['ROTTEN_TOMATOES']))

    print("Cosine Similarity between IMDB and METACRITIC")
    print (cosine_similarity(genre['IMDB'],genre['METACRITIC']))

    print("Cosine Similarity between ROTTEN_TOMATOES and METACRITIC")
    print (cosine_similarity(genre['ROTTEN_TOMATOES'],genre['METACRITIC']))

    print("Cosine Similarity between the 3 Websites is : ")
    print (cosine_similarity(genre['Website1_2'],genre['Website2_3']))



if __name__ == "__main__":
    i = 0
    print('\n############## IMDB #################\n')
    print('\nFetching IMDB Movie Names......\n')
    for n in GetIMDBMovieNames():
        i = i + 1
        print(i,'.',n)
    i = 0    
    print('\nFetching IMDB Movie Links......\n')
    for a in GetIMDBMovieReviewLinks():
        i = i + 1
        print(i,'.',a)
    print('\nFetching IMDB Movie Reviews......\n')    
    for r in GetIMDBMovieReviews():
        print(r)
    print('\nGenerating IMDB Movie Reviews Dictionary......\n')   
    print(IMDB_Dictionary(IMDB_Dictionary(GetIMDBMovieReviewWords())))    
    i = 0
    print('\n############## Rotten Tomatoes #################\n')
    print('\nFetching Rotten Tomatoes Movie Names......\n')
    for n in GetRottenTomatoesMovieNames():
        i = i + 1
        print(i,'.',n)
    print('\nFetching Rotten Tomatoes Movie Links......\n')
    i = 0
    for a in GetRottenTomatoesMovieLinks():
        i = i + 1
        print(i,'.',a)
    print('\nFetching Rotten Tomatoes Movie Reviews......\n')    
    for r in GetRottenTomatoesMovieReviews():
        print(r)
    print('\nGenerating Rotten Tomatoes Movie Reviews Dictionary......\n')   
    print(RottenTomatoes_Dictionary(RottenTomatoes_Dictionary(GetRottenTomatoesMovieReviewWords())))   
    url = 'https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc'
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.content, "html.parser")
    container = soup.find_all('td', class_ = 'clamp-summary-wrap')
    movies = container[:50]
    all_words = []
    i = 0
    print('\n############## METACRITIC #################\n')
    print('\nFetching METACRITIC Movie Names......\n')
    for movie in movies:
        i = i + 1
        print(i,'.',get_name(movie))
    print('\nFetching METACRITIC Movie Links......\n')
    i = 0
    for movie in movies:
        i = i + 1
        print(i,'.',get_link(movie))
    print('\nFetching METACRITIC Movie Reviews......\n')    
    for movie in movies:
        print(get_reviews(movie))
    print('\nGenerating METACRITIC Movie Reviews Dictionary......\n')   
    print(Metactritic_Dictionary(Metacrtitc_Review_Words)) 
    print('\nCalculating Cosine Similarity......\n')
    Cosine_Similarity()
   
    