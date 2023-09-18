import requests
from bs4 import BeautifulSoup
import re,os,time,random,json
import jaconv
import urllib.request
from pathlib import Path

# m4a_tools
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class VersionInfo:
    def __init__(self):
        self.version='4.0.0'
        print('Amadeus '+self.version)

class WorkInfo:
    def __init__(self,url=''):
        print(url)
        category=(url.split('/')[-1].split('.')[0])[0:2] in ['RJ','VJ']
        self.sale_now=not ('announce' in url.split('/') )
        response = self.get_res_obj(url)
        if(category and self.sale_now and response):
            soup = BeautifulSoup(response.text, "html.parser")
            self.url=url
            self.work_id=url.split('/')[-1].split('.')[0]
            self.title=self.get_title(soup)
            self.get_detail(soup)
            self.imgurl=self.get_imgurl(soup)
            self.description=self.get_description(soup)
            self.sample_url=self.get_sampleurl(soup)
        else:
            self.url=''
            self.work_id=''
            self.title=''
            self.circle=''
            self.circle_url=''
            self.release_date=''
            self.cv=[]
            self.scenario=[]
            self.adult=''
            self.type=[]
            self.genres=[]
            self.imgurl=''
            self.description=''
            self.sample_url=''
        self.confidence=100.0
        self.maintext=''
        self.remark=''
        print('WorkInfo コンストラクタを生成しました。')

    def modify_url(self,url):
        ind=url.find('.html')
        url_new=url[:ind+5]+'/?locale=ja_JP'
        return url_new

    def get_res_obj(self,url):
        #urlからレスポンスオブジェクトを取得する
        #正常に取得できなかったときはもう一度だけ取得する
        response = requests.get(self.modify_url(url))
        print("status_code : {0}".format(response.status_code))
        if(int(response.status_code)!=200):
            print("60秒後に再接続します...")
            time.sleep(60)
            response = requests.get(self.modify_url(url))
            if(int(response.status_code)!=200):
                print(self.modify_url(url))
                print("DLsiteから作品情報の取得に失敗しました。")
                self.status_code=response.status_code
                return False
        self.status_code=response.status_code
        return response
    
    def remove_end_spaces(self,str):
        if(str==''):
            return ''
        if(str[0]==' ' or str[0]=='　' or str[0]=='\n'):
            str=str[1:]
            str=self.remove_end_spaces(str)
        if(str[-1]==' ' or str[-1]=='　' or str[-1]=='\n'):
            str=str[:-1]
            str=self.remove_end_spaces(str)
        return str
    def get_title(self,soup):
        elems=soup.find('h1',attrs={'id':'work_name'})
        title=self.remove_end_spaces(elems.string)
        return title
    def get_detail(self,soup):
        self.cv=[]
        self.scenario=[]
        self.genres=[]
        self.type=[]
        self.lang=[]
        elem_tr=soup.find("div",id='work_right_inner').find_all('tr')
        for tr in elem_tr:
            # print(tr.find('th'))
            if( (tr.find('th')).text=='販売日'):
                self.release_date=self.remove_end_spaces(tr.find('td').text)
                # print(self.release_date)
            if( (tr.find('th')).text=='年齢指定'):
                self.adult=self.remove_end_spaces(tr.find('td').text)
                # print(self.adult)
            if( (tr.find('th')).text=='作品形式'):
                for type in tr.find('td').find_all('a'):
                    (self.type).append(self.remove_end_spaces(type.text))
                # print(self.type)
            if( self.remove_end_spaces((tr.find('th')).text) in ['サークル名','ブランド名','出版社名']):
                self.circle=self.remove_end_spaces(tr.find('td').find('a').text)
                self.circle_url=self.remove_end_spaces(tr.find('td').find('a')['href'])
                # print(self.circle)
                # print(self.circle_url)
            if( (tr.find('th')).text in ['作者','シナリオ','著者']):
                for x in (tr.find('td').text).split('/'):
                    self.scenario.append(self.remove_end_spaces(x))
            if( (tr.find('th')).text=='声優'):
                cvs=(tr.find('td').text).split('/')
                for cv in cvs:
                    if(cv!=''):
                        self.cv.append(self.remove_end_spaces(cv))
                # print(self.cv)
            if( (tr.find('th')).text=='ジャンル'):
                genres=(tr.find('td').text).split('\n')
                for g in genres:
                    if(g!=''):
                        self.genres.append(self.remove_end_spaces(g))
                # print(self.genres)
            if( (tr.find('th')).text=='対応言語'):
                for lang in tr.find('td').find_all('a'):
                    self.lang.append(self.remove_end_spaces(lang.text))
                # print(self.lang)


    def get_imgurl(self,soup):
        elems=soup.find("picture").find("source")
        img_url=elems['srcset']
        return img_url
    def get_description(self,soup):
        elems=soup.find("div",attrs={'itemprop':'description'})
        description=elems.get_text()

        # 改行を統一する
        description=re.sub('\r\n','\n',description)
        # 先頭の改行を削除する
        description=self.remove_top_newline(description)
        return description
    def get_sampleurl(self,soup):
        dw_link=''
        elems=soup.find('a',attrs={'class':'btn_trial'})
        if(elems):
            dw_link=elems['href']
            dw_link='https:' + dw_link
        return dw_link
    def write2txt(self,filepath):
        #入力されたパスにテキストファイルで作品情報を書き出す。
        with open(filepath+'info.txt','w',encoding='utf-8')as f:
            f.write('title@:'+self.title+'\n')
            f.write('circle@:'+self.circle+'\n')
            f.write('circle_url@:'+self.circle_url+'\n')
            f.write('release_date@:'+self.release_date+'\n')
            if(self.scenario):
                f.write('scenario@:'+'///'.join(self.scenario)+'\n')
            if(self.cv):
                f.write('cv@:'+'///'.join(self.cv)+'\n')
            if(self.adult):
                f.write('adult@:'+self.adult+'\n')
            if(self.type):
                f.write('type@:'+self.type+'\n')
            if(self.genres):
                f.write('genres@:'+' '.join(self.genres)+'\n')
            f.write('url@:'+self.url+'\n')
            f.write('img_url@:'+self.imgurl+'\n')
            f.write('confidence@:'+str(self.confidence)+'\n')
            f.write('description_separate_point\n')
            f.write(self.description)
        print('Complete writing a txt.')

    def initialize_by_txt(self,txt):
        for x in txt.splitlines():
            if(x.split('@:')[0]=='title'):
                self.title=self.remove_end_spaces(x.split('@:')[1])
            if(x.split('@:')[0]=='circle'):
                self.circle=self.remove_end_spaces(x.split('@:')[1])
            if(x.split('@:')[0]=='circle_url'):
                self.circle_url=self.remove_end_spaces(x.split('@:')[1])
            if(x.split('@:')[0]=='release_date'):
                self.release_date=self.remove_end_spaces(x.split('@:')[1])
            if(x.split('@:')[0]=='scenario'):
                self.scenario=x.split('@:')[1].split('///')
            if(x.split('@:')[0]=='adult'):
                self.adult=x.split('@:')[1]
            if(x.split('@:')[0]=='type'):
                self.type=x.split('@:')[1].split('///')
            if(x.split('@:')[0]=='cv'):
                self.cv=x.split('@:')[1].split('///')
            if(x.split('@:')[0]=='genres'):
                self.genres=x.split('@:')[1].split(' ')
            if(x.split('@:')[0]=='url'):
                self.url=x.split('@:')[1]
                self.work_id=self.url.split('/')[-1].split('.')[0]
            if(x.split('@:')[0]=='img_url'):
                self.imgurl=x.split('@:')[1]
            if(x.split('@:')[0]=='confidence'):
                self.confidence=float( x.split('@:')[1] )
        self.description=txt.split('description_separate_point')[-1]
    
    def download_sample(self,dirpath):
        circle=self.circle
        if(re.search('[\/:*?"<>|.]',circle)):
            circle=re.sub('[\/:*?"<>|.]','',circle)
            circle=circle+'_edited'
        os.makedirs(os.path.join(dirpath,circle),exist_ok=True)
        if('ボイス・ASMR'==self.type):
            if(self.sample_url):
                filename=os.path.basename(self.sample_url)
                self.download_file_urllib(self.sample_url, os.path.join(dirpath,circle,filename) )
                print('Download '+filename)
                return os.path.join(dirpath,circle,filename)
            else:
                ins=m4a_tools(self.url)
                if(ins.chobit_url!=''):
                    ins.download(os.path.join(dirpath,circle))
                    return 'm4a'
                else:
                    os.makedirs(os.path.join(dirpath,circle,self.work_id+'_trial'),exist_ok=True)
                    return 'fail'
        else:
            return 'Not_voice'
    def download_sample_direct(self,dirpath):
        os.makedirs(os.path.join(dirpath),exist_ok=True)
        m4a=m4a_tools(self.url)
        if(m4a.chobit_url):
            m4a.download(os.path.join(dirpath))
            return 'm4a'
        else:
            if(self.sample_url):
                filename=os.path.basename(self.sample_url)
                self.download_file_urllib(self.sample_url, os.path.join(dirpath,filename) )
                return os.path.join(dirpath,filename)
            else:
                os.makedirs(os.path.join(dirpath,self.work_id+'_trial'),exist_ok=True)
                return 'fail'
    def download_file_urllib(self,url,dir):
        # urllib.request.urlretrieveでファイルをダウンロードする
        # 失敗したときもう一度だけダウンロードを試みる
        try:
            urllib.request.urlretrieve(url, dir)
        except:
            print('Retry download')
            print(url)
            time.sleep(60)
            urllib.request.urlretrieve(url, dir)

    def remove_top_newline(self,text):
        if(text==''):
            return text
        if(text[0]=='\n'):
            return self.remove_top_newline(text[1:])
        elif(text[0:2]=='\r\n'):
            return self.remove_top_newline(text[2:])
        else:
            return text



    def print_workinfo(self,show_desc=False):
            print('URL : {0}\n'.format(self.url) )
            print('work_id : {0}\n'.format(self.work_id) )
            print('title : {0}\n'.format(self.title) )
            print('circle : {0}\n'.format(self.circle) )
            print('release_date : {0}\n'.format(self.release_date) )
            print('CV : {0}\n'.format(self.cv) )
            print('scenario : {0}\n'.format(self.scenario) )
            print('adult : {0}\n'.format(self.adult) )
            print('type : {0}\n'.format(self.type) )
            print('genres : {0}\n'.format(self.genres) )
            print('language : {0}\n'.format(self.lang))
            print('imgurl : {0}\n'.format(self.imgurl) )
            print('sample_url : {0}\n'.format(self.sample_url) )
            print('sale_now : {0}'.format(self.sale_now))
            if(show_desc):
                print('description : {0}\n'.format(self.description) )

