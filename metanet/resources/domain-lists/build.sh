#!/bin/bash
set -e
cd "$(dirname $BASH_SOURCE[0])"

echo '=> Clean old file'
rm _all.txt

echo '=> Build ads...'
./ads/generate.sh

echo '=> Combining...'
cat */_all.txt | rev | sort | uniq | rev > _all.txt

echo '=> DONE'