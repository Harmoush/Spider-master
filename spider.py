from urllib2 import urlopen
from link_finder import LinkFinder
from domain import *
from general import *
from gensim.models.doc2vec import TaggedLineDocument, Doc2Vec
#from keras.utils import get_file
import numpy as np

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()
    data_train = set()
    data_test =set()
    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)

            #Building the Doc2vec Model
            f = urlopen(page_url)
            html=f.read()
            open('temp.txt', 'w').close()
            f=open('temp.txt','w')
            f.write(html)
            f.close()
            html=TaggedLineDocument('temp.txt')
            model = Doc2Vec(html, size=100, window=8, min_count=5, workers=4)
            model.train(html, total_examples=100, epochs=5)
            #print model.docvecs[0]

            #saving data for building and testing the svm
           # if len(Spider.data_train)<50:
            #    Spider.data_train.add(model.docvecs[0])
            #else:
             #   Spider.data_test.add(model.docvecs[0])

            #set_to_file(Spider.data_train,'data_train.txt')
            #set_to_file(Spider.data_test,'data_test.txt')


            Spider.crawled.add(page_url)
            Spider.update_files()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.info().getheader('Content-Type'):
               html_bytes = response.read()
               html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
