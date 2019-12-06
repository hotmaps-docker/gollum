#!/bin/bash

LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo $LOCATION

if [ $1 ]
then
	AT=$1
else
	AT="."
fi

echo "cd $AT"
cd $AT
echo "$LOCATION/change-filename.sh"
$LOCATION/change-filename.sh 

echo "$LOCATION/set-h1.sh"
$LOCATION/set-h1.sh 

echo "$LOCATION/anchors-to-lower.sh"
$LOCATION/anchors-to-lower.sh 

echo "$LOCATION/cut-lang-index.sh"
$LOCATION/cut-lang-index.sh 

echo "$LOCATION/correct-linkage.sh"
$LOCATION/correct-linkage.sh 

echo "$LOCATION/correct-to-top.sh"
$LOCATION/correct-to-top.sh

echo "$LOCATION/hardlinks.sh"
$LOCATION/hardlinks.sh
