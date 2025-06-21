rm -r dist/main_app
pyinstaller main_app.spec

cd dist/main_app/
./main_app

