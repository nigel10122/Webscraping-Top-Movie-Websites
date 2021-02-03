
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
import itertools
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

 

#____________________________________________________________________________________IMDB______________________________________________________________________________________________________________________#

def GetIMDBMovieNames():
    url_imdb = 'http://www.imdb.com/chart/top'
    response = requests.get(url_imdb)
    soup = BeautifulSoup(response.text, 'lxml')
    movies = soup.select('td.titleColumn')
    final_movies = movies[:50]
    imdb = []
    i = 0
    for index in range(0, len(final_movies)):
        i = i + 1
        movie_string = movies[index].get_text()
        movie = (' '.join(movie_string.split()).replace('.', ''))
        movie_title = movie[len(str(index))+1:-7]
        
        data = [i,movie_title]
        imdb.append(data)
    return imdb  
        
def GetIMDBMovieLinks():
    url_imdb = 'https://www.imdb.com/chart/top'
    response = requests.get(url_imdb)
    soup = BeautifulSoup(response.text, 'lxml')
    movie_links = soup.select('td.titleColumn a')
    imdb_top_5_links = movie_links[:50]
    imdb_movie_links = []
    i = 0
    for a in imdb_top_5_links:
        i = i + 1
        links = a.attrs.get('href')
        movie_links = 'https://www.imdb.com'+links
        
        imdb_movie_links.append(movie_links)
    return imdb_movie_links    



def GetIMDBMovieGenre_For_CSV():
    movie_genre = []
    i = 0
    for url in GetIMDBMovieLinks():
        i = i + 1
        page = requests.get(url, headers = headers)
        soup = BeautifulSoup(page.content, "html.parser")
        genre_subtext = soup.find_all('div', class_ = 'see-more inline canwrap')[1]
        genre_subtext2 = genre_subtext.find_all('a')
        genre_subtext3 = remove_html_tags(str(genre_subtext2).strip())
        genre_subtext4 = (' '.join(genre_subtext3.split()).replace('[', ''))
        genre_subtext5 = (' '.join(genre_subtext4.split()).replace(']', ''))
        
        data = [i,genre_subtext5]
        movie_genre.append(data)
    return movie_genre    

def GetIMDBMovieGenre_For_Dict():
    movie_genre = []
    i = 0
    for url in GetIMDBMovieLinks():
        i = i + 1
        page = requests.get(url, headers = headers)
        soup = BeautifulSoup(page.content, "html.parser")
        genre_subtext = soup.find_all('div', class_ = 'see-more inline canwrap')[1]
        genre_subtext2 = genre_subtext.find_all('a')
        for j in range(0,len(genre_subtext2)):
            genre = remove_html_tags(str(genre_subtext2[j]).replace(' ','').replace('Sci-Fi','Scifi'))
            movie_genre.append(genre.lower())
    return movie_genre    
        
def IMDB_Dictionary(my_list): 
   count = {} 
   for i in my_list: 
    count[i] = count.get(i, 0) + 1
   return count 

def IMDB():
    imdb = []
    imdb = merge(GetIMDBMovieNames(),GetIMDBMovieGenre_For_CSV())
    return imdb

def WriteCSVFile_IMDB():    
    filename = "imdb_top_50.csv"
    headers = ['Movie Number', 'Movie Name', 'Movie Genre']
    with open(filename,'w',newline='') as csvfile:  
         csvwriter = csv.writer(csvfile)  
         csvwriter.writerow(headers)  
         csvwriter.writerows(IMDB()) 

def WriteDBFile_IMDB():
    con = sqlite3.connect("MovieGenreDatabase.db") 
    if(con):
        print("Connection Successfull")
    else:
        print("Unable to connect")    
    cur = con.cursor()
   
    with open('imdb_top_50.csv','r') as fin: 
      
        dr = csv.DictReader(fin) 
        to_db = [(i['Movie Number'], i['Movie Name'], i['Movie Genre'])  for i in dr]

    #cur.execute("CREATE TABLE IMDB (Movie_Number,Movie_Name,Movie_Genre)")    
    query = cur.executemany("INSERT INTO IMDB (Movie_Number, Movie_Name, Movie_Genre) VALUES (?, ?, ?);", to_db)
    if(query):
        print("Inserted Successfull")
    else:
        print("Unable to Insert")    
    con.commit()
    con.close()  

