#!/bin/sh

SLACK_CLIENT_ID=xxxxxxxx
SLACK_CLIENT_SECRET=xxxxxxxx
DIR=/usr/local/src/slack-backup
DOMAIN=localhost

# install
sudo yum install -y gcc gcc-c++ git python python-pip
sudo yum install -y uwsgi
#sudo yum install -y postgresql-server postgresql-devel

cd /usr/local/src
sudo git clone https://github.com/menemy/slack-backup.git
cd slack-backup/
sudo pip install -r requirements.txt

# settings
sudo cp slackbackup/settings_local_sample.py slackbackup/settings_local.py
sudo sed -i -E "s/SLACK_CLIENT_ID.*/SLACK_CLIENT_ID = '${SLACK_CLIENT_ID}'/" slackbackup/settings_local.py
sudo sed -i -E "s/SLACK_CLIENT_SECRET.*/SLACK_CLIENT_SECRET = '${SLACK_CLIENT_SECRET}'/" slackbackup/settings_local.py
sudo sed -i -E "s/DOMAIN.*/DOMAIN = 'http:\/\/${DOMAIN}'/" slackbackup/settings_local.py

# migration and crawling
sudo python manage.py migrate
sudo python manage.py parse_channels

# prepare static files
sudo python manage.py collectstatic

# scheduling
sudo touch /etc/cron.d/slackbackup
sudo chmod 777 /etc/cron.d/slackbackup
cat > /etc/cron.d/slackbackup << EOS
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root
HOME=/
*/5 * * * * root python ${DIR}/manage.py parse_channels 1>>${DIR}/logs/parse.log 2>>${DIR}/logs/parse.err.log
EOS
sudo chmod 644 /etc/cron.d/slackbackup

# run
RUN_SCRIPT="/usr/sbin/uwsgi --ini ${DIR}/uwsgi.ini"
sudo chmod 777 /etc/rc.d/rc.local
echo $RUN_SCRIPT >> /etc/rc.d/rc.local
sudo chmod 755 /etc/rc.d/rc.local
sudo sh -c "${RUN_SCRIPT}"
