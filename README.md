# Hotmaps wiki

This wiki uses [gollum](https://github.com/gollum/gollum) and [omnigollum](https://github.com/arr2036/omnigollum).

## Build

``` Dockerfile
docker build -t hotmaps/wiki . 
```

## Run
### Run wiki from Dockerfile

- Replace *-e ENV_VARIABLES*
- Replace *-v VOLUME* to match your wiki directory

``` Dockerfile
docker run -d --rm 
-p 80:4567 
--name wiki 
-e GITHUB_CLIENT_ID=0123456789 
-e GITHUB_CLIENT_SECRET=0123456789 
-e AUTH_USERS=email1,email2,email3
-v /path/to/wiki_dir:/root/wikidir
hotmaps/wiki
```

### Run wiki from docker-compose

Create *.env* file based on *.env.example*, update environment variables and make the volume point to your wiki directory.

``` yaml
# ./docker-compose.yml

version: '3.2'
services:
  wiki:
    env_file: .env
    build: .
    ports:
      - "80:80"
    volumes:
      - "/path/to/wiki_dir:/root/wikidir"
```
Run docker-compose (in terminal)
``` bash
docker-compose up -d 
```

### Configuration

Here are the environment variables that you need to configure to make the container work:
- **GITHUB_CLIENT_ID**: OAuth provider app client ID for GitHub
- **GITHUB_CLIENT_SECRET**: OAuth provider app client secret for GitHub
- **AUTH_USERS**: list of user emails separated by a coma (eg. email1,email2,email3)

Here is the volume you need to configure to make the container point to your wiki:
- **/path/to/wiki_dir**:/root/wikidir

#### OAuth configuration
For GitHub, you need to create client ID and client secret on GitHub website on the settings page of your account or ogranization, in developer settings, OAuth Apps.

To add another provider you should also edit *config.rb*:

``` ruby
# ./config.rb

# [...]

options = {
  # OmniAuth::Builder block is passed as a proc
  :providers => Proc.new do

    # GitHub
    provider :github, ENV['GITHUB_CLIENT_ID'], ENV['GITHUB_CLIENT_SECRET'],
    
    # LDAP
    provider :ldap,
      :host => '127.0.0.1',
      :port => 389,
      :method => :plain,
      :base => 'dc=example,dc=com',
      :uid => 'uid',
      :bind_dn => 'cn=manager,dc=example,dc=com',
      :password => 'password'
    
    # Twitter
    provider :twitter, 'CONSUMER_KEY', 'CONSUMER_SECRET'
    
    # OpenID
    provider :open_id, OpenID::Store::Filesystem.new('/tmp')  
    
    # others ...

  # [...]
}
```

Omnigollum allows many OAuth providers. You can find more information about this [here](https://github.com/arr2036/omnigollum).

