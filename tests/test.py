import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
from app import create_app
from app.auth import validate_email, validate_password, validate_passwords


class Test(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status, '200 OK')


    def test_email_validation(self):
        emails = ['', 'Testing123@gmail.com', 'frozen@gmail.com', 'asdasd2312dsa', 'fro@hotmail.com']

        self.assertEqual([False, 'Please provide a email address.'], validate_email(emails[0]))
        # self.assertEqual([False, 'Please enter a valid email address.'], validate_email(emails[0]))
        # self.assertEqual([True, 'Email is validated'], validate_email(emails[0]))

        # self.assertEqual([False, 'Please provide a email address.'], validate_email(emails[1]))
        #self.assertEqual([False, 'Please enter a valid email address.'], validate_email(emails[1]))
        self.assertEqual([True, 'Email is validated'], validate_email(emails[1]))

        # self.assertEqual([False, 'Please provide a email address.'], validate_email(emails[2]))
        # self.assertEqual([False, 'Please enter a valid email address.'], validate_email(emails[2]))
        self.assertEqual([True, 'Email is validated'], validate_email(emails[2]))

        # self.assertEqual([False, 'Please provide a email address.'], validate_email(emails[3]))
        self.assertEqual([False, 'Please enter a valid email address.'], validate_email(emails[3]))
        # self.assertEqual([True, 'Email is validated'], validate_email(emails[3]))

        # self.assertEqual([False, 'Please provide a email address.'], validate_email(emails[4]))
        # self.assertEqual([False, 'Please enter a valid email address.'], validate_email(emails[4]))
        self.assertEqual([True, 'Email is validated'], validate_email(emails[4]))

    def test_password_validation(self):
        password = ['',
                    'as123@a',
                    'Asdasdasdasdqweqw1234qewfdsadf23423qewfeafewaf12312rfqwesdf23r31fvwesf'
                    '!!E@1e211e1e12e1dscvasvadsavadsvsadvawfq2fq2gvrewvsvazvavavadvwagergw',
                    '!@QWE34RT%6Y']

        self.assertEqual([False, 'Please provide a password.'], validate_password(password[0]))
        # self.assertEqual([False, 'Your length password must be at least 8 characters.'], validate_password(password[0]))
        # self.assertEqual([False, 'Your password length must be below 64 characters.'], validate_password(password[0]))
        # self.assertEqual([True, "Password is validated"], validate_password(password[0]))

        # self.assertEqual([False, 'Please provide a password.'], validate_password(password[1]))
        self.assertEqual([False, 'Your password length must be at least 8 characters.'], validate_password(password[1]))
        # self.assertEqual([False, 'Your password length must be below 64 characters.'], validate_password(password[1]))
        # self.assertEqual([True, "Password is validated"], validate_password(password[1]))

        # self.assertEqual([False, 'Please provide a password.'], validate_password(password[2]))
        # self.assertEqual([False, 'Your password length must be at least 8 characters.'], validate_password(password[2]))
        self.assertEqual([False, 'Your password length must be below 64 characters.'], validate_password(password[2]))
        # self.assertEqual([True, "Password is validated"], validate_password(password[2]))

        # self.assertEqual([False, 'Please provide a password.'], validate_password(password[3]))
        # self.assertEqual([False, 'Your password length must be at least 8 characters.'], validate_password(password[3]))
        # self.assertEqual([False, 'Your password length must be below 64 characters.'], validate_password(password[3]))
        self.assertEqual([True, "Password is validated"], validate_password(password[3]))

    def test_passwords_validation(self):
        passwords = ['',
                     'asda@323rfvre',
                     'as123@a',
                     'Asdasdasdasdqweqw1234qewfdsadf23423qewfeafewaf12312rfqwesdf23r31fvwesf'
                     '!!E@1e211e1e12e1dscvasvadsavadsvsadvawfq2fq2gvrewvsvazvavavadvwagergw',
                     '!234567asdfgh',
                     '!@QWE34RT%6Y']
        confirmedPasswords = ['!@34567qwert',
                              '',
                              'as123@a',
                              'asd',
                              '!234567asdqwe',
                              '!@QWE34RT%6Y']

        self.assertEqual([False, 'Please provide a password.'], validate_passwords(passwords[0], confirmedPasswords[0]))
        # self.assertEqual([False, 'Please provide a confirm password.'], validate_passwords(passwords[0], confirmedPasswords[0]))
        # self.assertEqual([False, 'Your password must be at least 8 characters.'], validate_passwords(passwords[0], confirmedPasswords[0]))
        # self.assertEqual([False, 'Your password must be below 64 characters.'], validate_passwords(passwords[0], confirmedPasswords[0]))
        # self.assertEqual([False, 'Password and confirm password does not match.'], validate_passwords(passwords[0], confirmedPasswords[0]))
        # self.assertEqual([True, "Password is validated"], validate_passwords(passwords[0], confirmedPasswords[0]))

        # self.assertEqual([False, 'Please provide a password.'], validate_passwords(passwords[1], confirmedPasswords[1]))
        self.assertEqual([False, 'Please provide a confirm password.'],
                         validate_passwords(passwords[1], confirmedPasswords[1]))
        # self.assertEqual([False, 'Your password must be at least 8 characters.'], validate_passwords(passwords[1], confirmedPasswords[1]))
        # self.assertEqual([False, 'Your password must be below 64 characters.'], validate_passwords(passwords[1], confirmedPasswords[1]))
        # self.assertEqual([False, 'Password and confirm password does not match.'], validate_passwords(passwords[1], confirmedPasswords[1]))
        # self.assertEqual([True, "Password is validated"], validate_passwords(passwords[1], confirmedPasswords[1]))

        # self.assertEqual([False, 'Please provide a password.'], validate_passwords(passwords[2], confirmedPasswords[2]))
        # self.assertEqual([False, 'Please provide a confirm password.'], validate_passwords(passwords[2], confirmedPasswords[2]))
        self.assertEqual([False, 'Your password must be at least 8 characters.'],
                         validate_passwords(passwords[2], confirmedPasswords[2]))
        # self.assertEqual([False, 'Your password must be below 64 characters.'], validate_passwords(passwords[2], confirmedPasswords[2]))
        # self.assertEqual([False, 'Password and confirm password does not match.'], validate_passwords(passwords[2], confirmedPasswords[2]))
        # self.assertEqual([True, "Password is validated"], validate_passwords(passwords[2], confirmedPasswords[2]))

        # self.assertEqual([False, 'Please provide a password.'], validate_passwords(passwords[3], confirmedPasswords[3]))
        # self.assertEqual([False, 'Please provide a confirm password.'], validate_passwords(passwords[3], confirmedPasswords[3]))
        # self.assertEqual([False, 'Your password must be at least 8 characters.'], validate_passwords(passwords[3], confirmedPasswords[3]))
        self.assertEqual([False, 'Your password must be below 64 characters.'],
                         validate_passwords(passwords[3], confirmedPasswords[3]))
        # self.assertEqual([False, 'Password and confirm password does not match.'], validate_passwords(passwords[3], confirmedPasswords[3]))
        # self.assertEqual([True, "Password is validated"], validate_passwords(passwords[3], confirmedPasswords[3]))

        # self.assertEqual([False, 'Please provide a password.'], validate_passwords(passwords[4], confirmedPasswords[4]))
        # self.assertEqual([False, 'Please provide a confirm password.'], validate_passwords(passwords[4], confirmedPasswords[4]))
        # self.assertEqual([False, 'Your password must be at least 8 characters.'], validate_passwords(passwords[4], confirmedPasswords[4]))
        # self.assertEqual([False, 'Your password must be below 64 characters.'], validate_passwords(passwords[4], confirmedPasswords[4]))
        self.assertEqual([False, 'Password and confirm password does not match.'],
                         validate_passwords(passwords[4], confirmedPasswords[4]))
        # self.assertEqual([True, "Password is validated"], validate_passwords(passwords[4], confirmedPasswords[4]))

        # self.assertEqual([False, 'Please provide a password.'], validate_passwords(passwords[5], confirmedPasswords[5]))
        # self.assertEqual([False, 'Please provide a confirm password.'], validate_passwords(passwords[5], confirmedPasswords[5]))
        # self.assertEqual([False, 'Your password must be at least 8 characters.'], validate_passwords(passwords[5], confirmedPasswords[5]))
        # self.assertEqual([False, 'Your password must be below 64 characters.'], validate_passwords(passwords[5], confirmedPasswords[5]))
        # self.assertEqual([False, 'Password and confirm password does not match.'], validate_passwords(passwords[5], confirmedPasswords[5]))
        self.assertEqual([True, "Password is validated"], validate_passwords(passwords[5], confirmedPasswords[5]))


if __name__ == '__main__':
    unittest.main()
