# Post class to store information of a single post
import datetime

class Post:
    def __init__(self, post_id, mysql_data, elasticsearch_data):
        self.post_id = post_id
        self.post_author = mysql_data["account_id"]
        self.created_on = mysql_data["created_on"].date()
        self.title = elasticsearch_data.get("_source").get("title")
        self.description = elasticsearch_data.get("_source").get("description")
        self.content = elasticsearch_data.get("_source").get("content")

        try:
            self.post_comments = elasticsearch_data.get("_source").get("comments")
        except Exception as e:
            self.post_comments = []