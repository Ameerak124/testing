import json
from wikiscrapping import wikipedia_scrapper
from summarizing import summarizzing
from flask import Flask
from flask import Flask, render_template, request, jsonify, Response, url_for, redirect
from flask_cors import CORS, cross_origin
from mongoDBOperations import MongoDBManagement
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import urlopen 
import base64
from logger_class import getLog

db_name= "wikidb"       # Name of the DataBase

logger = getLog('app.py')

app = Flask(__name__)

#For selenium driver implementation on heroku
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("disable-dev-shm-usage")

@app.route('/', methods=['GET', 'POST']) # To render Homepage
@cross_origin()
def home_page():
    return render_template('index.html')

@app.route('/scrap',methods = ["POST"])
def index():

    if(request.method == "POST"):
        #searchString = request.form['content'].replace(" ", "").lower()  # obtaining the search string entered in the form    
        searchString = request.form['content'].lower()  # obtaining the search string entered in the form    
        try:
            mongo_object = MongoDBManagement(username="rakesh", password="rk123")  #instance of the MongoDBManagement Class
            mongo_object.createDatabase(db_name)  #creating the DB                  

            #******************* To check if Collection is present or not *******************************
            if(mongo_object.isCollectionPresent(collection_name=searchString, db_name=db_name) == True):
                logger.info("Database Already Present") 
                response = mongo_object.findAllRecords(db_name=db_name, collection_name=searchString)
                reviews = [i for i in response]
                if len(reviews) > 0:       # If present then check if is empty or not
                    for i in reviews:
                        Summary = (i["Summary"])  # show the results to user if collection has data
                        Ref_link = (i["Ref_link"])  # show the results to user if collection has data
                        Image_link = (i["Image_link"])  # show the results to user if collection has data
                    return render_template('results.html',Summary=Summary,Ref_link = Ref_link,Image_link =Image_link )  

                #******************* if Collection is present and it is empty *******************************
                else:
                    summarized_text = "" 
                    paragraph_nobrac = []
                    imgtob64_converted = []

                    find = wikipedia_scrapper("https://www.wikipedia.org/")
                    logger.info("Url hitted")

                    logger.info(f"Search begins for {searchString}")
                    lst = find.search(searchString) 
                    logger.info("Searching completed")  
                    
                    for text in lst:
                        text_nobrac = find.bracketremoval(text)         #Scrapping
                        paragraph_nobrac.append(text_nobrac)
                                       
                    summarized_paragraph2 = summarizzing()      #instance of the summarizzing class
                    
                    print("************************** >>>> Inner Else BLOCK <<<< ************************************")
                   
                    for text in paragraph_nobrac:
                        text = text.replace('"','')  # Removing "" from the text
                        #print(f"TEXT = {text} \n\n\n")
                        summarized_text = summarized_text + summarized_paragraph2.summarizer(text)  #Summarizing the text
                    logger.info("Summarization Done") 

                    ref_links = find.ref()
                    logger.info("Ref_links Fetched")

                    image_links = find.image()
                    logger.info("Image_links Fetched")

                    for url in image_links:
                        mybs64 = base64.b64encode(urlopen(url).read())
                        imgtob64_converted.append(mybs64)
                    logger.info("imgtob64 Done")

                    result = {"Summary" : summarized_text,
                              "Ref_link" : ref_links,
                              "Image_link" : image_links,
                              "Imgtob64" : imgtob64_converted}  #Converting to dict
                                

                    mongo_object.insertRecord(db_name=db_name, collection_name=searchString, record = result) # Insert the dict to DB
                    logger.info("Data saved in MongoDB")
                    #result = result["Summary"]
                    return render_template('results.html',Summary=result["Summary"],Ref_link = result["Ref_link"],Image_link =result["Image_link"])

            #******************* If Collection is not present *******************************
            else:
    
                mongo_object.createCollection(collection_name=searchString, db_name=db_name) #Creating a collection
                
                paragraph_nobrac = []    
                summarized_text = ""
                imgtob64_converted = []

                find = wikipedia_scrapper("https://www.wikipedia.org/")
                logger.info("Url hitted")

                logger.info(f"Search begins for {searchString}")
                lst = find.search(searchString) 
                logger.info("Searching completed") 
                
                for text in lst:
                        text_nobrac = find.bracketremoval(text)         #Scrapping
                        paragraph_nobrac.append(text_nobrac)
                
                summarized_paragraph2 = summarizzing()

                print("************************** >>>> Outer Else BLOCK <<<< ************************************")
                for text in paragraph_nobrac:
                    text = text.replace('"','')
                    #print(f"TEXT = {text} \n\n\n")

                    print("************************** >>>> check 1 <<<< ************************************")
                    summarized_text = summarized_text +"\n\n\t"+ summarized_paragraph2.summarizer(text)
                
                logger.info("Summarization Done") 
                print("************************** >>>> check 2 <<<< ************************************")
                
                ref_links = find.ref()
                logger.info("Ref_links Fetched")

                print("************************** >>>> check 3 <<<< ************************************")
                image_links = find.image()
                logger.info("Image_links Fetched")

                for url in image_links:
                        mybs64 = base64.b64encode(urlopen(url).read())
                        imgtob64_converted.append(mybs64)
                logger.info("imgtob64 Done")
           
                print("************************** >>>> check 6 <<<< ************************************")
                result = {"Summary" : summarized_text,
                              "Ref_link" : ref_links,
                              "Image_link" : image_links,
                              "Imgtob64" : imgtob64_converted}  #Converting to dict

                print("************************** >>>> check 7 <<<< ************************************")                        
                mongo_object.insertRecord(db_name=db_name, collection_name=searchString, record = result)
                logger.info("Data saved in MongoDB")

                #result = result["Summary"]
                
                print("************************** >>>> check 8 <<<< ************************************")
                return render_template('results.html',Summary=result["Summary"],Ref_link = result["Ref_link"],Image_link =result["Image_link"])
                
        except Exception as e:
            raise Exception("(app.py) - Something went wrong while rendering all the details of product.\n" + str(e))
        
        #return jsonify(result)  # Returning the final result
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run()