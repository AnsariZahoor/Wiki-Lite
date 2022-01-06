from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

class WikipediaScrapper:
    def __init__(self, executable_path, chrome_options):
        """
        This function initializes the web browser driver
        :param executable_path: executable path of chrome driver.
        """
        try:
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
        except Exception as e:
            raise Exception(f"(__init__): Something went wrong on initializing the webdriver object.\n" + str(e))


    def getUrl(self, search_term):
        """
        This function generate a url from search term
        """
        try:
            url = 'https://en.wikipedia.org/wiki/{}'.format(search_term)
            return url
        except Exception as e:
            raise Exception(f"(getUrl) - Something went wrong while generating url.\n" + str(e))


    def checkPageExist(self, soup):
        """
        This function check Wikipedia does have an article with this exact name.
        """
        try:
            text = soup.find('div', {'class', 'noarticletext'}).find_all('b')
            return False
        except AttributeError as e:
            return True


    def getTitle(self, soup):
        """
        This function returns Wikipedia title
        """
        try:
            #link
            title = soup.find(id="firstHeading").get_text(strip=False)
            return title
        except Exception as e:
            raise Exception(f"(getTitle) -  Not able to get the title.\n" + str(e))


    def getParagraph(self, soup):
        """
        This function returns Wikipedia paragraph
        """
        try:
            paras = ''.join(paragraph.text for paragraph in soup.find_all('p'))
            # Drop footnote superscripts in brackets
            text = re.sub(r"\[.*?\]+", ' ', paras)
            # Replace '\n' (a new line) with ''
            text = text.replace('\n', '')
            return text
        except Exception as e:
            raise Exception(f"(getParagraph) - Not able to get the wikipedia information.\n" + str(e))


    def getImageLink(self, soup):
        """
        This function returns Image Link
        """
        try:
            wiki_image = [div.find('img') for div in soup.find_all('a',{'class':'image'})]
            image_link = [i.get('src') for i in wiki_image]
            image_width = [i.get('width') for i in wiki_image]
            df = pd.DataFrame({'Image Link':image_link, 'Width':image_width})
            df["Width"] = pd.to_numeric(df["Width"])
            df_filtered = df[df['Width'] > 100 ]
            if df_filtered.empty == False:
                image_links = df_filtered['Image Link'].values.tolist()
            else:
                image_links = df['Image Link'].values.tolist()

            return image_links
        except Exception as e:
            raise Exception(f"(getImageLink) - Not able to get the Image Link.\n" + str(e))


    def findElementReference(self, soup):
        """
        This function finds all element from the page.
        """
        try:
            allReferences = soup.find('div',{'class','reflist'}).find_all('a',{'class','external text'})
            return allReferences
        except Exception as e:
            raise Exception(f"(findElementReference) - Something went wrong on searching the element.\n" + str(e))


    def getReferenceText(self, soup):
        """
        This function returns References Text
        """
        try:
            allReferences = self.findElementReference(soup)
            references_text = [i.get_text(strip=True) for i in allReferences]
            return references_text
        except Exception as e:
            raise Exception(f"(getReferenceText) - Not able to get the References Text.\n" + str(e))

    def getReferenceLink(self, soup):
        """
        This function returns References Link
        """
        try:
            allReferences = self.findElementReference(soup)
            references_links = [i.get('href') for i in allReferences]
            return references_links
        except Exception as e:
            raise Exception(f"(getReferenceLink) - Not able to get the References Link.\n" + str(e))

    def getTopReferences(self, soup):
        """
        This function returns References Link
        """
        try:
            references_text = self.getReferenceText(soup)
            references_link = self.getReferenceLink(soup)
            df = pd.DataFrame({'References Text': references_text, 'References Link': references_link})
            text_list = df['References Text'].values.tolist()
            text_alpha = [s for s in text_list if not re.compile(r'\d').search(s)]
            df_filtered = df[df['References Text'].isin(text_alpha)]
            ref_text = df_filtered['References Text'].values.tolist()
            ref_link = df_filtered['References Link'].values.tolist()
            return ref_text[:10], ref_link[:10]
        except Exception as e:
            raise Exception(f"(getTopReferences) - Not able to get the top references.\n" + str(e))



    def searchWikipedia(self, searchString):
        """
        This function helps to search topic using search string provided by the user
        """
        try:
            url = self.getUrl(searchString)
            self.driver.get(url.format(url))
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            if self.checkPageExist(soup) is False:
                return False
            else:
                title = self.getTitle(soup)
                paragraph = self.getParagraph(soup)
                image_links = self.getImageLink(soup)

                references_text, references_links = self.getTopReferences(soup)

                dictionary = {
                    "Title": title,
                    "Information": paragraph,
                    "References Text": references_text,
                    "References Link": references_links,
                    "Image Links": image_links
                }

                return dictionary

        except Exception as e:
            raise Exception(f"(searchWikipedia) - Something went wrong on searching.\n" + str(e))

    

    

