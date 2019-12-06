#!/bin/bash

for FILE in $(ls $1*.md | grep -v '_'); 
do 
	# remove hardlinks to github wiki pages, leaving relative links
	sed -i 's/https:\/\/github.com\/HotMaps\/hotmaps_wiki\/wiki\///g' $FILE; 

	# change github image hardlinks to relative links
	sed -i 's/https:\/\/github.com\/HotMaps\/hotmaps_wiki\/blob\/master\/Images/..\/images/g' $FILE;
done;

