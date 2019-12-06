# Hotmaps wiki

This image offers an easy way to deploy any git-based wiki repository.
Just tell where your wiki is located and it will deploy a web application that allows to edit/add/remove pages. A basic authentication system is preinstalled and can be configured to only allow certain users to make changes to the wiki content.

This wiki uses [gollum](https://github.com/gollum/gollum) and [omnigollum](https://github.com/arr2036/omnigollum).

## Build

``` Dockerfile
docker build -t hotmaps/wiki .
```

## Run

### Run wiki from Dockerfile

- Replace *-e ENV_VARIABLES*
- Replace *-v VOLUMES* to match your wiki and ssh directory

``` Dockerfile
docker run  -d --rm
            -p 80:80
            --name wiki
            -e GITHUB_CLIENT_ID=0123456789
            -e GITHUB_CLIENT_SECRET=0123456789
            -e AUTH_USERS=email1,email2,email3
            -v /path/to/wiki_dir:/root/wikidata
            -v /path/to/ssh_dir:/root/.ssh
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
      - "/path/to/wiki_dir:/root/wikidata"
      - "/path/to/ssh_dir:/root/.ssh"
```

Run docker-compose (in terminal)

``` bash
docker-compose up -d
```

### Configuration

#### Environment variables

Here are the environment variables that you need to configure to make the container work:

- **GITHUB_CLIENT_ID**: OAuth provider app client ID for GitHub
- **GITHUB_CLIENT_SECRET**: OAuth provider app client secret for GitHub
- **AUTH_USERS**: list of user emails separated by a coma (eg. email1,email2,email3)

#### Volumes

Here is the volumes you need to configure:

- **/path/to/wiki_dir**:/root/wikidata (the git repository that gollum will use)

#### Git hooks

Gollum pushes commits automatically using post_commit hook.
In order to push to the git remote you need to configure and register an ssh key.

You need to add two files in the ssh directory:

- id_rsa (your private key)
- id_ras_pub (your public key)

Find more information on how to generate an ssh key and register it to GitHub [here](https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh) (registeration process might slighty defer depending on where your git remote is hosted).

You also need to add a volume to share your ssh key with the container:

- **/path/to/ssh_dir**:/root/.ssh (needed for automatic push)

You will also need to edit the *config.rb* file:

``` ruby
# ./config.rb

# [...]

# Hooks
Gollum::Hook.register(:post_commit, :hook_id) do |committer, sha1|
  system('/root/wikidata/.git/hooks/post-commit')
end
```

Of course you can add any other kind of hooks.

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
