# Clone wikitranslate (disabled repository is set to private)
# git clone https://github.com/ripaul/wikitranslate.git /tmp/wikitranslate

DIR="/wikitranslate/"
if [ -d "$DIR" ]; then
    ### Take action if $DIR exists ###
    echo "Installing wikitranslate..."
    # Add crontab file in the cron directory
    mkdir -p /etc/cron.d
    mv /crontab /etc/cron.d/wikitranslate-cron

    # Give execution rights on the cron job
    chmod 0644 /etc/cron.d/wikitranslate-cron

    # Create the log file to be able to run tail
    touch /var/log/cron.log

    # Install wikitranslate dependencies
    bash /wikitranslate/setup.sh

else
    echo "Error: ${DIR} not found. This module won't be installed."
    exit 1
fi