#__________________________________________________________________________________ROTTEN TOMATOES______________________________________________________________________________#

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
        url = 'https://www.rottentomatoes.com'+links
        movie_links.append(url)
    return movie_links    
        
def GetRottenTomatoesMovieGenre_For_CSV():
    movie_genre = []
    i = 0
    for url in GetRottenTomatoesMovieLinks():
        i = i + 1
        page = requests.get(url, headers = headers)
        soup = BeautifulSoup(page.content, "html.parser")
        genre_subtext = soup.find('div', class_ = 'meta-value genre').text
        genre_subtext2 = (' '.join(str(genre_subtext).split()).replace('[', ''))
        genre_subtext3 = (' '.join(genre_subtext2.split()).replace(']', ''))
        genre_subtext4 = (' '.join(genre_subtext3.split()).replace('and', ','))
        data = [i,genre_subtext4]
        movie_genre.append(data)
    return movie_genre    

def GetRottenTomatoesMovieGenre_For_Dict():
    movie_genre = []
    i = 0
    for url in GetRottenTomatoesMovieLinks():
        i = i + 1
        page = requests.get(url, headers = headers)
        soup = BeautifulSoup(page.content, "html.parser")
        genre_subtext = soup.find('div', class_ = 'meta-value genre').text
        genre = ' '.join(genre_subtext).replace(',','').replace(' ','').replace('and','\n')
        genre2 = genre.split()
        movie_genre.append(genre2)
    return movie_genre    
    

def RottenTomatoes_Dictionary(my_list): 
   count = {} 
   for i in my_list: 
       for x in i:
            count[x] = count.get(x, 0) + 1
   return count 

def ROTTEN_TOMATOES():
    rotten_tomatoes = []
    rotten_tomatoes = merge(GetRottenTomatoesMovieNames(),GetRottenTomatoesMovieGenre_For_CSV())
    return rotten_tomatoes

def WriteCSVFile_ROTTENTOMATOES():    
    filename = "Rotten_Tomatoes_top_50.csv"
    headers = ['Movie Number', 'Movie Name', 'Movie Genre']
    with open(filename,'w',newline='') as csvfile:  
         csvwriter = csv.writer(csvfile)  
         csvwriter.writerow(headers)  
         csvwriter.writerows(ROTTEN_TOMATOES()) 


def WriteDBFile_RottenTomatoes():
    con = sqlite3.connect("MovieGenreDatabase.db")
    if(con):
        print("Connection Successfull")
    else:
        print("Unable to connect")    
    cur = con.cursor()
 
    with open('Rotten_Tomatoes_top_50.csv','r') as fin:
      
        dr = csv.DictReader(fin) 
        to_db = [(i['Movie Number'], i['Movie Name'], i['Movie Genre'])  for i in dr]
    query = cur.executemany("INSERT INTO ROTTENTOMATOES (Movie_Number, Movie_Name, Movie_Genre) VALUES (?, ?, ?);", to_db)
    if(query):
        print("Inserted Successfull")
    else:
        print("Unable to Insert")    
    con.commit()
    con.close()  


#__________________________________Metacritics____________________________________________________________________________________________________________________________#

def GetMetacriticsMovieNames():
   url = "https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc"
   page = requests.get(url, headers = headers)
   soup = BeautifulSoup(page.content, "html.parser")
   container = soup.find_all('td', class_ = 'clamp-summary-wrap')
   movie_names = []
   movies = container[:50] #here we get the top 50 movies we want
   i = 0
   for movie in movies:
       i = i + 1
       name = movie.find('h3').text
       data = [i, name]
       movie_names.append(data)
   return movie_names

