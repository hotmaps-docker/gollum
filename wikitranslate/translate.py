#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
* find all markdown files in specified root
* convert files into html
* translate via API
* all files are sent in one request per target language
* write results back, as html
"""

import requests
import datetime
import werkzeug
import json
import time
import os

# enforce quotas (https://cloud.google.com/translate/quotas) (very naive implementation)
quota_char = 0
quota_limit = 100000
quota_wait = 100

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

if not os.path.exists(config_path):
    raise Exception("%s not found" % config_path)

with open(config_path, "r") as fd:
    config = json.load(fd)

if "auth_type" not in config:
    raise Exception("configuration file (%s) must specify 'auth_type': 'apikey'")


def get_temp_dir():
    tdir = os.path.join(
        "/tmp", "translate", datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )

    if not os.path.exists(tdir):
        os.makedirs(tdir)

    return tdir


def oauth_init(headers):
    # TODO: not implemented
    raise Exception("oauth is not implemented")
    # 1) open in browser:
    # https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=https://developers.google.com/oauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=https://www.googleapis.com/auth/cloud-translation&access_type=offline
    # 2) wait for callback on redirect uri
    # /oauthplayground/?code=4/IAHF5AAuEYtmLlUK8PnbPyqL-d7j3bFJnpuA5mcrc1UAyhgISt4Q9lQhutkehYe1AH3BFrQ82XOovvBstiPS5vI&scope=https://www.googleapis.com/auth/cloud-translation
    # 3) get code from request (2)
    # 4) exchange authorization code for token
    # POST https://developers.google.com/oauthplayground/exchangeAuthCode
    # { code: '4/IAHF5AAuEYtmLlUK8PnbPyqL-d7j3bFJnpuA5mcrc1UAyhgISt4Q9lQhutkehYe1AH3BFrQ82XOovvBstiPS5vI',
    #   token_uri: 'https://www.googleapis.com/oauth2/v4/token' }

    # https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=http://localhost:5555/XXX&prompt=consent&response_type=code&client_id=XXX.apps.googleusercontent.com&scope=https://www.googleapis.com/auth/cloud-translation&access_type=offline

    bearer_token = "TODO"
    headers["Authorization"] = "Bearer %s" % bearer_token
    return headers


def query_string(data):
    if type(data) != dict:
        return ""
    if len(data) == 0:
        return ""
    return "?" + werkzeug.urls.url_encode(data)


def translate(tdict, source_lang, language):
    s_tdict = {}
    for d in tdict:
        sdict = {d: tdict[d]}
        s_tdict[d] = translate_single(sdict, source_lang, language)
    return s_tdict


def translate_single(tdict, source_lang, language):
    global quota_char
    # dont translate source language
    if language == source_lang:
        return tdict

    keys = sorted(tdict.keys())
    o_text_list = []
    for key in keys:
        o_text_list.append(tdict[key])

    data = {
        "q": o_text_list,
        "target": language,
        "format": "html",
        "source": source_lang,
        "model": "nmt",
    }

    query_data = {}

    headers = {"Content-Type": "application/json; charset: utf-8"}

    if config["auth_type"] == "apikey":
        query_data["key"] = config["api_key"]
    elif config["auth_type"] == "oauth":
        headers = oauth_init(headers)
    else:
        raise Exception("auth_type '%s' not implemented" % config["auth_type"])

    URL = "https://translation.googleapis.com/language/translate/v2" + query_string(
        query_data
    )

    quota_char += len(str(data))
    if quota_char >= quota_limit:
        print("Would hit rate limit - waiting %s seconds" % (quota_wait + 5))
        time.sleep(quota_wait + 5)
        print("Resuming after rate limit")
        quota_char = 0

    print("  translating %s -> %s: %s" % (source_lang, language, keys))

    req = requests.post(URL, headers=headers, json=data)
    response = req.json()

    if (
        "error" in response
        and "code" in response["error"]
        and response["error"]["code"] == 403
    ):
        print("Rate limit hit - waiting %s seconds" % (quota_wait + 5))
        time.sleep(quota_wait + 5)
        quota_char = 0
        print("Resuming after rate limit")
        return translate_single(tdict, source_lang, language)

    cnt = 0
    for t in response["data"]["translations"]:
        tdict[keys[cnt]] = t["translatedText"]
        cnt += 1

    return tdict
