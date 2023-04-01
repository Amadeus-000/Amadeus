import os,re,time,sys
import zipfile
import requests
from bs4 import BeautifulSoup

# Amadeusのインポート
# モジュールが含まれるディレクトリの絶対パスを取得
module_dir = os.path.dirname(os.path.abspath("amadeus.py"))
# 絶対パスをシステムパスに追加
sys.path.insert(0, module_dir)
# モジュールをインポート
import amadeus


def convert_date_format(date_string):
    # 文字列から年月日を抽出
    year = re.search(r'\d{4}', date_string).group(0)
    month = re.search(r'年(\d{1,2})月', date_string).group(1)
    day = re.search(r'月(\d{1,2})日', date_string).group(1)

    # 数値に変換して結合
    formatted_date = f"{year:0>4}{int(month):0>2}{int(day):0>2}"
    return formatted_date

def zip_extract(zip_path,extract_path):
    encoding='cp932' # Shift-JIS
    zip_ref = zipfile.ZipFile(zip_path, "r")
    for info in zip_ref.infolist():
        # 適切なエンコーディングでファイル名をデコード
        info.filename = info.filename.encode('cp437').decode(encoding)
        zip_ref.extract(member=info, path=extract_path)

    # 引数pathに展開先ディレクトリを指定
    # zip_ref.extractall(extract_path)

    #ZipFileオブジェクトをクローズ
    zip_ref.close()


workurls=[]
new_circle_list=[]

print('ダウンロードするDLsiteのURLを入力してください')
url=input()
# url='https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category%5B0%5D/male/order%5B0%5D/release_d/work_type%5B0%5D/SOU/work_type_name%5B0%5D/%E3%83%9C%E3%82%A4%E3%82%B9%E3%83%BBASMR/options_and_or/and/options%5B0%5D/JPN/options%5B1%5D/NM/per_page/30/show_type/3/lang_options%5B0%5D/%E6%97%A5%E6%9C%AC%E8%AA%9E/lang_options%5B1%5D/%E8%A8%80%E8%AA%9E%E4%B8%8D%E8%A6%81/page/10'

# スクレイピング
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
ul_elem=soup.find('ul',attrs={'id':'search_result_img_box'})
li_elems=ul_elem.find_all('li',attrs={'class':'search_result_img_box_inner'})
for i in li_elems:
    print(i.find('a').get('href'))
    workurls.append(i.find('a').get('href'))

print('作品数')
print(len(workurls))

# サークルのIDを取得
circle_id_list=requests.get('https://woxram.com/api/getcircleid/').json()

# ダウンロード
os.makedirs('downloads',exist_ok=True)
for workurl in workurls:
    time.sleep(1)
    workinfo=amadeus.WorkInfo(workurl)
    print(workinfo.title)
    print(workinfo.release_date)
    print(workinfo.circle_url)
    
    release_data=convert_date_format(workinfo.release_date)
    if(workinfo.circle_url.split('/')[-1].split('.')[0] in circle_id_list):
        print('サークルIDが登録されています')
        downloadpath=workinfo.download_sample_direct('downloads\\'+release_data)
        print(downloadpath)

        # zipファイルの場合は展開
        # if(downloadpath.split('.')[-1]=='zip'):
        #     zip_extract(downloadpath, os.path.dirname(downloadpath)+'/'+os.path.basename(downloadpath).split('.')[0]) 
        
    else:
        print('サークルIDが登録されていません')
        new_circle_list.append('\''+workinfo.circle_url + '\', #' +release_data)

# 新規サークルのリストを保存
with open('downloads\\new_circle_list.txt','a') as f:
    for circle_url in new_circle_list:
        f.write(circle_url + '\n')
