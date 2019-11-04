FROM ubuntu:18.04

MAINTAINER Daniel Hunacek <daniel.hunacek@hevs.ch>

ENV DEBIAN_FRONTEND noninteractive

# Install dependencies
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y -q build-essential ruby-full python python-docutils ruby-bundler libicu-dev libreadline-dev libssl-dev zlib1g-dev git-core
RUN apt-get clean
RUN rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# Install gollum
COPY gollum-install.sh .
RUN bash gollum-install.sh

# Install gollum extensions / dependencies
RUN gem install redcarpet github-markdown
RUN gem install omniauth-github github-markup

# Install omnigollum
COPY omnigollum-install.sh .
RUN bash omnigollum-install.sh

# Initialize wiki data
RUN mkdir /root/wikidata
RUN git init /root/wikidata
RUN touch /root/wikidata/home.md

COPY ./config.rb .

# Expose gollum port 80
EXPOSE 80

ENTRYPOINT ["/usr/local/bin/gollum", "/root/wikidata", "--config", "config.rb", "--port", "80"]