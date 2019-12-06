#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import translate
import lang
import sys
import os
import subprocess


def check_libreoffice():
    PATH = os.environ["PATH"]
    for path in PATH.split(":"):
        if os.path.exists(os.path.join(path, "libreoffice")):
            return True
    return False


def execute(source, dest_dir, source_lang, target_lang, format):
    LOGFILE = "/tmp/log"
    TEMPDIR = translate.get_temp_dir()
    print("working directory:", TEMPDIR)

    errors = 0
    oks = 0

    with open(LOGFILE, "w") as fd:
        fd.write("")

    def call(args):
        print(" ".join(args))
        with open(LOGFILE, "a") as log:
            log.write("\n# %s\n" % " ".join(args))
            ret = subprocess.call(args, stdout=log, stderr=log)
        return ret

    ext = format

    o_basename, _ = os.path.splitext(source)
    o_basename = os.path.basename(o_basename)
    # dest_fn = o_basename
    dest_fn = "%s.%s" % (o_basename, ext)

    intermediate_html_file = os.path.join(TEMPDIR, "%s.html" % dest_fn)
    args = [
        "libreoffice",
        "--convert-to",
        "html:XHTML Writer File:UTF8",
        "--convert-images-to",
        "png",
        "--outdir",
        TEMPDIR,
        source,
    ]
    call(args)
    s_html, _ = os.path.splitext(os.path.basename(source))
    s_html += ".html"
    s_html = os.path.join(TEMPDIR, s_html)
    os.rename(s_html, intermediate_html_file)

    with open(intermediate_html_file, "r") as fd:
        intermediate_html = fd.read()
    o_tdict = {"0": intermediate_html}

    for tl in target_lang:
        t_tdict = translate.translate(o_tdict, source_lang, tl)

        translated_html = t_tdict["0"]
        translated_html_file = os.path.join(TEMPDIR, "%s-%s.html" % (dest_fn, tl))
        with open(translated_html_file, "w") as fd:
            fd.write(translated_html)

        outfile = os.path.join(dest_dir, "%s-%s.%s" % (dest_fn, tl, ext))

        if ext.lower() == "docx":
            args = [
                "libreoffice",
                "--convert-to",
                "odt",
                "--outdir",
                TEMPDIR,
                translated_html_file,
            ]
            call(args)

            odt_filename = os.path.join(
                TEMPDIR, os.path.basename(translated_html_file)[:-5] + ".odt"
            )
            args = [
                "libreoffice",
                "--convert-to",
                "docx",
                "--outdir",
                dest_dir,
                odt_filename,
            ]
            ret = call(args)
        elif ext.lower() == "odt":
            args = [
                "libreoffice",
                "--convert-to",
                "odt",
                "--outdir",
                dest_dir,
                translated_html_file,
            ]
            ret = call(args)
        elif ext.lower() == "pdf":
            # TODO: try libreoffice pdf printer
            # args = ["weasyprint", translated_html_file, outfile]
            args = [
                "libreoffice",
                "--convert-to",
                "pdf",
                "--outdir",
                dest_dir,
                translated_html_file,
            ]
            ret = call(args)
        else:
            raise Exception("invalid extension: '%s'" % ext)

        print("%s: " % outfile, end="")

        if ret == 0:
            oks += 1
            print("OK")
        else:
            errors += 1
            print("ERROR")
    if errors > 0:
        print("%s errors reported. See %s for details" % (errors, LOGFILE))
    else:
        print("Translated %s documents" % oks)
    return 0


if __name__ == "__main__":

    if not check_libreoffice():
        print("Error: libreoffice executable not found")
        sys.exit(1)

    parser = argparse.ArgumentParser()

    parser.add_argument("source")
    parser.add_argument("destdir", default=os.getcwd())

    parser.add_argument("--format", "-f", default="pdf")

    parser.add_argument("--source-lang", "-s", default="en")
    parser.add_argument(
        "--target-lang", "-t", default=lang.default_languages, nargs="+"
    )

    args = parser.parse_args()

    source = os.path.abspath(args.source)
    if not os.path.isdir(args.destdir):
        print("%s does not exist" % args.destdir)
        sys.exit(1)

    if not os.path.exists(args.source):
        print("%s does not exist" % args.source)
        sys.exit(1)

    sys.exit(
        execute(
            args.source, args.destdir, args.source_lang, args.target_lang, args.format
        )
    )