class CircleInfo:
    def __init__(self,url):
        self.url=url
        response = requests.get(url+'/show_type/3')
        soup = BeautifulSoup(response.text, "html.parser")

        self.circle=self.get_circleName(soup)
        self.totalworks=self.get_totalworks(soup)
        self.urls=self.get_list_workurls(soup)

    def print(self):
        print('サークル名 : '+self.circle)
        print('URL : :'+self.url)
        print('作品数 : '+str(self.totalworks))
        print('作品URLリスト : ')
        print(self.urls)
    
    def remove_end_spaces(self,str):
        if(str==''):
            return ''
        if(str[0]==' ' or str[0]=='　' or str[0]=='\n'):
            str=str[1:]
            str=self.remove_end_spaces(str)
        if(str[-1]==' ' or str[-1]=='　' or str[-1]=='\n'):
            str=str[:-1]
            str=self.remove_end_spaces(str)
        return str
    
    def download_all(self,dirpath):
        circle=self.circle
        if(re.search('[\/:*?"<>|.]',circle)):
            circle=re.sub('[\/:*?"<>|.]','',circle)
            circle=circle+'_edited'
        os.makedirs(os.path.join('downloads',circle),exist_ok=True)
        
        self.sample=[]
        self.m4a=[]
        self.not_voice=[]
        self.fail=[]

        print('Download starting the '+ self.circle)
        for url in self.urls:
            time.sleep(random.randint(15,30))
            w1=WorkInfo(url)
            dl_status=w1.download_sample(dirpath)
            if(dl_status=='sample'):
                (self.sample).append(url)
            elif(dl_status=='m4a'):
                (self.m4a).append(url)
            elif(dl_status=='not_voice'):
                (self.not_voice).append(url)
            else:
                (self.fail).append(url)

        self.write_download_info(dirpath)

        num=int(len(self.sample))+int(len(self.m4a))+int(len(self.not_voice))+int(len(self.fail))
        if(self.totalworks!=num):
            print('ERROR')
            print('サークルの作品数とダウンロードした作品数が合いません。')
            print('作品数{0},ダウンロード作品数{1}'.format(self.totalworks,num))
    
    def write_download_info(self,dirpath):
        circle=self.circle
        if(re.search('[\/:*?"<>|.]',circle)):
            circle=re.sub('[\/:*?"<>|.]','',circle)
            circle=circle+'_edited'
        with open(os.path.join(dirpath,circle,'dl_info.txt'),'w',encoding='utf-8') as f:
            f.write('sample : {0}\n'.format(len(self.sample)))
            [f.write(i+'\n') for i in self.sample]
            f.write('\nm4a : {0}\n'.format(len(self.m4a)))
            [f.write(i+'\n') for i in self.m4a]
            f.write('\nnot_voice : {0}\n'.format(len(self.not_voice)))
            [f.write(i+'\n') for i in self.not_voice]
            f.write('\nfail : {0}\n'.format(len(self.fail)))
            [f.write(i+'\n') for i in self.fail]
        print('Download end '+ self.circle)
    
    #以下はインスタンスから呼び出さない
    def get_circleName(self,soup):
        elems=soup.find("strong",attrs={'class':'prof_maker_name'})
        try:
            circle=self.remove_end_spaces(elems.get_text())
        except AttributeError:
            # サークルが存在しないとき
            circle='サークルが存在しません'
        return circle
    def get_totalworks(self,soup):
        try:
            elems=soup.find("div",attrs={"class":"page_total"})
            elems=elems.find("strong")
            totalworks=int(elems.get_text())
        except AttributeError:
            totalworks=0
        return totalworks
    def get_list_workurls(self,soup):
        urls=[]
        pagenum=-(-self.totalworks//50)
        for i in list( range(1, pagenum+1)):
            if(i==1):
                elems = soup.find_all('dd',attrs={'class':'work_name'})
            else:
                response = requests.get(self.url+'/show_type/3/page/{0}'.format(i))
                soup = BeautifulSoup(response.text, "html.parser")
                elems = soup.find_all('dd',attrs={'class':'work_name'})
            
            for elem in elems:
                urls.append( elem.find('a')['href'] )
        
        #print(self.totalworks==len(urls))
        return urls

class m4a_tools:
    def __init__(self,url):
        self.url=url
        self.work_id=url.split('/')[-1].split('.')[0]+'_trial'
        self.chobit_url=self.get_chobit_url(self.url)
        print("m4a_tools コンストラクタが呼ばれました")
        
    def download(self,dirpath):
        os.makedirs(os.path.join(dirpath,self.work_id),exist_ok=True)
        m4a_urls=self.get_m4a_urls(self.chobit_url)
        for i in m4a_urls:
            filename=i.split('/')[-1]
            self.download_file_urllib(i, os.path.join(dirpath,self.work_id,filename))
            print('Download {0}'.format(filename))

    def download_file_urllib(self,url,dir):
        # urllib.request.urlretrieveでファイルをダウンロードする
        # 失敗したときもう一度だけダウンロードを試みる
        try:
            urllib.request.urlretrieve(url, dir)
        except:
            print('Retry download')
            print(url)
            time.sleep(60)
            urllib.request.urlretrieve(url, dir)


    def get_chobit_url(self,url):

        #url='https://www.dlsite.com/maniax/work/=/product_id/RJ381003.html'

        #立ち上げ時の制約（Option）の定義
        ChromeOptions = webdriver.ChromeOptions()
        #これがエラーをなくすコードです。ブラウザ制御コメントを非表示化しています
        ChromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
        #これがエラーをなくすコードです。WebDriverのテスト動作をTrueにしています
        ChromeOptions.use_chromium = True
        #ヘッドレスモード
        ChromeOptions.add_argument('--headless')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=ChromeOptions)
        # driver = webdriver.Chrome('Amadeus/chromedriver_win32/chromedriver',options=ChromeOptions)
        driver.get(url)
        #driver.find_element_by_class_name('btn_yes').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        elems=soup.find_all('iframe',attrs={'src':re.compile(r'.*')})
        chobit_url=''
        for e in elems:
            #print(e['src'])
            if(re.search('chobit.cc',e['src'])):
                chobit_url=e['src']

        print(chobit_url)

        #html書き出し
        # with open('selenium_test.html','w',encoding='utf-8') as f:
        #     f.write(str(html))
        print('Complete extracting chobit url ')

        return chobit_url

    def get_m4a_urls(self,chobit_url):
        urls=[]
        try:
            response = requests.get(chobit_url)
            soup = BeautifulSoup(response.text, "html.parser")
            elems = soup.find_all('li')
            for e in elems:
                urls.append(e['data-src'])
            #print(urls)
            if(urls==[]):
                elems2=soup.find("video")
                elems2=elems2.find_all("source")
                for e in elems2:
                    # print(e)
                    # print(e['src'])
                    tmp=[]
                    if((e['src'].split('.'))[-1] in ['mp4','m4a']):
                        tmp.append(e['src'])
                urls.append(tmp[-1])
                print(urls)
        except requests.exceptions.MissingSchema:
            print('m4aがありません。')
        except AttributeError:
            print('mp4,m4aがありません。')
        return urls
        
