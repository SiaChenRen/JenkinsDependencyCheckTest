import uuid
import time
import pymysql.cursors

from flask import current_app as app, session
from werkzeug.security import check_password_hash, generate_password_hash

from app.mail import send_verification_email


class MySQLDAO:

    def __init__(self):
        self.db = pymysql.connect(
            host = app.config["MYSQL_HOST"],
            user = app.config["MYSQL_USER"],
            password = app.config["MYSQL_PASSWORD"],
            database = app.config["MYSQL_DB"],
            cursorclass = pymysql.cursors.DictCursor
        )

    #  Authentication method
    def user_exists(self, email):
        cursor = self.db.cursor()
        sql = "SELECT email FROM accounts WHERE email=%s"
        cursor.execute(sql, (email))
        result = cursor.fetchone()

        if result is not None:
            return True
        else:
            return False

    def admin_access(self, userId):
        cursor = self.db.cursor()
        sql = "SELECT account_id FROM accounts WHERE account_id=%s AND role = 'admin'"

        cursor.execute(sql, (userId))
        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False

    def mod_access(self, userId):
        cursor = self.db.cursor()
        sql = "SELECT account_id FROM accounts WHERE account_id=%s AND role = 'mod'"

        cursor.execute(sql, (userId))
        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
    

    def user_id_exists(self, userId):
        cursor = self.db.cursor()
        sql = "SELECT account_id FROM accounts WHERE account_id=%s"
        cursor.execute(sql, (userId))
        result = cursor.fetchone()

        if result is not None:
            return True
        else:
            return False


    def generate_account_id(self):
        account_id = None
        cursor = self.db.cursor()
        sql = "SELECT email FROM accounts WHERE account_id=%s"
        
        while account_id is None:
            # generate uuid
            account_id = uuid.uuid4().hex

            # check for existing uuid
            cursor.execute(sql, (account_id,))
            result = cursor.fetchone()
            if result is not None:
                account_id = None
        
        return account_id


    def authenticate(self, email, password):
        cursor = self.db.cursor()
        sql = "SELECT account_id, email, password, role, status FROM accounts WHERE email = %s"

        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        if user is None:
            return [False, "Invalid Email/Password."]

        validatePasswordStatus = check_password_hash(user["password"], password)
        if validatePasswordStatus is False:
            return [False, "Invalid Email/Password."]

        if user["status"] == "ban" or user["status"] == "deleted":
            return [False, "User account has been banned/deleted. Please contact the administrator."]

        print(user["status"])
        if user["status"] == "unverified":
            return [False, "Please verify your account. A verification link has been sent to your email."]

        session.clear()
        session["user"] = user["account_id"]
        session["role"] = user["role"]
        return [True, "Successfully logged in."]


    def register(self, email, password):
        cursor = self.db.cursor()
        account_id = self.generate_account_id()
        sql = "INSERT INTO accounts (account_id, email, password) VALUES (%s, %s, %s)"

        try:
            cursor.execute(sql, (account_id, email, generate_password_hash(password)))
            self.db.commit()
            token = self.create_token(account_id, "verify account")[1]
            send_verification_email(email, account_id, token)
            return True
        except Exception as e:
            print(e)
            return False


    def verify_account(self, userId):
        cursor = self.db.cursor()
        sql = "UPDATE accounts SET status = 'verified' WHERE account_id = %s"

        try:
            cursor.execute(sql, (userId,))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    
    # create token for actions that require 2FA
    def create_token(self, user_id, type):
        cursor = self.db.cursor()

        # delete existing token if any
        self.delete_token(user_id, type)

        sql = "INSERT INTO otp (account_id, token, type) VALUES (%s, %s, %s)"
        error = "Error in creating token."
        token = uuid.uuid4().hex

        try:
            cursor.execute(sql, (user_id, token, type))
            self.db.commit()
            return [True, token]

        except Exception as e:
            print(e)
            return [False, error]

    
    # verify that token and account is valid for action to be performed
    def verify_token(self, userId, token, type):
        cursor = self.db.cursor()
        sql = "SELECT timestamp FROM otp WHERE account_id=%s AND token=%s AND type=%s"
        error = "Error in performing action."
        tokenExpiry = app.config["TOKEN_DURATION"]

        try:
            cursor.execute(sql, (userId, token, type))
            result = cursor.fetchone()
            
            if result is None:
                return [False, error]

            # check if token has expired
            elapsedTime = time.time() - result["timestamp"].timestamp()
            if elapsedTime > tokenExpiry:
                error = "Token expired"
                return [False, error]

            self.delete_token(userId, type)
            return [True, "Successfully verified token"]

        except Exception as e:
            return [False, error]


    def delete_token(self, userId, type):
        cursor = self.db.cursor()
        sql = "DELETE FROM otp WHERE account_id=%s AND type=%s"
        error = "Error in performing action."

        try:
            cursor.execute(sql, (userId, type))
            self.db.commit()

            if cursor.rowcount == 1 :
                return True
            return False

        except Exception as e:
            return [False, error]


    # User Data methods
    def get_user_email(self, userId):
        cursor = self.db.cursor()
        sql = "SELECT email FROM accounts WHERE account_id=%s"

        cursor.execute(sql, (userId))
        result = cursor.fetchone()
        if result is not None:
            return [True, result.get("email")]
        return [False, "Error occurred while trying to retrieve user email."]
         

    def check_existing_email(self, new_email):
        cursor = self.db.cursor()
        sql = "SELECT email FROM accounts WHERE email =%s"

        cursor.execute(sql, (new_email))
        result = cursor.fetchone()
        if result is not None:
            return True
        return False


    def update_email(self, userId, new_email):
        cursor = self.db.cursor()
        sql = "UPDATE accounts SET email = %s, status = 'unverified' WHERE account_id = %s"

        cursor.execute(sql, (new_email, userId))
        self.db.commit()
        if cursor.rowcount == 1 :
            return True
        return False

    
    def check_current_password(self, user_id, current_password):
        cursor = self.db.cursor()
        sql = "SELECT password FROM accounts WHERE account_id = %s"

        cursor.execute(sql, (user_id))
        result = cursor.fetchone()

        if result is not None:
            password = result.get("password")
        return check_password_hash(password, current_password)


    def update_password(self, user_id, new_password):
        cursor = self.db.cursor()
        sql = "UPDATE accounts SET password = %s WHERE account_id = %s"

        cursor.execute(sql, (generate_password_hash(new_password), user_id))
        self.db.commit()
        if cursor.rowcount == 1 :
            return True
        return False


    # General Post methods
    def generate_post_id(self):
        post_id = None
        cursor = self.db.cursor()
        sql = "SELECT post_id FROM posts WHERE post_id=%s"
        
        while post_id is None:
            # generate uuid
            post_id = uuid.uuid4().hex

            # check for existing uuid
            cursor.execute(sql, (post_id,))
            result = cursor.fetchone()
            if result is not None:
                post_id = None
        
        return post_id


    def create_post(self):
        cursor = self.db.cursor()
        sql = "INSERT INTO posts (account_id, post_id) VALUES (%s, %s)"
        post_id = self.generate_post_id()

        try:
            cursor.execute(sql, (session["user"], post_id))
            self.db.commit()

            if cursor.rowcount == 1 :
                return [True, post_id]
            return [False, "Error in creating post."]
        except Exception as e:
            print(e)
            return [False, "Error in creating post."]


    def retrieve_post(self, post_id):
        cursor = self.db.cursor()
        sql = "SELECT * FROM posts WHERE post_id = %s AND status='Active'"

        try:
            cursor.execute(sql, (post_id))
            post_data = cursor.fetchone()

            if post_data is None:
                return [False, "Post not found."]

            return [True, post_data]
        except Exception as e:
            print(e)
            return [False, "Error occurred while trying to retrieve post data."]
    
    
    def retrieve_post_pagination(self, page_number, post_limit):
        cursor = self.db.cursor()
        sql = "SELECT * FROM posts WHERE status = 'active' LIMIT %s,%s"
        try:
            cursor.execute(sql, (page_number*post_limit, post_limit))
            post_data = cursor.fetchall()

            if post_data is None:
                return [False, "Posts not found."]
            
            return [True, post_data]
        except Exception as e:
            print(e)
            return [False, "Error occurred while trying to retrieve post data."]
    

    def retrieve_all_active_post(self):
        cursor = self.db.cursor()
        sql = "SELECT * FROM posts WHERE status = 'active'"
        try:
            cursor.execute(sql)
            post_data = cursor.fetchall()

            if post_data is None:
                return [False, "Posts not found."]

            return [True, post_data]
        except Exception as e:
            print(e)
            return [False, "Error occurred while trying to retrieve post data."]


    def retrieve_number_of_post(self):
        cursor = self.db.cursor()
        sql = "SELECT COUNT(*) as numOfPost FROM posts WHERE status = 'active'"

        try:
            cursor.execute(sql)
            post_data = cursor.fetchall()

            if post_data is None:
                return [False, "No posts found."]
            
            return [True, post_data[0]]
        except Exception as e:
            print(e)
            return [False, "Error occurred while trying to retrieve number of post."]


    # Account post methods
    def retrieve_account_post_list(self, account_id):
        cursor = self.db.cursor()
        sql = "SELECT * FROM posts WHERE status = 'active' AND account_id = %s"
        try:
            cursor.execute(sql, (account_id))
            post_data = cursor.fetchall()

            if post_data is None:
                return [False, "Posts not found."]
            
            return [True, post_data]
        except Exception as e:
            print(e)
            return [False, "Error occurred while trying to retrieve post data."]


    def edit_post(self, account_id, post_id):
        cursor = self.db.cursor()
        sql = "SELECT count(*) as user_count FROM posts WHERE status = 'active' AND account_id = %s AND post_id = %s"
        try:
            cursor.execute(sql, (account_id, post_id))
            post_data = cursor.fetchall() 
            if post_data[0].get("user_count") < 1 or post_data[0].get("user_count") > 1:
                return [False, "Posts not found."]
            return [True]
        except Exception as e:
            print(e)
            return [False, "Error occurred while trying to edit post data."]
        

    def delete_post(self, account_id, post_id):
        cursor = self.db.cursor()
        sql = "SELECT count(post_id) as user_count FROM posts WHERE status = 'active' AND account_id = %s AND post_id = %s"
        update_sql = "UPDATE posts SET status = 'deleted' WHERE account_id = %s AND post_id = %s"

        try:
            cursor.execute(sql, (account_id, post_id))
            post_data = cursor.fetchone()

            if post_data is None:
                return [False, "Error in deleting post."]

            cursor.execute(update_sql, (account_id, post_id))
            self.db.commit()
            
            if cursor.rowcount == 1:
                return [True, "Successfully deleted the post."]

            return [False, "Error in deleting post."]
        except Exception as e:
            print(e)
            return [False, "Error occurred while trying to retrieve post data."]


    # Direct messaage
    def generate_message_id(self):
        message_id = None
        cursor = self.db.cursor()
        sql = "SELECT message_id FROM direct_messaging WHERE message_id=%s"
        
        while message_id is None:
            # generate uuid
            message_id = uuid.uuid4().hex

            # check for existing uuid
            cursor.execute(sql, (message_id))
            result = cursor.fetchone()
           
            if result is not None:
                message_id = None
        
        return message_id


    def send_message(self, account1_id, account2_id):
        cursor = self.db.cursor()
    
        sql = "INSERT INTO direct_messaging (message_id, account1_id, account2_id) VALUES (%s, %s, %s)"
        message_id = self.generate_message_id()

        try:
            cursor.execute(sql , (message_id, account1_id, account2_id))
            result = cursor.fetchone()
            self.db.commit()

            return [True, message_id]
        except Exception as e:
            print(e)
            return [False, "Error occured while trying to send message"]

        return [False, "Error occured while trying to send message"]


    def retrieve_message(self, account1_id, account2_id):
        cursor = self.db.cursor()
        sql = "SELECT * FROM direct_messaging WHERE (account1_id = %s AND account2_id = %s) OR (account1_id = %s AND account2_id = %s) ORDER BY created_on ASC"
        
        try:
            cursor.execute(sql, (account1_id, account2_id, account2_id, account1_id))
            message_data = cursor.fetchall()

            if message_data is None:
                return [False, "No message found."]

            return [True, message_data]
        except Exception as e:
            print(e)
            return [False, "Error occured while trying to retrieve message data"]
        [False,  "Error occured while trying to retrieve message data"]


    def retrieve_conversation_list(self, account_id):
        cursor = self.db.cursor()
        sql = "SELECT DISTINCT account1_id, account2_id FROM direct_messaging WHERE account1_id = %s OR account2_id = %s"
        try:
            cursor.execute(sql, (account_id, account_id))
            conversation_data = cursor.fetchall()
            if conversation_data is None:
                return [False, "No conversaton found."]
            return [True, conversation_data]

        except Exception as e:
            print(e)
            return [False, "Error occured while trying to retrieve message data"]
 

    # Adminstrator Methods
    def retrieve_all_user(self):
        cursor = self.db.cursor()
        sql = "SELECT account_id, email, role, status, created_on FROM accounts"
        try:
            cursor.execute(sql)
            user_data = cursor.fetchall()
            if user_data is None:
                return [False, "No user found."]
            return [True, user_data]
        except Exception as e:
            print(e)
            return [False, "Error occured while trying to retrieve message data"]


    def make_moderator(self, account_id):
            cursor = self.db.cursor()
            sql = "UPDATE accounts SET role = 'mod' WHERE account_id = %s"

            try:
                cursor.execute(sql, (account_id))
                self.db.commit()
                if cursor.rowcount == 1 :
                    return True
                return False
            except Exception as e:
                print(e)
                return [False, "Error occured while trying to update moderator"]


    def remove_moderator(self, account_id):
            cursor = self.db.cursor()
            sql = "UPDATE accounts SET role = 'user' WHERE account_id = %s"

            try:
                cursor.execute(sql, (account_id))
                self.db.commit()
                if cursor.rowcount == 1 :
                    return True
                return False
            except Exception as e:
                print(e)
                return [False, "Error occured while trying to update moderator"]


    # Moderator/Admin Methods
    def retrieve_all_post(self):
        cursor = self.db.cursor()
        sql = "SELECT * FROM posts"

        try:
            cursor.execute(sql)
            post_data = cursor.fetchall()

            if post_data is None:
                return [False, "No post found."]
            return [True, post_data]
        except Exception as e:
            print(e)
            return [False, "Error occured while trying to retrieve post data"]


    def remove_post(self, post_id):
        cursor = self.db.cursor()
        sql = "DELETE FROM posts WHERE post_id = %s"

        try:
            cursor.execute(sql,(post_id))
            self.db.commit()

            if cursor.rowcount == 1 :
                return True
            return False

        except Exception as e:
            print(e)
            return [False, "Error occured while trying to retrieve post data"]
    

    def retrieve_nonadmin_user(self):
        cursor = self.db.cursor()
        sql = "SELECT * FROM accounts WHERE role != 'admin'"

        try:
            cursor.execute(sql)
            user_data = cursor.fetchall()
            if user_data is None:
                return [False, "No post found."]
            return [True, user_data]
        
        except Exception as e:
            print(e)
            return [False, "Error occured while trying to retrieve post data"]


    def request_user_ban(self, account_id):
        cursor = self.db.cursor()
        sql = "UPDATE accounts SET status = 'request ban' WHERE account_id = %s"

        try:
            cursor.execute(sql, (account_id))
            self.db.commit()
            if cursor.rowcount == 1 :
                return True
            return False
        except Exception as e:
            print(e)
            return [False, "Error occured while trying to request user ban"]


    def morderator_undo_ban_request(self, account_id):
        cursor = self.db.cursor()
        sql = "UPDATE accounts SET status = 'unverified' WHERE account_id = %s"

        try:
            cursor.execute(sql, (account_id))
            self.db.commit()
            if cursor.rowcount == 1 :
                return True
            return False
        except Exception as e:
            print(e)
            return [False, "Error occured while trying to request user ban"]




    





    