gitchangelog > CHANGELOG.md
pydoc-markdown --build --site-dir=docs
rm -rf mkdocs.yml docs content
mv build/docs/docs .
mv build/docs/mkdocs.yml .
mv build/docs/content .

rm -rf build