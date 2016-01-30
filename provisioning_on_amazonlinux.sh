cd ~
sudo yum install -y gcc gcc-c++ git python postgresql-server postgresql-devel
git clone https://github.com/snakazawa/slack-backup.git
cd slack-backup/
sudo pip install -r requirements.txt
