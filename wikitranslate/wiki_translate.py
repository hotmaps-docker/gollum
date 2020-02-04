#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is the main module of the hotmaps wiki translation tool.
See README.md for installation, usage and a general overview.
"""

import lang
import translate

import cmarkgfm
from jinja2 import Environment, FileSystemLoader

import re
import os
import sys
import traceback
import bs4
import glob
import argparse
import codecs
from collections import OrderedDict

jinja_env = Environment(
    loader=FileSystemLoader("templates"), keep_trailing_newline=True
)

def render_anchor (header):
    # normalize header by replacing space,:,/ by - and dropping brackets. 
    # TODO: this list of disallowed characters should/could be longer.
    header = header.lower().replace(' ','-').replace(':','-').replace('/','-').replace('(','').replace(')','')
    return '<a class="anchor" id="' + header + '" href="#' + header + '"><i class="fa fa-link"></i></a>'

def set_anchors (html_string, take_action = True):
    """
    this function is part of a hack to get page internal linkage working. gollum renders the anchors for 
    all headers itself, after the translation process. this leads to the anchors of the translated headers
    obviously being translated too. however linking sections in text is done explicitly by the text's author
    hence the reference to the anchor already exists before translation. it is however not translated, since
    it is part of the corresponding html tag.

    we solve this issue by adding the anchor in the gollum style ourselves in the html, which is rendered
    from the markdown file. later we use css to hide the gollum-rendered anchor, leaving only our, the 
    correctly working anchor. this function inserts the header anchors in the html.
    """
    if (not take_action):
        return html_string
    
    # all html header tags which are supposed to get an anchor
    tags = [('<h1>', '</h1>'), ('<h2>', '</h2>'), ('<h3>', '</h3>'), ('<h4>', '</h4>'), ('<h5>', '</h5>'), ('<h6>', '</h6>')]

    for _tags in tags:
        # tag: opening tag, ctag: closing tag
        tag = _tags[0]
        ctag = _tags[1]
        
        i = 0
        while i >= 0:
            # get positions of opening and corresponding closing tag
            i = html_string.find(tag, i)
            j = html_string.find(ctag, i)
            
            # if i < 0, there exists none
            if (i < 0):
                break
            
            # if a opneing tag exists, but no closing tag was found, there has to be some error.
            if (i >= 0 and j < 0):
                print("Meh. That's wrong.")
                exit()
            
            # get the header, which is the text between the tags.
            header = html_string[i+len(tag):j]
            # render the anchor
            anchor = render_anchor(header)
            # insert it between the tags
            html_string = html_string[:i + len(tag)] + anchor + header + html_string[j:]
            i = i + len(anchor)

    return html_string

def find_mdfiles(root, source_lang):
    """
    recursively find all *.md files below <root> which
    start with <source_lang> prefix.
    returns found files as list (absolute paths).
    """
    mdfiles = glob.glob(str("%s/" + source_lang + "/*.md") % root, recursive=True)
    return mdfiles


def normalize_soup(soup):
    """
    transforms HTML tags prior translation
    """

    # update <img> src for images
    for img in soup.find_all("img"):
        if "src" in img and img["src"].startswith("images"):
            img["src"] = "../%s" % img["src"]

    return soup


def lang_written_to_dict(lang_written, source_lang):
    """
    returns a dictionary which contains performed translations, e.g.:
    {"de": "German", ...}
    <source_lang> is not contained in the dictionary
    """
    d_lang_written = OrderedDict()
    d_lang_written[source_lang] = lang.languages[source_lang]
    for lw in lang_written:
        if lw == source_lang:
            continue
        d_lang_written[lw] = lang.languages[lw]
    return d_lang_written


def get_already_written (index, start=0, end=-1):
    """
    returns languages, which are already contained in the index
    """
    already_written = []

    with codecs.open(index, 'r', 'utf-8') as fd:
        content = fd.read()[start:end]
        # magic numbers 1 and 3, since language codes are two characters long, 
        # excluding leading slash
        already_written = [content[m+1:m+3] for m in [m.start() for m in re.finditer('/../', content)]]
    
    return already_written

def write_index(index, lang_written, source_lang):
    """
    returns the rendered index template (language selection) as string
    """
    
    template = jinja_env.get_template("index.md")
    d_lang_written = lang_written_to_dict(lang_written, source_lang)

    already_written = get_already_written(index)

    lang_to_write = sorted(list(set(already_written).union(set(d_lang_written) - set(['en']))))
    d_lang_to_write = OrderedDict()
    d_lang_to_write['en'] = lang.languages['en']
    for l in lang_to_write:
        d_lang_to_write[l] = lang.languages[l]

    print(d_lang_to_write)
    with codecs.open(index, "w", "utf-8") as fd:
        fd.write(template.render(languages=d_lang_to_write, source_lang=source_lang))


def execute(root, source_path, source_lang, target_lang, alternative_root = ""):
    """
    translate all md files from <source_path> from <target_lang> to all
    <source_lang> languages, and put them into subfolders of <root>
    """

    returncode = 0
    lang_skipped = []
    lang_written = []

    # read all md files into dictionary after transforming to HTML
    o_tdict = {}
    o_md = {}
    o_title = {}
   
    # get all mdfiles from original version, which is determined by source_lang
    mdfiles = find_mdfiles(source_path, source_lang)
    for mdfile in mdfiles:
        # open the source file which is supposed to be translated.
        # with open(mdfile, "r") as fd:
        #    md = fd.read()
        with codecs.open(mdfile, "r", "utf-8") as fd:
            md = fd.read()

        # parse to html, since Google Translate handles HTML better than MD
        html = cmarkgfm.markdown_to_html(md)
        soup = bs4.BeautifulSoup(html, "html.parser")
        soup = normalize_soup(soup)

        # set_anchors is a small hack for the gollum design wiki. check description
        # of the set_anchors function. by setting set_anchors(..., false) it simply
        # returns the input string.
        o_tdict[mdfile] = set_anchors(str(soup), (os.path.basename(mdfile)[0] != '_'))
        o_md[mdfile] = md
        o_title[mdfile] = (mdfile.split('/')[-1]).replace('-',' ')[:-3]

    # translate into target languages
    for language in target_lang:
        if language in lang_skipped + lang_written:
            continue

        if language not in lang.languages:
            print("Warning: skipped language '%s'" % language)
            lang_skipped.append(language)
            continue
       
        # call Google Translate API
        t_tdict = translate.translate(o_tdict, source_lang, language)

        ## target_root is the directory where the translated files are supposed
        ## to go in. because of github wiki parser, we have to change this. the 
        ## target directory remains the same as the root directory, but we change
        ## the filename later to contain the language prefix in the file title.
        ## note that this leads to another rather ugly situation, where all wiki
        ## pages carry the language prefix in the page title.
        #
        target_root = os.path.join(root, language)
        # target_root = os.path.join(root)
        # print(target_root)
        os.makedirs(target_root, exist_ok=True)

        # write back translations (md files with HTML content)
        for mdfile in t_tdict:
            mdfile_newpath = os.path.join(
                target_root, mdfile.split('/')[-1]
            )
            
            with codecs.open(mdfile_newpath, "w", "utf-8") as fd:
                if language == source_lang:
                    fd.write(o_md[mdfile])
                else:
                    fd.write(t_tdict[mdfile][mdfile])

        lang_written.append(language)

    # append language selection at bottom of each page
    langselect_identifier = "<!--- THIS IS A SUPER UNIQUE IDENTIFIER -->"
    d_lang_written = lang_written_to_dict(lang_written, source_lang)
    template = jinja_env.get_template("langselect.md")
    
    print(lang_written + [source_lang])
    for language in lang_written + [source_lang]:
        for mdfile in o_tdict:
            # skip _Footer.md and _Sidebar.md
            if (os.path.basename(mdfile)[0] == '_'): 
                continue
            # mdfile_newpath is the page we ought to add the footer.
            # mdfile_newpath = os.path.join(target_root, str(language + "-" + os.path.basename(mdfile)[3:]))
            mdfile_newpath = os.path.join(root, language, os.path.basename(mdfile))
            print("changing the following file:" + mdfile_newpath)
            #print(os.path.basename(mdfile.split(".md")[0]))
            
            with codecs.open(mdfile_newpath, "r+", "utf-8") as fd:
                # check if langselect is already contained
                html = fd.read()
                i = html.find(langselect_identifier)
            
            already_written = get_already_written(mdfile_newpath, i)

            # get union of languages already in the index and those which are to be appended. exclude english,
            # because we insert it manually, s.t. it is the first language in the index, whereas the rest
            # gets sorted
            lang_to_write = sorted(list(set(already_written).union(set(d_lang_written) - set(['en']))))
            d_lang_to_write = OrderedDict()
            d_lang_to_write['en'] = lang.languages['en']

            for l in lang_to_write:
                d_lang_to_write[l] = lang.languages[l]

            with codecs.open(mdfile_newpath, "w+", "utf-8") as fd:
                # if it is already contained, truncate it
                if (i >= 0):
                    html = html[:i]
                fd.write(
                    html + template.render(
                        languages=d_lang_to_write,
                        this_lang=language,
                        source_lang=source_lang,
                        page_link=os.path.basename(mdfile.split(".md")[0]),
                    )
                )
            
            update_index = [l for l in already_written]

            for l in update_index:
                mdfile_update = os.path.join(root, l, os.path.basename(mdfile))
                
                if (not(os.path.isfile(mdfile_update)) and alternative_root != ""):
                    mdfile_update = os.path.join(alternative_root, l, os.path.basename(mdfile))
                    if (not(os.path.isfile(mdfile_update))):
                        continue
                
                with codecs.open(mdfile_update, "r+", "utf-8") as fd:
                    # check if langselect is already contained
                    html = fd.read()
                    i = html.find(langselect_identifier)
                
                with codecs.open(mdfile_update, 'w+', 'utf-8') as fd:
                    # if it is already contained, truncate it
                    if (i >= 0):
                        html = html[:i]
                    print("changing the following file:" + mdfile_update)
                    fd.write(
                        html + template.render(
                            languages=d_lang_to_write,
                            this_lang=l,
                            source_lang=language,
                            page_link=os.path.basename(mdfile.split(".md")[0]),
                        )
                    )
                    


    # write language index
    index = os.path.join(root, "Home.md")
    write_index(index, lang_written, source_lang)

    print("wrote index to %s" % index)
    print("Done.")

    # print warnings again at end
    for language in lang_skipped:
        print("Warning: skipped language '%s'" % language)
        returncode = 1

    return returncode


def main():
    try:
        # argparse is used to parse cli arguments
        parser = argparse.ArgumentParser()

        # path argument is called without any flag, it gives us the path to the wiki directory
        # where we supposedly find all the md files
        parser.add_argument("path")

        # this leads to the directory with the original versions. however this is supposed to
        # be changed as the github wiki structure does not allow subdirectories, but all md-
        # files are supposed to be in the root directory. hence, the original language must be 
        # set as file name prefix.
        parser.add_argument(
            "--source-path",
            "-p",
            default=None,
            help="absolute path to originating version. default: <path>/<source-lang>",
        )
        parser.add_argument(
            "--alternative-root",
            "-a",
            default=None,
            help="if copies of files lie at other places too, they might be used as a fallback."
        )
        parser.add_argument("--source-lang", "-s", default="en", help="default: en")
        parser.add_argument(
            "--target-lang",
            "-t",
            default=lang.default_languages,
            nargs="+",
            help="default: %s" % " ".join(lang.default_languages),
        )
        
        args = parser.parse_args()
        if args.source_path is None:
            args.source_path = args.path

        sys.exit(execute(args.path, args.source_path, args.source_lang, args.target_lang, args.alternative_root))
    except:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
