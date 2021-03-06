#!/bin/bash
# setup.sh
# Turns a stock Ubuntu 16 install into a gallery host

set -e

if (( $EUID != 0)); then
	echo "This script requires superuser permissions.  Please run:"
	echo "sudo ./setup.sh"
	exit
fi

if [ -e /web/gallery/secrets.py ] ; then
	echo "This script seems to have already been run.  Exiting..."
	exit
fi

# Install prerequisite software
apt-get update
apt-get -y install nginx python-dev python-pip postgresql libpq-dev

pip install virtualenv

# Create gallery user to run everything
id -u "gallery" &>/dev/null || useradd gallery
usermod -a -G www-data gallery

# Create directory to hold everything
mkdir /web
cd /web

# Setup virtualenv for /web/gallery
virtualenv gallery
source gallery/bin/activate; pip install passlib uwsgi web.py pygresql;deactivate

# Create directory for avatars.
mkdir /web/gallery/avatars

# make sure gallery:www-data owns /web/gallery
chown -R gallery:www-data /web/gallery

# Configure uWSGI in virtualenv
cat << EOF > /web/gallery/gallery.ini
[uwsgi]
module = gallery:application

master = true
processes = 5

uid = gallery
socket = /run/uwsgi/gallery.sock
chown-socket = gallery:www-data
chmod-socket = 664
vacuum = true

die-on-term = true
EOF

# Configure uWSGI in systemd so uWSGI starts automatically
cat << EOF > /etc/systemd/system/gallery.service
[Unit]
Description=uWSGI Gallery Instance

[Service]
ExecStartPre=-/bin/bash -c 'mkdir -p /run/uwsgi; chown gallery:www-data /run/uwsgi'
ExecStart=/bin/bash -c 'cd /web/gallery/; source bin/activate; uwsgi --ini gallery.ini'

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx to point to uWSGI
cat << EOF > /etc/nginx/sites-available/gallery
server {
	listen 80;
	server_name server_domain_or_IP;

	location / {
		include uwsgi_params;
		uwsgi_pass unix:/run/uwsgi/gallery.sock;
	}
}
EOF

ln -s /etc/nginx/sites-available/gallery /etc/nginx/sites-enabled
rm /etc/nginx/sites-enabled/default

# Setup postgre for the gallery
gallerydbpassword=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
gallerydbsalt=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
id -u "gallerydb" &>/dev/null || useradd gallerydb
sudo -u postgres bash -c "psql -c \"CREATE USER gallerydb WITH PASSWORD '$gallerydbpassword';\""
sudo -u postgres bash -c "psql -c \"CREATE DATABASE gallery WITH OWNER=gallerydb;\""
sudo -u postgres bash -c "psql -d gallery -c \"ALTER DATABASE gallery OWNER TO gallerydb;\""
sudo -u postgres bash -c "psql -d gallery -c \"CREATE SCHEMA gallery;\""
sudo -u postgres bash -c "psql -d gallery -c \"GRANT ALL ON SCHEMA gallery TO gallerydb;\""
sudo -u postgres bash -c "psql -d gallery -c \"CREATE TABLE gallery.users (id serial NOT NULL, password character varying(256) NOT NULL, username character varying(128) NOT NULL, admin bool);\""
sudo -u postgres bash -c "psql -d gallery -c \"CREATE TABLE gallery.userflags (id serial NOT NULL, userid integer NOT NULL, flagtype character varying(64) NOT NULL);\""
sudo -u postgres bash -c "psql -d gallery -c \"CREATE TABLE gallery.profiles (id serial NOT NULL, userid integer NOT NULL, screenname character varying(64) NOT NULL, urlname character varying(32) NOT NULL, avatarfile character varying(64) NOT NULL);\""
sudo -u postgres bash -c "psql -d gallery -c \"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gallery TO gallerydb;\""
sudo -u postgres bash -c "psql -d gallery -c \"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA gallery TO gallerydb;\""

sudo mv /etc/postgresql/9.5/main/pg_hba.conf /etc/postgresql/9.5/main/pg_hba.conf.bak
sudo awk '
/# Put your actual configuration here/ {
    print "local gallery gallerydb md5"
}
{ print }
' /etc/postgresql/9.5/main/pg_hba.conf.bak > /etc/postgresql/9.5/main/pg_hba.conf

echo "# secrets.py - created by setup.sh" >> /web/gallery/secrets.py
echo "dbpass = \"$gallerydbpassword\"" >> /web/gallery/secrets.py
echo "dbsalt = \"$gallerydbsalt\"" >> /web/gallery/secrets.py

chown gallery:www-data /web/gallery/secrets.py

# Fetch the gallery application itself.
cd /web/gallery
git init .
git remote add origin https://github.com/almafeta/gallery.git
git pull origin master

# Restart services and add them to the autoplay lists
systemctl start nginx
systemctl enable nginx
systemctl start gallery
systemctl enable gallery
service nginx restart
service postgresql restart

# Final notices
echo "Gallery installed!  Save this information."
echo "gallerydb postgres password set to: $gallerydbpassword"
