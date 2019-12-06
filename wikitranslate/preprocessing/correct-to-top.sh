#!/bin/bash

for FILE in $1*.md
do
	sed -i 's/<code><ins>\*\*[][]To Top[][](#table-of-contents)\*\*<\/ins><\/code>/\[**`To Top`**\](#table-of-contents)/g' $FILE
done
