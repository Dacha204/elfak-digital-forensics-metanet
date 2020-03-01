#!/bin/bash
set -e
cd "$(dirname $BASH_SOURCE[0])"

echo '==> Cleanup previous'
rm -v ext_*.txt
rm -v _all.txt

echo '==> Download: AdAway'
curl -Ss https://adaway.org/hosts.txt | grep -v '#' | grep . | tail -n +3 | awk '{ print $2 }' > ext_ad_away.txt

echo '==> Download: AdGuardDNS'
curl -Ss https://v.firebog.net/hosts/AdguardDNS.txt > ext_ad_guard.txt

echo '==> Download: AnuDeep'
curl -Ss https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt | grep -v '#' | grep . | awk '{ print $2 }' > ext_anudeep.txt

echo '==> Download: Disconnect'
curl -Ss https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt | grep -v '#' | grep . > ext_disconnect.txt


echo '==> Download: EasyList'
curl -Ss https://v.firebog.net/hosts/Easylist.txt > ext_easy_list.txt

echo '==> Combine lists'
cat *.txt | rev | sort | uniq | rev > _all.txt

echo '==> DONE'