# Post class to store information of a single post
import datetime

class Message:
    def __init__(self, message_id, mysql_data, elasticsearch_data):
        try:
            self.message_id = message_id
            self.created_on = mysql_data["created_on"].date()
            self.account1_id = mysql_data["account1_id"]
            self.account2_id = mysql_data["account2_id"]
            self.message = elasticsearch_data.get("_source").get("message")
        except Exception as e:
            print(e)