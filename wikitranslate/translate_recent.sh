#!/bin/bash

HELP="
translate_recent.sh: translate_recent.sh PATH/TO/WIKI [COMMIT-ID]\n
\taim of this script is to call the translate program only on the most\n
\trecently changed files in order to save resources, since every word\n
\ttranslated by the Google API does cost money.\n
\n
\tidea is as follows: \n
\t- use git diff to get all changes since last translation\n
\t- copy them into a seperate directory\n
\t- translate every md file inside this directory\n
\t- copy the translated files as well as the original files, which have\n
\t  appended a language index, back\n
\t- commit changes and save the commit id, such that next time, we can use\n
\t  git diff to identify changed files\n
"
# location of this script

if [ "$1" = "" ]
then
	echo -e $HELP
	exit
fi

### SET UP VARIABLES ###

LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

BASE=$1 		# wiki root directory
ORIGINAL="en" 		# directory which contains original translation
TRANSLATE="translate"	# auxiliary directory
INDEX="Home.md"		# index file where language index gets written to
COMMIT=".commit-id"	# file with git commit from which to get latest changes
COMMIT_ID=$(cat $BASE/$COMMIT)

# Generate .commit-id file
if [ -f "${BASE}/${COMMIT}" ]; then
	echo "${BASE}/${COMMIT} found!"
else
	echo "${BASE}/${COMMIT} not found. Generating..."
	git -C $BASE rev-parse HEAD > ${BASE}/${COMMIT}
fi

# Handle commit ID parameter
if [ $2 ]
then
        COMMIT_ID=$2
fi


# target languages
TARGET_LANGS=(da es fr lt bg hu mt sk fi et ga pt nl el sl ro hr lv sv it cs de pl)	
TARGET_LANGS=(de)

# move into wiki root at BASE, create (or clear) dir with files which are to be translated
echo "moving to $BASE ..."
cd $BASE
BASE=$(pwd)
rm -rf $TRANSLATE
mkdir $TRANSLATE


### IDENTIFY CHANGED FILES ### 

# rather user git commit and git diff for getting most recent changes.
#FILES=$(find $ORIGINAL -maxdepth 1 -mtime -$INTERVAL -type f)
FILES=$(git diff --name-only $COMMIT_ID -- $ORIGINAL/)

if [ "$FILES" = "" ]
then
	echo "no files to translate."
	echo "done."

	exit 0
fi


### COPY FILES INTO SEPERATE DIRECTORY ###

echo "copying files which are to be translated ..."

# get most recent changes in ORIGINAL directory and move them to TRANSLATE
for FILE in $FILES
do	
	cp --parents $FILE $TRANSLATE/
done

cp "$BASE/$INDEX" "$BASE/$TRANSLATE/$INDEX"


echo "copied $(echo $FILES | sed 's/\ /\n/g' | wc -l) files."

### START TRANSLATION ###

# all files which are to be translated are now in TRANSLATE, on which we will now run the translation script
echo "moving to $LOCATION ..."
cd $LOCATION

echo "starting translation ..."
python3 wiki_translate.py "$BASE/$TRANSLATE" --target-lang ${TARGET_LANGS[@]} --alternative-root "$BASE"

echo "translation finished!"


### COPY FILES BACK ###

echo "moving to $BASE/$TRANSLATE ..."
cd "$BASE/$TRANSLATE"
FILES=$(find . -name '*.md')
for FILE in $FILES
do
	DIR=$(echo $FILE |  awk -F "/" '{ for (i=2; i < NF; i++) { printf $i"/"; } }')
	cp --parents $FILE ../
done

cp "$BASE/$TRANSLATE/$INDEX" "$BASE/$INDEX"


### COMMIT CHANGES

cd $BASE

# commit changes
echo "committing translated and changed files ..."
echo "git add ${TARGET_LANGS[@]}"
git add ${TARGET_LANGS[@]}
git commit -am "translated ${#FILES[@]} files into ${#TARGET_LANG[@]} languages."
# set COMMIT to this commit 
git rev-parse HEAD > $COMMIT
git add $COMMIT
git commit -m "added commit id of last translation"

echo "done."

