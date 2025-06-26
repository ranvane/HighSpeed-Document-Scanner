# HighSpeed-Document-Scanner
开源的高拍仪程序


打包命令：

nuitka main_app.py   --mingw64   --standalone   --onefile   --show-progress   --windows-console-mode=disable   --include-module=wx._xml   --include-data-dir=models=models   --output-dir=out



nuitka main_app.py \
 --mingw64 \
 --standalone \
 --onefile \
 --show-progress \
 --windows-console-mode=disable \
 --include-module=wx._xml \
 --include-data-files=HighSpeed-Document-Scanner.png=. \
 --include-data-files=HighSpeed-Document-Scanner.ico=. \
 --include-data-dir=models=models \
 --output-dir=out

nuitka main_app.py \
 --mingw64 \
 --standalone \
 --onefile \
 --show-progress \
 --windows-console-mode=disable \
 --include-module=wx._xml \
 --include-data-files=HighSpeed-Document-Scanner.png=. \
 --include-data-files=HighSpeed-Document-Scanner.ico=. \
 --include-data-dir=models=./models \
 --output-dir=out