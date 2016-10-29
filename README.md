slack-backup
============

Slack is great, it would be better if you can easily back-up all Slack chat history into your secured host automatically and help browsing history easily .    
 
### Preinstall Requiments:

- python 2.7
- virtualenv


If you want to test locally, you should install all modules in requirements.txt into your virtualenv. 

### You can use a free hosted service here:

[http://slackbk.herokuapp.com](http://slackbk.herokuapp.com)

Manual Installation
----------------------

### Get your Slack client_id and client_secret

[https://api.slack.com/applications](https://api.slack.com/applications)

Redirect URI(s) is http://\[your_domain\]

### Download provisioning script

    curl -O https://raw.githubusercontent.com/menemy/slack-backup/master/provisioning_on_centos7.sh

### Edit provisioning script

    SLACK_CLIENT_ID=[your_client_id]
    SLACK_CLIENT_SECRET=[your_client_secret]
    DOMAIN=[your_domain]

### Execute provisioning script

    chmod 777 provisioning_on_amazonlinux.sh
    sudo ./provisioning_on_amazonlinux.sh

For restore your history
________________________

### Download archive from

http://my.slack.com/services/export

### Unpack to directory

/usr/local/src/slack-backup/full_history/

### Execute command

python /usr/local/src/slack-backup/manage.py restore_backup

### Don't know heroku & don't have time? I can help you to deploy.

    hong (at) vietnamdevelopers.com

