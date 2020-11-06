import requests
import os
from time import sleep
import pandas as pd


class DownloadJSONFile():

    def __init__(self, API_KEY, PASSWORD, DOMAIN_NAME, LIMIT_PER_PAGE, API_VERSION, TYPE_OF_JSON,
                 RESULT_JSON_FILE_NAME, TRIM_FROM, TRIM_TO, PAYLOAD_CONATAINS_ONLY_ID, SHOP_NAME):

        self.API_KEY = API_KEY

        self.PASSWORD = PASSWORD

        self.DOMAIN_NAME = SHOP_NAME + "." + DOMAIN_NAME

        self.LIMIT_PER_PAGE = LIMIT_PER_PAGE

        self.API_VERSION = API_VERSION

        self.TYPE_OF_JSON = TYPE_OF_JSON

        self.TRIM_FROM = TRIM_FROM

        self.TRIM_TO = TRIM_TO

        self.RESULT_JSON_FILE_NAME = RESULT_JSON_FILE_NAME

        self.PAYLOAD_CONATAINS_ONLY_ID = PAYLOAD_CONATAINS_ONLY_ID

        self.SHOP_NAME = SHOP_NAME

    def addJsonToFile(self, payload, API_KEY, PASSWORD, DOMAIN_NAME, API_VERSION, TYPE_OF_JSON, RESULT_JSON_FILE_NAME, TRIM_FROM,
                      TRIM_TO, SHOP_NAME):
        """
        To get the json content and append in the json file
        """
        if self.PAYLOAD_CONATAINS_ONLY_ID == 'yes':
            payload['fields'] = 'id,handle,title'
        baseUrl = 'https://' + API_KEY + ":" + PASSWORD + "@" + DOMAIN_NAME + "/admin/api/" + API_VERSION +"/" +TYPE_OF_JSON+".json"
        response = requests.get(baseUrl, params=payload)
        if response.status_code != 200:   # If internet disconnects in the middle it will retry
            sleepTime = 10
            while response.status_code != 200:
                sleep(sleepTime)
                response = requests.get(baseUrl, params=payload)
                sleepTime = sleepTime + 10
                if sleepTime == 300:
                    break

        if response.text != '{"articles":[]}':
            with open(RESULT_JSON_FILE_NAME, 'a',
                      encoding='utf-8-sig') as jsonFile:
                jsonFile.write(str(response.text)[TRIM_FROM:TRIM_TO] + ",")  # To remove extra brackets
                jsonFile.close()
        return response

    def generateJSONFile(self):
        """
        This method is to collect content from API call and to write as a json file
        """
        payload = {'limit': self.LIMIT_PER_PAGE, 'page_info': ''}
        response = self.addJsonToFile(payload, self.API_KEY, self.PASSWORD, self.DOMAIN_NAME, self.API_VERSION,
                                      self.TYPE_OF_JSON,
                                      self.RESULT_JSON_FILE_NAME, self.TRIM_FROM, self.TRIM_TO, self.SHOP_NAME)
        while True:  # To collect all the product from second page
            try:
                responseHeaderLink = (response.headers['link'])  # Getting the link from the response
                if 'rel="previous"' not in responseHeaderLink:
                    nextUrlParams = responseHeaderLink.split('page_info=')[1].split('>')[0]
                else:
                    splitHeaderLink = responseHeaderLink.split(';')
                    nextUrlParams = splitHeaderLink[1].split('page_info=')[1].split('>')[0]
                payload = {'limit': self.LIMIT_PER_PAGE, 'page_info': nextUrlParams}

            except:
                break  # Breaks at the last page

            response = self.addJsonToFile(payload, self.API_KEY, self.PASSWORD, self.DOMAIN_NAME, self.API_VERSION,
                                          self.TYPE_OF_JSON,
                                          self.RESULT_JSON_FILE_NAME, self.TRIM_FROM, self.TRIM_TO, self.SHOP_NAME)

        with open(self.RESULT_JSON_FILE_NAME, 'rb+') \
                as jsonFile:
            jsonFile.seek(-1, os.SEEK_END)  # To remove ,(comma) at the last
            jsonFile.truncate()
            jsonFile.close()

        with open(self.RESULT_JSON_FILE_NAME, 'r+',
                  encoding='utf-8-sig') as jsonFile:
            content = jsonFile.read()
            jsonFile.seek(0, 0)
            jsonFile.write('[' + content)
            content = jsonFile.read()  # Adding square brackets in the beginning and ending of the file
            jsonFile.write(content + ']')
            jsonFile.close()

    def downloadArticles(self, BLOGS_JSON_FILE_NAME):
        """
        This method is to download articles from blogs ID by API call
        """
        # Assigning feed file name
        with open(BLOGS_JSON_FILE_NAME, encoding="utf-8-sig") \
                as jsonContent:
            trimmedJsonContent = (jsonContent.read())
        blogsDF = pd.read_json(trimmedJsonContent)    # Loading json content as pandas data frame
        for index, row in blogsDF.iterrows():
            payload = {'limit': self.LIMIT_PER_PAGE, 'page_info': ''}
            response = self.addJsonToFile(payload, self.API_KEY, self.PASSWORD, self.DOMAIN_NAME,
                                           self.API_VERSION ,"blogs/"+ str(row['id']) + '/articles',
                                          self.RESULT_JSON_FILE_NAME, self.TRIM_FROM, self.TRIM_TO, self.SHOP_NAME)
            while True:  # To collect all the product from second page
                try:
                    responseHeaderLink = (response.headers['link'])  # Getting the link from the response
                    if 'rel="previous"' not in responseHeaderLink:
                        nextUrlParams = responseHeaderLink.split('page_info=')[1].split('>')[0]
                    else:
                        splitHeaderLink = responseHeaderLink.split(';')
                        nextUrlParams = splitHeaderLink[1].split('page_info=')[1].split('>')[0]
                    payload = {'limit': self.LIMIT_PER_PAGE, 'page_info': nextUrlParams}

                except:
                    break  # Breaks at the last page

                response = self.addJsonToFile(payload, self.API_KEY, self.PASSWORD, self.DOMAIN_NAME,
                                              self.API_VERSION, self.TYPE_OF_JSON,
                                              self.RESULT_JSON_FILE_NAME, self.TRIM_FROM, self.TRIM_TO, self.SHOP_NAME)

        with open(self.RESULT_JSON_FILE_NAME, 'rb+') \
                as jsonFile:
            jsonFile.seek(-1, os.SEEK_END)  # To remove ,(comma) at the last
            jsonFile.truncate()
            jsonFile.close()

        with open(self.RESULT_JSON_FILE_NAME, 'r+',
                  encoding='utf-8-sig') as jsonFile:
            content = jsonFile.read()
            jsonFile.seek(0, 0)
            jsonFile.write('[' + content)  # Adding square brackets in the beginning and ending of the file
            content = jsonFile.read()
            jsonFile.write(content + ']')
            jsonFile.close()