# Hotmaps wiki translation tool

## Short tutorial

Install necessary python modules
```
$ ./setup sh
```
Given your gollum wiki lies in `path/to/wiki`
```
$ ./translate_recent.sh path/to/wiki
```
will translate all changes in `path/to/wiki/en/` since the commit with the id which is stored in `path/to/wiki/.commit-id`. If no such file exists, then `git diff` won't find any files at all. You can create such a file by running
```
$ git rev-parse HEAD > .commit-id
```
You can also pass custom commits by just adding them as second argument, e.g. for some commit-id 123
```
$ ./translate_recent.sh path/to/wiki 123
```
Obviously you can also expand other commands using this, e.g.
```
$ ./translate_recent.sh path/to/wiki $(git rev-parse HEAD~3)
```
which would get you the commit id of the third-last commit.

## Description

This tool uses the [Google cloud translation API](https://cloud.google.com/translate/) (`v2`) to translate the [hotmaps wiki](https://github.com/HotMaps/hotmaps_wiki/wiki) from english into as many other european languages as possible.

The wiki is authored in markdown (.md). The translation API cannot directly translate markdown syntax. Therefore the tool transforms the markdown into HTML, which is then translated via the API. A backtransformation is not necessary as the wiki is able to display HTML as well.

Furhter, this tool generates a language index at the bottom of each page as well as an index in Home.md in the root directory of the wiki. The indices are supposed to be handled in an updating manner, such that e.g. having a page, which is already available in English and German, translated to French, will update the language index on the German and English versions with corresponding links to the newly created French version.

## Requirements
* Python 3 with pip
* API key for Google translation API

### Python installation
Create a python virtual environment where dependencies are installed:
```
cd path/to/wikitranslate
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

or just execute
```
./setup.sh
```

### API key
You need an API key for the Google translation API to use it.  
To obtain one, you need an account with Google and a creditcard for billing purposes.

(Possibly) relevant links:

* [Google console](https://console.cloud.google.com/)  
  Via `APIs & Services`, enable `Cloud Translation API`.  
  This should ask you to add a billing method.  
  Once enabled:  
  Anmeldedaten erstellen → API-Schlüssel → evtl. einschränken → put into `config.json`.  

However the current API key should be located in the `config.json`.

## Wiki structure
To support multiple languages easily and conserving language-internal cross referencing, each language gets its own subdirectory in which the pages are saved with the original english name.

* `/Home.md` (generated index of available languages)
* `/en/Home.md` (former `/Home.md`)
* `/en/wiki_page_1.md` (former `wiki_page_1.md`)
* `/en/wiki_page_2.md`
* `/de/Home.md` (translated `/Home.md`)
* `/de/wiki_page_1.md` (translated `wiki_page_1.md`)
* `/de/wiki_page_2.md`
* `...`

Note that the `uploads` and `images` directories are shared by all translations. 

## Usage
The main program is `wiki_translate.py`, which does the actual translation and some text processing like e.g. updating the language indices. The `translate_recent.sh` script is basically an out-of-the box script for translating most recent changes from english to any other desired language. Changes are being tracked using git diff and a commit-id which by default is stored in `.commit-id`. In order to call `translate_recent.sh` on a wiki, which we suppose to be a git repository in some directory `path/to/wiki`, do
```
./translate_recent.sh path/to/wiki
```
This will check for some commit-id stored in `path/to/wiki/.commit-id`, get all recently changed filenames from `path/to/wiki/en/` and translate them using the python script. Afterwards the translated and updated files are being committed, `.commit-id` is being set to the id of the latest commit, then `.commit-id` is being committed.

## Code structure
* `translate_recent.sh`
  bash script for automatically getting recent changes and translating only those recently changed files.
* `wiki_translate.py`:  
  main entry point and tool logic
* `translate.py`:  
  Google translation API interface
* `docx_translate.py`:  
  not used for wiki translation but may serve as starting point when translating docx and pdf files
* `lang.py`:  
  language codes as understood by translation API
* `config.json`:  
  configuration file. see `config.json.example`. Contains authentication details for the translation API
* `templates/`:  
  Markdown templates for index and language selection
* `preprocessing/`:
  different scripts for preprocessing the original markdown files from the github wiki since directory structure and other stuff changes when migrating the wiki to gollum.
