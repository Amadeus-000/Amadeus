import os,sys

# Amadeusのインポート
# モジュールが含まれるディレクトリの絶対パスを取得
module_dir = os.path.dirname(os.path.abspath("amadeus.py"))
# 絶対パスをシステムパスに追加
sys.path.insert(0, module_dir)
# モジュールをインポート
import amadeus


urls=[
]

for url in urls:
    ins=amadeus.CircleInfo(url)
    ins.download_all('downloads')