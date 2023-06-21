Amadeusライブラリの説明

amadeusパッケージはDlsiteのデータを処理する
作品データを収集、正規化、伏せ字解除、サンプルダウンロードすることができる

faureパッケージは作品のメインテキストを処理する
誤字をAIで修正する


インストールコマンド
faure
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
pip install unidic-lite
pip install mecab-python3
pip install sentencepiece
conda install -c conda-forge transformers
pip install jaconv
conda install -c conda-forge spacy
pip install -U ginza ja_ginza_electra

amadeus
conda install -c anaconda beautifulsoup4
conda install -c conda-forge selenium
pip install jaconv
pip install webdriver-manager