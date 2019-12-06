#!/bin/bash

for FILE in $1*.md;
do
	FILE=$(echo $FILE | awk -F '/' '{ print $NF }')	
	FIRST=$(echo $FILE | cut -c 1-3)
	if [ $FIRST == "en-" ]
	then
		NEW_FILE=$(echo $FILE | cut -c 4-)
		mv "$1$FILE" "$1$NEW_FILE"
	fi
done