class ModifyText:
    def __init__(self,text=''):
        self.text=text
        self.maru_pattern = re.compile(r'●|○|◯|〇|☆|★|◎')
 
        # description
        self.replace_rn2n()
        self.replace_question()
        self.text=self.remove_top_newline(self.text)
        self.convert2hira()
        self.text_conv=self.replace_fuseji(self.text_conv)


    def replace_fuseji(self,text):
        maru_list=['●','○','◯','〇','☆','★','◎']
        fuseji_dict={
            'マ●コ':'マンコ',
            'ま●こ':'まんこ',
            'まん●':'まんこ',
            'お●んこ':'おまんこ',
            'オ●ンコ':'オマンコ',
            'マン●':'マンコ',
            'チ●ポ':'チンポ',
            'ち●ぽ':'ちんぽ',
            'お●んぽ':'おちんぽ',
            'オ●ンポ':'オチンポ',
            'チ●コ':'チンコ',
            'ち●こ':'ちんこ',
            'ちん●':'ちんこ',
            'チン●':'チンコ',
            'チ●チン':'チンチン',
            'ち●ちん':'ちんちん',
            'オ●ンチン':'オチンチン',
            'お●んちん':'おちんちん',
            'ちん●ん':'ちんちん',
            'セッ●ス':'セックス',
            'せっ●す':'せっくす',
            'レ●プ':'レイプ',
            '●K':'JK',
            'ザー●ン':'ザーメン',
        }
        for fuseji in fuseji_dict:
            for maru in maru_list:
                replacement_moji=fuseji.replace('●',maru)
                text=text.replace(replacement_moji,fuseji_dict[fuseji])

        return text
                
    def convert2hira(self):
        # text=repr(text_input)
        # text=re.sub(r'\\u3000',' ',text) #removing zenkaku space
        # clean_text=eval(text)
        self.text_conv=jaconv.kata2hira(self.text)
    def replace_rn2n(self):
        self.text=re.sub('\r\n','\n',self.text)
    def replace_question(self):
        self.text=re.sub('？','?',self.text)
    def remove_top_newline(self,text):
        if(text==''):
            return text
        if(text[0]=='\n'):
            return self.remove_top_newline(text[1:])
        elif(text[0:2]=='\r\n'):
            return self.remove_top_newline(text[2:])
        else:
            return text

class DlsiteTools:
    def __init__(self):
        pass
    def get_workurls(self,year,month,day):
        # 指定した日付の作品のURLを取得
        # 登録されていないサークルの作品があったときは、そのサークルの全作品を取得する
        workurls=[]
        # サークルのIDを取得
        circle_id_list=requests.get('https://woxram-api.com/search/getcircleid/').json()

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
                circleinfo=CircleInfo(circle_url)
                workurls.extend(circleinfo.urls)

        print('作品数')
        print(len(workurls))
        self.workurls=workurls
        return workurls

