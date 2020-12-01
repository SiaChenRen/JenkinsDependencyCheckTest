import click
import pymysql.cursors

from flask import current_app as app, g
from flask.cli import with_appcontext

from .mysql import *
from .elasticsearch import *
from app.mail import send_verification_email


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = DB()

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    cursor = db.mysql.cursor()

    with app.open_resource("schema.sql") as f:
        sqlFile = f.read().decode("utf8")
        f.close()
        sqlCommands = sqlFile.split(';')

        for command in sqlCommands:
            try:
                if command.strip() != '':
                    cursor.execute(command)
            except IOError as e:
                print("Command skipped: ", e)

    db.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


class DB:

    # Store DAOs
    def __init__(self):
        self.mysql = MySQLDAO()
        self.elasticsearch = ElasticsearchDAO()

    def cursor(self):
        return self.mysql.db.cursor()

    def close(self):
        self.mysql.db.close()
        self.elasticsearch.close()

    # Authentication methods
    def user_exists(self, email):
        return self.mysql.user_exists(email)

    def user_id_exists(self, userId):
        return self.mysql.user_id_exists(userId)

    def admin_access(self, user_id):
        return self.mysql.admin_access(user_id)

    def mod_access(self, user_id):
        return self.mysql.mod_access(user_id)

    def register(self, email, password):
        return self.mysql.register(email, password)

    def login(self, email, password):
        return self.mysql.authenticate(email, password)


    # User Data methods
    def retrieve_email(self, userId):
        return self.mysql.get_user_email(userId)

    def check_existing_email(self, email):
        return self.mysql.check_existing_email(email)
        
    def update_email(self, userId, email):
        return self.mysql.update_email(userId, email)

    def check_current_password(self, userId, currentPassword):
        return self.mysql.check_current_password(userId, currentPassword)

    def update_password(self, userId, newPassword):
        return self.mysql.update_password(userId, newPassword)

    def verify_token(self, userId, token, type):
        return self.mysql.verify_token(userId, token, type)

    def verify_account(self, userId, token):
        result = self.verify_token(userId, token, "verify account")
        if not result[0]:
            return False
        
        return self.mysql.verify_account(userId)
    

    # Post methods
    def create_post(self, title, description, content):
        # Create post data row in mySQL
        mysql_result = self.mysql.create_post()

        # Validate Mysql result
        if mysql_result[0] == False:
            return mysql_result

        # Insert data into elasticSearch (NOSQL)
        nomysql_result = self.elasticsearch.create_post(mysql_result[1], title, description, content)
        return nomysql_result

    def retrieve_post(self, post_id):
        from app.posts.post import Post

        # Check if the post id is valid and status is active from mySQL
        # Retrieve the post id, author, created_on data
        mysql_result = self.mysql.retrieve_post(post_id)
        if mysql_result[0] == False:
            return mysql_result

        # Retrieve title and description fom elasticSearch (NOSQL)
        elasticsearch_result = self.elasticsearch.retrieve_post(post_id)
        if elasticsearch_result[0] is not True:
            return elasticsearch_result

        # Return a POST object with the result found
        return Post(post_id, mysql_result[1], elasticsearch_result[1][0])


    # Retrieve post with the page number and limit
    def retrieve_post_list(self, pageNumber, postLimit):
        from app.posts.post import Post

        mysql_result = self.mysql.retrieve_post_pagination(pageNumber, postLimit)
        if mysql_result[0] is not True:
            return mysql_result
        
        post_list = []

        for item in mysql_result[1]:

            post_id = item.get("post_id")
            elasticsearch_result = self.elasticsearch.retrieve_post(post_id)
            if elasticsearch_result[0] is not True:
                continue
            else:
                for postData in elasticsearch_result[1] :
                    post = Post(post_id, item, postData)
                    post_list.append(post)

        return post_list


    # Retrieve the number of post in database
    def retrieve_number_of_post(self):
        mysql_result = self.mysql.retrieve_number_of_post()

        if mysql_result[0] is not True:
            return mysql_result

        return mysql_result[1].get("numOfPost")
       
    def search_post(self, searchTerm):
        from app.posts.post import Post

        post_list = []
        mysql_result = self.mysql.retrieve_all_active_post()
        if mysql_result[0] is not True:
            return mysql_result

        elasticsearch_result = self.elasticsearch.search_post(searchTerm)
        if elasticsearch_result[0] is not True:
            return elasticsearch_result

        for item in mysql_result[1]:
            for postData in elasticsearch_result[1]:
                if (item.get("post_id") == postData.get("_id")):
                        post = Post(item.get("post_id"), item, postData)
                        post_list.append(post)
       
        return post_list

    def retrieve_account_post_list(self, accountID):
        from app.posts.post import Post

        mysql_result = self.mysql.retrieve_account_post_list(accountID)
        if mysql_result[0] is not True:
            return mysql_result

        post_list = []
        for item in mysql_result[1]:
            post_id = item.get("post_id")
            elasticsearch_result = self.elasticsearch.retrieve_post(post_id)
            if elasticsearch_result[0] is not True:
                continue
            else:   
                for postData in elasticsearch_result[1] :
                    
                    post = Post(post_id, item, postData)
                    post_list.append(post)

        return post_list

    def update_post(self, accountID, postID, title, description):
        mysql_result = self.mysql.edit_post(accountID, postID)
        if mysql_result[0] is not True:
            return [False,"Error in updating post data."]
        return self.elasticsearch.update_post(postID, title, description)

    def delete_post(self, account_id, post_id):
        return self.mysql.delete_post(account_id, post_id)


    # Messaging Method
    def retrieve_messages(self, account1_id, account2_id):
        from app.posts.message import Message
        mysql_result = self.mysql.retrieve_message(account1_id, account2_id)
        message_list = []
        for item in mysql_result[1]:
            message_id = item.get("message_id")
            elasticsearch_result = self.elasticsearch.retrieve_message(message_id)

            if elasticsearch_result[0] is False:
                continue
            else:   
                for message_data in elasticsearch_result[1] :
                    message = Message(message_id, item, message_data)
                    message_list.append(message)
        return message_list
            

    def retrieve_conversation_list(self, account_id):
        return self.mysql.retrieve_conversation_list(account_id)


    def send_message(self, sender_id, recipient_id, message):
        # Insert data into the mySQL
        mysql_message_status = self.mysql.send_message(sender_id, recipient_id)

        if mysql_message_status[0] == False:
            return mysql_message_status
        
        # Insert data into elasticSearch (NOSQL)
        return self.elasticsearch.create_message(mysql_message_status[1], message)


    # Moderator Method
    def moderator_view(self):
        # Import post object
        from app.posts.post import Post

        # Retrieve data from the mySQL
        mysql_post_status = self.mysql.retrieve_all_post()

        # Validate retrieve all post, return error message after retrieve
        if mysql_post_status[0] == False:
            return mysql_post_status

        # Retrieve post data from NOSQL and parsing the data into object
        post_list = []
        for item in mysql_post_status[1]:
            post_id = item.get("post_id")
            elasticsearch_result = self.elasticsearch.retrieve_post(post_id)
            if elasticsearch_result[0] is not True:
                continue
            else:   
                for postData in elasticsearch_result[1] :
                    post = Post(post_id, item, postData)
                    post_list.append(post)

        return post_list

    def moderator_delete_post(self, post_id):
        # Delete post from nosql
        elasticsearch_result = self.elasticsearch.remove_post(post_id)

        if elasticsearch_result == False :
            return elasticsearch_result
        
        # Delete post from sql
        return self.mysql.remove_post(post_id)

    def moderator_view_user(self):
        return self.mysql.retrieve_nonadmin_user()

    def moderator_request_ban(self,account_id):
        return self.mysql.request_user_ban(account_id)

    def morderator_undo_ban_request(self, account_id):
        return self.mysql.morderator_undo_ban_request(account_id)
         

    # Administrator Method
    def administrator_view_user(self):
        return self.mysql.retrieve_all_user()

    def make_moderator(self, account_id):
        return self.mysql.make_moderator(account_id)

    def remove_moderator(self, account_id):
        return self.mysql.remove_moderator(account_id)

    
    # Logging functions
    def log_entry(self, jsonData):
        return self.elasticsearch.send_log(jsonData)
