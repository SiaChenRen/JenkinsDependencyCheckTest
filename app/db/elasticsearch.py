from flask import current_app as app
from elasticsearch import Elasticsearch, helpers
import time


class ElasticsearchDAO:
    def __init__(self):
        self.username = app.config["NOSQL_USER"]
        self.password = app.config["NOSQL_PASSWORD"]
        self.index_logs = app.config["NOSQL_INDEX_LOGS"]
        self.index_posts = app.config["NOSQL_INDEX_POSTS"]
        self.index_messaging = app.config["NOSQL_INDEX_MESSAGING"]
        self.hosts = app.config["NOSQL_HOSTS"]
        self.es = Elasticsearch(self.hosts, http_auth=(self.username, self.password))


    def ping(self):
        if self.es.ping():
            print("Successfully connected to Elasticsearch.")
            return True
        else:
            print("Could not connect to Elasticsearch database!")
            return False


    def close(self):
        return self.es.close()


    # Post content methods
    def create_post(self, post_id, title, description, content):
        body = {"title": title, "description": description, 'content':content}

        try:
            self.es.create(index=self.index_posts, body=body, id=post_id)
            return [True, "Post has been successfully created."]
        except Exception as e:
            print("Error in indexing data!")
            print(str(e))
            return [False, "Error in creating post."]


    def retrieve_post(self, post_id):
        query = {"query": {"match": {"_id": post_id}}}

        try:
            result = self.es.search(index=self.index_posts, body=query)
            post_data = result["hits"]["hits"]
            
            if post_data[0] is None:
                return [False, "Post data not found."]

            return [True, post_data]
        except Exception as e:
            print("Error in retrieving data!")
            print(str(e))
            return [False, "Error in retrieving post data."]

    
    def retrieve_post_list(self):
        try:
            result = self.es.search(index=self.index_posts)
            post_data = result["hits"]["hits"]
            
            if post_data[0] is None:
                return [False, "Post data not found."]

            return [True, post_data]
        except Exception as e:
            print("Error in retrieving data!")
            print(str(e))
            return [False, "Error in retrieving post data."]


    def search_post(self, searchterm):
        query = {"query": {"bool": {"must": {"wildcard": {"title": searchterm+"*"}}}}}
        
        try:
            result = self.es.search(index=self.index_posts, body=query)
            post_data = result["hits"]["hits"]

            if post_data is None:   
                return [False, "Post data not found."]
            return [True, post_data]
        except Exception as e:
            print("Error in retrieving data!")
            print(str(e))
            return [False, "Error in retrieving post data."]


    def update_post(self, postID, title, description):
        body = {
            "doc" : {
            "title" : title,
            "description":description
            }
        }

        try:
            self.es.update(index=self.index_posts,  doc_type="_doc", id=postID, body=body, refresh=True)
            return [True, "Successfully update the post data"]
        except Exception as e:
            return [False, "Error in updating post data."]


    def remove_post(self, post_id):
        try:
            self.es.delete(index=self.index_posts,  doc_type="_doc", id=post_id, refresh=True)
            return True
        except:
            return False

    
    # Messaging content methods
    def create_message(self, message_id, message):
        body = {"message": message}

        try:
            self.es.create(index=self.index_messaging, body=body, id=message_id, refresh=True)
            return [True, "Message send"]
        except Exception as e:
            print(str(e))
            return [False, "Error occured while trying to send message"]


    def retrieve_message(self, message_id):
        query = {"query": {"match": {"_id": message_id}}}
        
        try:
            result = self.es.search(index=self.index_messaging, body=query)
            message_data = result["hits"]["hits"]
            
            if message_data[0] is None:
                return [False, "Message data not found."]

            return [True, message_data]
        except Exception as e:
            print("Error in retrieving data!")
            print(str(e))
            return [False, "Error in retrieving message data."]


    # Logging methods
    def send_log(self, jsonData):
        try:
            self.es.index(index=self.index_logs, body=jsonData)
            return True
        except Exception as e:
            print("Error in indexing data!")
            print(str(e))
            return False

