#!/bin/bash

LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for FILE in $1*.md;
do
	python3 $LOCATION/preprocess.py $FILE > $FILE.buf
	mv $FILE.buf $FILE
done
