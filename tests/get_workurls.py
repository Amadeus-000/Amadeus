import os,re,time,sys
import requests
from bs4 import BeautifulSoup

# Amadeusのインポート
# モジュールが含まれるディレクトリの絶対パスを取得
module_dir = os.path.dirname(os.path.abspath("amadeus.py"))
# 絶対パスをシステムパスに追加
sys.path.insert(0, module_dir)
# モジュールをインポート
import amadeus


def get_workurls(year,month,day):
    # 指定した日付の作品のURLを取得
    # 登録されていないサークルの作品があったときは、そのサークルの全作品を取得する
    workurls=[]
    # サークルのIDを取得
    circle_id_list=requests.get('https://woxram.com/django/api/getcircleid/').json()

    # url='https://www.dlsite.com/maniax/new/=/date/2023-05-07/work_type_category/voice/'
    url='https://www.dlsite.com/maniax/new/=/date/{0}-{1:02}-{2:02}/work_type_category/voice/'.format(year,month,day)
    print(url)

    # スクレイピング
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    div_works=soup.find_all("div", class_="n_worklist_item")


    # urlを収集
    for work in div_works:
        url=work.find("dt", class_="work_name").find("a").get("href")
        circle_url=work.find("dd", class_="maker_name").find("a").get("href")
        circle_id=circle_url.split('/')[-1].split('.')[0]
        print(url)
        print(circle_id)

        if(circle_id in circle_id_list):
            print('サークルIDが登録されています')
            workurls.append(url)
        else:
            print('サークルIDが登録されていません')
            circleinfo=amadeus.CircleInfo(circle_url)
            workurls.extend(circleinfo.urls)

    print('作品数')
    print(len(workurls))
    return workurls

print(get_workurls(2023,5,8))