def GetMetacriticsMovieLinks():
    url = "https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc"
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.content, "html.parser")
    container = soup.find_all('td', class_ = 'clamp-summary-wrap')
    movie_reviews = []
    movies = container[:50]
    i = 0
    for movie in movies:
        i = i + 1
        tag = movie.find('a', class_ = 'title')
        link = tag.get('href', None)
        url = "https://www.metacritic.com"+link
        movie_reviews.append(url)
       
    return movie_reviews

def GetMetacriticMovieGenre_For_CSV():
    movie_genre = []
    i = 0
    for url in GetMetacriticsMovieLinks():
        i = i + 1
        page = requests.get(url, headers = headers)
        soup = BeautifulSoup(page.content, "html.parser")
        genre_subtext = soup.find('div', class_ = 'genres').text
        genre_subtext2 = (' '.join(str(genre_subtext).split()).replace('[', ''))
        genre_subtext3 = (' '.join(genre_subtext2.split()).replace(']', ''))
        genre_subtext4 = (' '.join(genre_subtext3.split()).replace('and', ',').replace('Genre(s):',''))
        data = [i,genre_subtext4]
        movie_genre.append(data)
    return movie_genre    

def GetMetacrtiticMovieGenre_For_Dict():
    movie_genre = []
    i = 0
    for url in GetMetacriticsMovieLinks():
        i = i + 1
        page = requests.get(url, headers = headers)
        soup = BeautifulSoup(page.content, "html.parser")
        genre_subtext = soup.find('div', class_ = 'genres').text
        genre = genre_subtext.replace('Genre(s):','').replace(' ','').replace('\n','').replace(',','\n').lower().split() 
        movie_genre.append(genre)

    return movie_genre    
           
def Metacritic_Dictionary(my_list): 
   count = {} 
   for i in my_list: 
       for x in i:
            count[x] = count.get(x, 0) + 1
   return count 

        
def METACTRIC():
    metactric = []
    metactric = merge(GetMetacriticsMovieNames(),GetMetacriticMovieGenre_For_CSV())
    return metactric   

def WriteCSVFile_METACRITIC():    
    filename = "Metactric_top_50.csv"
    headers = ['Movie Number', 'Movie Name', 'Movie Genre']
    with open(filename,'w',newline='') as csvfile:  
         csvwriter = csv.writer(csvfile)  
         csvwriter.writerow(headers)  
         csvwriter.writerows(METACTRIC())    

def WriteDBFile_Metacritics():
    con = sqlite3.connect("MovieGenreDatabase.db")
    if(con):
        print("Connection Successfull")
    else:
        print("Unable to connect")    
    cur = con.cursor()
 
    with open('Metactric_top_50.csv','r') as fin:
      
        dr = csv.DictReader(fin) 
        to_db = [(i['Movie Number'], i['Movie Name'], i['Movie Genre'])  for i in dr]
    query = cur.executemany("INSERT INTO METACRITIC (Movie_Number, Movie_Name, Movie_Genre) VALUES (?, ?, ?);", to_db)
    if(query):
        print("Inserted Successfull")
    else:
        print("Unable to Insert")    
    con.commit()
    con.close()  

#____________________________________________________________________Calculate Cosine Similarity_____________________________________________________________________#

set_total = ('action', 'adventure', 'animation', 'biography', 'comedy', 'crime', 'documentary', 'drama', 'family', 'fantasy', 'film-noir', 'history', 'horror','kids','music', 'musical', 'mystery', 'romance', 'scifi', 'thriller', 'war', 'western')

def combine(dict1,dict2):
    Cdict = collections.defaultdict(int) 
    for key, val in itertools.chain(dict1.items(), dict2.items()): 
        Cdict[key] += val 
    return Cdict

def total(dictionary):
    dict_total = {}
    for i in set_total:
        dict_total.update({i:0})
    for i in list(dict_total.keys()):
        if i in list(dictionary.keys()):
            dict_total[i] = dictionary[i]
    return dict_total

