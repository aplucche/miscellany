"""
    gmail_scraper.py
    ~~~~~~~~~~~~~~~~
        Writes email contents to seperate files. Can extract unseen emails or
        all.  Settings allow files to be marked as read or remain unmodified and
        for only specified elements to be extracted (e.g. tables)

        Note: Gmail no longer supports using username and password without
        changing security settings - use OAuth instead.

    Usage::
        Set up Oauth credentials if using gmail. Create config file based on
        example below then run
    Example Config::
        -gmail_scraper.ini

        [email_info]
        LOGIN_METHOD: <oauth | password>
        ;use for oauth login
        CLIENT_KEY: <oauth client key>
        CLIENT_SECRET: <oauth client secret>
        REFRESH_TOKEN: <oauth refresh token>
        ;use for password login
        EMAIL_USERNAME: <username>
        EMAIL_PASSWORD: <password>

        [scraper_settings]
        SEARCH_TYPE: <ALL | (UNSEEN)>
        MARK_AS_READ: <True | False>
        ;EXTRACT_ELEMENT Downloads full text if false
        EXTRACT_ELEMENT: <True | False>
        LOGGING: <True | False>
        DOWNLOAD_DIRECTORY: <dir>
    Setting up OAuth credentials for Gmail::
        Client key and secret can be created using google console here:
            https://console.developers.google.com/apis/credentials
        Download Google's OAuth helper file here:
            https://raw.githubusercontent.com/google/
                                    gmail-oauth2-tools/master/python/oauth2.py
        Follow example at https://github.com/google/gmail-oauth2-tools/
                                                    wiki/OAuth2DotPyRunThrough
          to generate refresh token
            1. run:
                python oauth2.py --generate_oauth2_token 
                        --client_id=<client_id> --client_secret=<client_secret>
            2. follow prompts then copy refresh token to ini file

"""

import imaplib
import csv
from bs4 import BeautifulSoup
import quopri
import ConfigParser
import email
import re
import sys
import logging
import lib.oauth2 as oauth2

#Set up Config and Logging
config = ConfigParser.ConfigParser()
config.read("gmail_scraper.ini")

logging.basicConfig(level=logging.DEBUG)
handler = logging.StreamHandler()
if config.getboolean("scraper_settings", "LOGGING"):
    handler = logging.FileHandler('gmail_scraper.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def main():
    conn = authenticate()
    ids = check_mail(conn)
    for email_id in ids:
        try:
            email_body, email_subject = get_email_by_id(conn, email_id)
            write_email_to_file(email_body, email_subject)
            #table, email_subject = get_table(conn, email_id)
            #write_table_to_csv(table, email_subject)
        except Exception as e:
            logger.error(e, exc_info=True)
    conn.logout()
    pass

def authenticate():
    login_method = config.get("email_info", "LOGIN_METHOD")
    if login_method == 'password':
        EMAIL_USERNAME = config.get("email_info", "EMAIL_USERNAME")
        EMAIL_PASSWORD = config.get("email_info", "EMAIL_PASSWORD")
        conn = imaplib.IMAP4_SSL('imap.gmail.com')
        conn.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    if login_method == 'oauth':
        CLIENT_KEY = config.get("email_info", "CLIENT_KEY")
        CLIENT_SECRET = config.get("email_info", "CLIENT_SECRET")
        username = 'aplucche@gmail.com'
        REFRESH_TOKEN = config.get("email_info", "REFRESH_TOKEN")
        access_token = oauth2.RefreshToken(CLIENT_KEY, CLIENT_SECRET, REFRESH_TOKEN)['access_token']
        auth_string = oauth2.GenerateOAuth2String(username, access_token, base64_encode=False)
        #oauth2.TestImapAuthentication(username, auth_string)
        conn = imaplib.IMAP4_SSL('imap.gmail.com')
        conn.debug = 4
        conn.authenticate('XOAUTH2', lambda x: auth_string)
    else:
        sys.exit('Set login method to oauth or password in gmail_scraper.ini')
    return conn

def check_mail(imap_conn):
    imap_conn.list() # Gives list of labels
    imap_conn.select("INBOX") # connect to gplus label.
    search_type = config.get("scraper_settings", "SEARCH_TYPE")
    result, data = imap_conn.uid('search', None, search_type) # search and return all uids
    #result, data = mail.uid('search', None, '(UNSEEN)') # search and return unseen uids
    ids = data[0].split()
    return ids

def get_email_by_id(conn, uid):
    read_type = '(RFC822)' if config.getboolean("scraper_settings", "MARK_AS_READ") else '(BODY.PEEK[])'
    result, data = conn.uid('fetch', uid, read_type)
    raw_email = data[0][1]
    email_message = email.message_from_string(raw_email)
    email_subject = email_message['Subject'].replace('\n','')
    email_body = ''
    if email_message.is_multipart():
        for payload in email_message.get_payload():
            email_body +=payload
    else:
        email_body = email_message.get_payload()
    #decoded_email = quopri.decodestring(raw_email)
    print email_body
    return email_body, email_subject


def get_table(mail, uid):
    read_type = '(RFC822)' if config.getboolean("scraper_settings", "MARK_AS_READ") else '(BODY.PEEK[])'
    result, data = mail.uid('fetch', uid, read_type)
    raw_email = data[0][1]
    email_message = email.message_from_string(raw_email)
    email_subject = email_message['Subject'].replace('\n','')
    decoded_email = quopri.decodestring(raw_email)
    soup = BeautifulSoup(decoded_email, "lxml")
    table = soup.find_all("tbody")
    if len(table) != 1:
        raise Exception(str(len(table)) + " tables present. Email Subject: " + str(email_subject))
    return table, email_subject

def write_email_to_file(email_body, email_subject):
    """write email to file with subject as filename and body as contents"""
    with open(format_email_subject(email_subject) + '.txt', 'wb') as f:
        for line in email_body:
            f.write(line)        

def write_table_to_csv(table, email_subject):
    for row in table:
        rows = row.find_all("tr")
        logger.info('writing ' + str(len(rows) - 1) + ' titles')
        with open(format_email_subject(email_subject) + '.csv', 'wb') as f:
            writer = csv.writer(f)
            first_row = True
            for r in rows:
                cells = r.find_all("td")
                row_data = [c.get_text().replace('\n', '') for c in cells]
                if first_row:
                    row_data.append("email_subject")
                    first_row = False
                else:
                    row_data.append(email_subject)
                writer.writerow(row_data)
                logger.debug(row_data)
    return

def format_email_subject(email_subject):
    """Formats email subject as filename"""
    safe_chars = "".join([x if x.isalnum() else "_" for x in email_subject])
    remove_extra_underscores = re.sub('_+','_', safe_chars)
    formatted_filename = re.sub('^Fwd_+','', remove_extra_underscores)
    logger.debug(formatted_filename)
    return formatted_filename

if __name__ == '__main__':
    main()
