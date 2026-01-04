git checkout html_layout
git pull
rm -r /tmp/_html_layout
cp -r _html_layout /tmp/_html_layout
git checkout main
rm -r _html_layout/
cp -r /tmp/_html_layout _html_layout
git add .
git commit -m "_html_layout refreshed"