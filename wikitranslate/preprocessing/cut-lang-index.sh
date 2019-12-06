#!/bin/bash

for FILE in $1*.md;
do
	if [ "$(grep '<!--- THIS IS A SUPER UNIQUE IDENTIFIER -->' $FILE | cut -c 1)" = "" ]
	then 
		if [ $(grep -n 'View in another language' $FILE | cut -c 1) ]
		then
			head -n $(($(cat $FILE | grep -n 'View in another language' | cut -f 1 -d ':')-1)) $FILE > $FILE.buf
			mv $FILE.buf $FILE
		fi
	fi
done

