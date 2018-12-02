
# Linux Server Configuration Project:

Public IP Address: 35.177.8.190\
SSH Port: 2200\
URL to hosted application: http://35.177.8.190

## Steps Taken & Software Installation Process:

## 1. Create a Lightsail instance using Amazon Web Services (https://lightsail.aws.amazon.com/)
An instance of UBuntu Linux was chosen (OS Only) - the details were as follows:\
Hostname: Funky-London-1\
Public IP Address: 35.177.8.190\
User name: ubuntu\
Then use the link on the AWS website to SSH into the server.
I saved the default private key in my local directory on my local machine and referenced it when logging in using the command below:

ssh -i /Users/hamza/Programming/linuxservers/LightsailDefaultKey-eu-west-2.pem ubuntu@35.177.8.190

## 2. Update all packages:
sudo apt-get update

## 3. Create the user 'grader':
sudo adduser grader
(password entered = grader)

Give them sudo access rights with the following command:
sudo visudo\
Then paste this below "root    ALL=(ALL:ALL) ALL" in the opened file (using nano editor)
grader  ALL=(ALL:ALL) ALL

## 4. Change SSH port from 22 to 2200:
On the Amazon Lightsail page - under Networking and Firewall add a "Custom" application that accepts connections on Port 2200\
Next use:
sudo nano /etc/ssh/sshd_config\
Then edit the file for the correct the ssh settings:

\# What ports, IPs and protocols we listen for\
\# Port 22\
Port 2200

\# Authentication:\
LoginGraceTime 120\
PermitRootLogin prohibit-password\
PermitRootLogin no\
StrictModes yes\

Use the command:\
sudo systemctl restart ssh\
This restarts ssh on ubuntu and going forward the only way to ssh on is to use the port 2200

## 5. Create grader public/private key combo:
On local machine use the command:\
ssh-keygen
This will create a pair of keys which I have called 'graderkey' and 'graderkey.pub'\
A .ssh folder was then created in the follwing directory:
/home/grader/.ssh\
The public key that was just generated 'graderkey.pub' was pasted into a new file called authorized_keys (using nano)\
The grader user is now able to login using the following command:\
ssh grader@35.177.8.190 -p 2200 -i graderkey

## 6. UFW configuration:
Apply the following commands:\
sudo ufw default deny incoming\
sudo ufw default allow outgoing\

Allow the ports we will need:\
sudo ufw allow ssh\
sudo ufw allow 2200/tcp\
sudo ufw allow www\
sudo ufw allow 123/udp

Make the firewall active:\
sudo ufw enable

Configure the timezone to UTC:\
sudo dpkg-reconfigure tzdata\
Pick "UTC"

## 7. Install and configure Apache to serve a Python mod_wsgi app:
Install Apache with:\
sudo apt-get install apache2\
If you visit http://35.177.8.190 this should now produce the default Apache page\
Install mod_wsgi with:\
sudo apt-get install libapache2-mod-wsgi\
sudo apt-get install python-dev\
Creation and configuration of the wsgi file will occur in step 14.

## 8. Install Git:
sudo apt-get install git

## 9. Install Dependencies for the Flask Application:
sudo apt-get install python-pip\
sudo apt-get install python-flask\
sudo apt-get install python-sqlalchemy\
sudo apt-get install python-psycopg2\
sudo pip install oauth2client\
sudo pip install requests\
sudo pip install httplib2

## 10. Install PostGreSql:
Install PostGreSql:\
sudo apt-get install postgresql

## 11. Clone the github repo of the flask application from GitHub:
sudo git clone https://github.com/Hzizzle/catalog.git catalog

## 12. Create the PostGreSql database along with a new user 'catalog':
Change directory to the catalog directory in which the flask app has been cloned\
Login to database server with postgres username:\
sudo su - postgres\
Run psql:\
psql\
Create a new user 'catalog' with the password 'catalog' and then create my main database 'recipecatalog.db':\
CREATE USER catalog WITH PASSWORD 'catalog';\
ALTER USER catalog CREATEDB;\
CREATE DATABASE recipecatalog WITH OWNER catalog;\
Protect the database recipecatalog by only allowing the user catalog to change it:\
Connect to the database:\
\c recipecatalog\
REVOKE ALL ON SCHEMA public FROM public;\
GRANT ALL ON SCHEMA public TO catalog;\
Quit Postgres and return to Ubuntu as ubuntu user\
Run the 2 python files to actually populate the database with the correct tables and some preliminary data:\
sudo python database_setup.py\
sudo python CreateCuisines.py

## 13. Create the WSGI file:
While still in the catalog directory (/var/www/catalog) run:\
sudo touch catalog.wsgi\
sudo nano catalog.wsgi\
Type the following:\

import sys\
import logging

logging.basicConfig(stream=sys.stderr)\
sys.path.insert(0, '/var/www/catalog')\

from application import app as application\
application.secret_key='super_secret_key'

## 14. Create a apache2 config file:
cd /etc/apache2/sites-available/\
sudo touch catalog.conf\
sudo nano catalog.conf\
Then type up the following in the file:\

<VirtualHost \*:80>\
     ServerName  35.177.8.190\
     ServerAdmin email address\
     #Location of the catalog WSGI file\
     WSGIScriptAlias / /var/www/catalog/catalog.wsgi\
     #Allow Apache to serve the WSGI app from our catalog directory\
     <Directory /var/www/catalog>\
          Order allow,deny\
          Allow from all\
     </Directory>\
     #Allow Apache to deploy static content\
     <Directory /var/www/catalog/static>\
        Order allow,deny\
        Allow from all\
     </Directory>\
      ErrorLog ${APACHE_LOG_DIR}/error.log\
      LogLevel warn\
      CustomLog ${APACHE_LOG_DIR}/access.log combined\
</VirtualHost>

## 15. Adjust my application.py file so that it doesn't run in debug mode and it references the correct directories for user authentication:
Change:\

if __name__ == '__main__':\
    app.secret_key = 'super_secret_key'\
    app.debug = True\
    app.run(host='0.0.0.0', port=8000, threaded=False)\

to the following:\

if __name__ == '__main__':\
    app.run()\

Change:\
client_secrets.json\
to\
/var/www/catalog/client_secrets.json

## 16. Restart Apache and Server should now be running
sudo service apache2 restart\

List of sources used to do this:\
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps\
Udacity Full Stack Nano Degree lectures - particularly "Linux Security" from the 4th section of the course\
Harushimo's github: https://github.com/harushimo/linux-server-configuration (used as a guide on the postgresql database setup)\
First 10 mins of this explained wsgi background to me: https://www.youtube.com/watch?v=H6Q3l11fjU0\
Parts of this video recommended by Udacity links: https://www.youtube.com/watch?v=HcwK8IWc-a8\