def sort(dictionary):
    sorted_dict = {key: value for key, value in sorted(dictionary.items())}     
    return sorted_dict


def cosine_dic(dic1,dic2):
    numerator = 0
    dena = 0
    for key1,val1 in dic1.items():
        numerator += val1*dic2.get(key1,0.0)
        dena += val1*val1
    denb = 0
    for val2 in dic2.values():
        denb += val2*val2
    return round(numerator/sqrt(dena*denb),3)




#____________________________________________________________________ MAIN _________________________________________________________________________________________#

if __name__ == "__main__":
    
    i = 0
    print('\n############## IMDB #################\n')
    print('\nFetching IMDB Movie Links......\n')
    for a in GetIMDBMovieLinks():
        i = i + 1
        print(i,'.',a)
    print('\nFetching IMDB Movie Genres......\n')    
    for i in IMDB():
        print(i)
    print('\nGenerating IMDB Movie Genre Dictionary......\n')   
    Imdb = sort(IMDB_Dictionary(GetIMDBMovieGenre_For_Dict()))
    imdb = total(Imdb)
    print(imdb)    
    i = 0
    print('\n############## Rotten Tomatoes #################\n')
    print('\nFetching Rotten Tomatoes Movie Links......\n')
    for a in GetRottenTomatoesMovieLinks():
        i = i + 1
        print(i,'.',a)
    print('\nFetching Rotten Tomatoes Movie Genres......\n')    
    for i in ROTTEN_TOMATOES():
        print(i)
    print('\nGenerating Rotten Tomatoes Movie Genre Dictionary......\n')  
    Rottentomatoes = sort(RottenTomatoes_Dictionary(GetRottenTomatoesMovieGenre_For_Dict())) 
    rottentomatoes = total(Rottentomatoes)
    print(rottentomatoes)  
    i = 0
    print('\n############## METACRITIC #################\n')
    print('\nFetching METACRITIC Movie Links......\n')
    for a in GetMetacriticsMovieLinks():
        i = i + 1
        print(i,'.',a)
    print('\nFetching METACRITIC Movie Genres......\n')    
    for i in METACTRIC():
        print(i)
    print('\nGenerating METACRITIC Movie Genre Dictionary......\n')   
    Metacritic = sort(Metacritic_Dictionary(GetMetacrtiticMovieGenre_For_Dict()))
    metacritic = total(Metacritic)
    print(metacritic)  
    print('\nCalculating Cosine Similarity between each website......\n')
    print('\nCosine Similarity between IMDB and RottenTomatoes is : ',cosine_dic(imdb,rottentomatoes),'\n')
    print('\nCosine Similarity between RottenTomatoes and Metacritic is : ',cosine_dic(rottentomatoes,metacritic),'\n')
    print('\nCosine Similarity between IMDB and Metacritic is : ',cosine_dic(imdb,metacritic),'\n')
    print('\nGenerating Common Dictionaries......\n')
    imdb_U_rottentomatoes = combine(imdb,rottentomatoes)
    rottentomatoes_U_metacritic = combine(rottentomatoes,metacritic)
    print('WEBSITE 1 : IMDB + ROTTENTOMATOES = ',imdb_U_rottentomatoes,'\n')
    print('WBESITE 2 : ROTTENTOMATOES + METACRITIC = ',rottentomatoes_U_metacritic,'\n')
    print('\nCalculating Cosine Similarity between all the three websites......\n')
    print('\nThe Cosine Similarity between the 3 Websites is : ',cosine_dic(imdb_U_rottentomatoes,rottentomatoes_U_metacritic),'\n')
    print('\nWriting to CSV Files......\n')
    WriteCSVFile_IMDB()
    WriteCSVFile_ROTTENTOMATOES()
    WriteCSVFile_METACRITIC
    print('\nALL DONE!.......\n')
    
    
    


    
    
      
    

    

