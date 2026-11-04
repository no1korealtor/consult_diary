d:
pushd "%~dp0"
python extract_script.py
node -c test_syntax.js > js_error.txt 2>&1
popd
