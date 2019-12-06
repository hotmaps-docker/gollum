#!/bin/bash

# process each file once
for FILE in $1*.md; 
do
	if [ $(echo $FILE | awk -F'/' '{ print $NF }' | cut -c 1) != "_" ] && \
		[ $(head -n 1 $FILE | head -c 4 | cut -f 1 -d ' ') != "<h1>" ] 
	then
		HEADER=$(echo $FILE | awk -F '/' '{ print $NF }')

		# render header from file name by replacing '-' with space ...
		HEADER=$(echo $HEADER | awk -F '-' '{ for (i=1; i <= NF; i++) { printf $i" "} }')

		# ... and truncating file extension
		HEADER=$(echo $HEADER | awk -F '.' '{ print $1 }')
	
		# insert header to file in first line
		sed -i "1i <h1>${HEADER}<\/h1>\n" $FILE 
	
		# fix stupid unicode character which appears out of nowhere. 
		# check with vim $FILE, if there's a <feff> before the original text of the file
		sed -i 's/\xEF\xBB\xBF//g' $FILE
	fi
done;
