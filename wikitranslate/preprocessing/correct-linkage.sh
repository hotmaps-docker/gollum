#!/bin/bash

for FILE in $1*.md;
do
	sed -i 's/](en-/](/' $FILE
done
