#!/bin/bash
# setup.sh
# Turns a stock Ubuntu 16 install into a gallery host

if (( $EUID != 0)); then
	echo "This script requires superuser permissions.  Please run:"
	echo "sudo source setup.sh"
	exit
fi

# Install prerequisite software
apt-get update
apt-get install nginx python-dev python-pip

pip install virtualenv

# Create gallery user to run everything
id -u "gallery" &>/dev/null || useradd gallery
usermod -a -G www-data gallery

# Create directory to hold everything

mkdir /web
cd /web

# Setup virtualenv for /web/gallery
virtualenv gallery
source gallery/bin/activate; pip install uwsgi;deactivate

# make sure gallery:www-data owns /web/gallery
chown -R gallery:www-data /web/gallery

# Configure uWSGI in virtualenv
cat << EOF > gallery.ini
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

# Restart services
systemctl start nginx
systemctl enable nginx
