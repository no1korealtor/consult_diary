d:
pushd "%~dp0"
node -c test_syntax.js > js_err.txt 2>&1
type js_err.txt
popd
pause
