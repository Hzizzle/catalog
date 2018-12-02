Linux Server Configuration Project:

Steps Taken & Software Installation Process:

1. Create a Lightsail instance using Amazon Web Services (https://lightsail.aws.amazon.com/)
An instance of UBuntu Linux was chosen (OS Only) - the details were as follows:
Hostname: Funky-London-1
Public IP Address: 35.177.8.190
User name: ubuntu
Then use the link on the AWS website to SSH into the server
I saved the default private key in my local directory on my local machine and referenced it when logging in using the command below:

ssh -i /Users/hamza/Programming/linuxservers/LightsailDefaultKey-eu-west-2.pem ubuntu@35.177.8.190

2. Update all packages:
sudo apt-get update

3. Create the user 'grader':
sudo adduser grader
(password entered = grader)

Give them sudo access rights with the following command:
sudo visudo
Then paste this below "root    ALL=(ALL:ALL) ALL" in the opened file (using nano editor)
grader  ALL=(ALL:ALL) ALL

4. Change SSH port from 22 to 2200:
On the Amazon Lightsail page - under Networking and Firewall add a "Custom" application that accepts connections on Port 2200
next use:
sudo nano /etc/ssh/sshd_config
This will edit the file for all the ssh settings

# What ports, IPs and protocols we listen for
# Port 22
Port 2200

# Authentication:
LoginGraceTime 120
PermitRootLogin prohibit-password
PermitRootLogin no
StrictModes yes

Use the command:
sudo systemctl restart ssh
This restarts ssh on ubuntu and going forward the only way to ssh on is to use the port 2200

5. Create grader public/private key combo:
On local machine use the command:
ssh-keygen
This will create a pair of keys which I have called 'graderkey' and 'graderkey.pub'
A .ssh folder was then created in the follwing directory:
/home/grader/.ssh
The public key that was just generated 'graderkey.pub' was pasted into a new file called authorized_keys (using nano)
The grader user is now able to login using the following command:
ssh grader@35.177.8.190 -p 2200 -i graderkey

6. UFW configuration:
Apply the following commands:
sudo ufw default deny incoming
sudo ufw default allow outgoing

Allow the ports we will need:
sudo ufw allow ssh
sudo ufw allow 2200/tcp
sudo ufw allow www
sudo ufw allow 123/udp

Make the firewall active:
sudo ufw enable

Configure the timezone to UTC:
sudo dpkg-reconfigure tzdata
Pick "UTC"

7. Install and configure Apache to serve a Python mod_wsgi app:
Install Apache with:
sudo apt-get install apache2
If you visit http://35.177.8.190 this should now produce the default Apache page
Install mod_wsgi with:
sudo apt-get install libapache2-mod-wsgi
sudo apt-get install python-dev
Creation and configuration of the wsgi file will occur in step 12.

8. Install Git:
sudo apt-get install git

9. Install Dependencies for the Flask Application:
sudo apt-get install python-pip python-flask python-sqlalchemy python-psycopg2
sudo pip install oauth2client requests httplib2

10. Install Database using PostGreSql:
First install PostGreSql:
sudo apt-get install postgresql


11. Clone the github repo of the flask application from GitHub:
