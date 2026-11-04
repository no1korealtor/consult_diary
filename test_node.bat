d:
pushd "%~dp0"
python check_syntax.py
node -c main_script.js > node_err.txt 2>&1
popd
pause
