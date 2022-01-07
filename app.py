from flask import Flask, render_template, request, url_for, redirect, flash
from flask_cors import CORS, cross_origin
from mongoDBOperations import MongoDBManagement
from WikiScrapping import WikipediaScrapper
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


# Database credentials
username = 'Zahoor'
password = 'aXnTvIYxLAwBAbxq'
db_name = 'Wikipedia-Scrapper'

free_status = True

# initialising the flask app with the name 'app'
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#For selenium driver implementation on heroku
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("disable-dev-shm-usage")

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        global free_status, collection_name
        ## To maintain the internal server issue on heroku
        if free_status != True:
            return "This website is executing some process. Kindly try after some time..."
        else:
            free_status = True

        # obtaining the search string entered in the form
        search_term = request.form['topic']

        try:
            mongoClient = MongoDBManagement(username=username, password=password)
            collection_name = search_term.replace(" ","-").lower()
            if mongoClient.isCollectionPresent(collection_name=collection_name, db_name=db_name):
                return redirect(url_for('search',collection_name=collection_name))
            else:
                try:
                    scrapper_object = WikipediaScrapper(executable_path=ChromeDriverManager().install(),chrome_options=chrome_options)
                    wikipediaData = scrapper_object.searchWikipedia(search_term)
                    if wikipediaData is False:
                        flash(f'{search_term}', 'danger')
                        return redirect(url_for('index'))
                    else:
                        mongoClient.saveJsonDataIntoCollection(collection_name=collection_name, db_name=db_name, json_data=wikipediaData)
                        return redirect(url_for('search',collection_name=collection_name))
                except Exception as e:
                    flash(f'{search_term}', 'danger')
                    return redirect(url_for('index'))

        except Exception as e:
            raise Exception("(app.py) - Something went wrong on scrapping wikipedia article.\n" + str(e))

    return render_template('index.html')

@app.route('/search/<collection_name>')
@cross_origin()
def search(collection_name):
    try:
        if collection_name is not None:
            mongoClient = MongoDBManagement(username=username, password=password)
            response = mongoClient.findAllRecords(db_name=db_name, collection_name=collection_name)
            context = {
                "title": response.get('Title'),
                "paragraph": response.get('Information'),
                "references_text": response.get('References Text'),
                "references_links": response.get('References Link'),
                "image_links": response.get('Image Links'),
                "wiki_link": response.get('Wikipedia Link'),
            }
            return render_template('search.html', context=context, zip=zip)
        else:
            return redirect(url_for('index'))
    except Exception as e:
        raise Exception("(search) - Something went wrong on retrieving wikipedia article from database.\n" + str(e))


if __name__ == "__main__":
    app.run()
