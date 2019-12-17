# git config
git config --global user.email $GIT_USER_EMAIL
git config --global user.name $GIT_USER_NAME

# run
service cron start
/usr/local/bin/gollum /root/wikidata --config config.rb --port 80
