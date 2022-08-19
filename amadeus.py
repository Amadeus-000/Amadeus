import requests
from bs4 import BeautifulSoup
import re,os,time,random
import jaconv
import urllib.request

from selenium import webdriver

# amadeus v2.04
class WorkInfo:
    def __init__(self,url=''):
        if(url==''):
            self.url=''
            self.work_id=''
            self.title=''
            self.circle=''
            self.release_date=''
            self.cv=[]
            self.author=[]
            self.scenario=[]
            self.adult=''
            self.type=''
            self.genres=[]
            self.imgurl=''
            self.description=''
            self.sample_url=''
        else:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            self.url=url
            self.work_id=url.split('/')[-1].split('.')[0]
            self.title=self.get_title(soup)
            self.circle=self.get_circle(soup)
            detail=self.get_detail(soup)
            self.release_date=detail[0]
            self.cv=detail[1]
            self.author=detail[2]
            self.scenario=detail[3]
            self.adult=detail[4]
            self.type=detail[5]
            self.genres=detail[6]
            self.imgurl=self.get_imgurl(soup)
            self.description=self.get_description(soup)
            self.sample_url=self.get_sampleurl(soup)
        self.confidence=100.0
        self.maintext=''
        self.remark=''
        print('WorkInfo コンストラクタを生成しました。')

    def remove_end_spaces(self,str):
        if(str[0]==' ' or str[0]=='　'):
            str=str[1:]
            str=self.remove_end_spaces(str)
        if(str[-1]==' ' or str[-1]=='　'):
            str=str[:-1]
            str=self.remove_end_spaces(str)
        return str
    def get_title(self,soup):
        elems=soup.find('h1',attrs={'id':'work_name'})
        title=self.remove_end_spaces(elems.string)
        return title
    def get_circle(self,soup):
        elems=soup.find("table", attrs={'id':'work_maker'})
        elems=elems.get_text()
        elems=[i for i in elems.splitlines() if i!='']
        for c in range(len(elems)):
            if(elems[c]=='サークル名'):
                circle=self.remove_end_spaces( elems[c+1] )
        return circle
    def get_detail(self,soup):
        cv,author,scenario,genres=[],[],[],[]
        release_date,adult,type='','',''

        elems=soup.find("table", attrs={'id':'work_outline'})
        elems=elems.get_text()
        elems=[i for i in elems.splitlines() if i!='' and not(re.fullmatch(r' *',i))]
        genres=[]
        for i in range(len(elems)):
            if(elems[i]=='販売日'):
                release_date=self.remove_end_spaces( elems[i+1] )
            if(elems[i]=='作者'):
                author=[self.remove_end_spaces(i) for i in elems[i+1].split('/')]
            if(elems[i]=='シナリオ'):
                scenario=[self.remove_end_spaces(i) for i in elems[i+1].split('/')]
            if(elems[i]=='声優'):
                cv=[self.remove_end_spaces(i) for i in elems[i+1].split('/')]
            if(elems[i]=='年齢指定'):
                adult=self.remove_end_spaces( elems[i+1] )
            if(elems[i]=='作品形式'):
                type=self.remove_end_spaces( elems[i+1] )
            if(elems[i]=='ジャンル'):
                j=1
                while(True):
                    if(elems[i+j]=='ファイル容量'):
                        break
                    genres.append(elems[i+j])
                    j+=1
        return release_date,cv,author,scenario,adult,type,genres
    def get_imgurl(self,soup):
        elems=soup.find("picture").find("source")
        img_url=elems['srcset']
        return img_url
    def get_description(self,soup):
        elems=soup.find("div",attrs={'itemprop':'description'})
        description=elems.get_text()
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
            f.write('release_date@:'+self.release_date+'\n')
            if(self.author):
                f.write('author@:'+'///'.join(self.author)+'\n')
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
            if(x.split('@:')[0]=='release_date'):
                self.release_date=self.remove_end_spaces(x.split('@:')[1])
            if(x.split('@:')[0]=='author'):
                self.author=x.split('@:')[1].split('///')
            if(x.split('@:')[0]=='scenario'):
                self.scenario=x.split('@:')[1].split('///')
            if(x.split('@:')[0]=='adult'):
                self.adult=x.split('@:')[1]
            if(x.split('@:')[0]=='type'):
                self.type=x.split('@:')[1]
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
        if(re.search('ボイス・ASMR',self.type)):
            os.makedirs(os.path.join(dirpath,circle),exist_ok=True)
            if(self.sample_url):
                filename=os.path.basename(self.sample_url)
                urllib.request.urlretrieve(self.sample_url, os.path.join(dirpath,circle,filename) )
                print('Download '+filename)
                return 'sample'
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
    
    def download_all(self,dirpath):
        self.sample=[]
        self.m4a=[]
        self.not_voice=[]
        self.fail=[]
        print('Download starting the '+ self.circle)
        for url in self.urls:
            time.sleep(random.randint(45,75))
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
        circle=elems.get_text()
        return circle
    def get_totalworks(self,soup):
        elems=soup.find("div",attrs={"class":"page_total"})
        elems=elems.find("strong")
        totalworks=int(elems.get_text())
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
            urllib.request.urlretrieve(i, os.path.join(dirpath,self.work_id,filename))
            print('Download {0}'.format(filename))


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

        driver = webdriver.Chrome('Amadeus/chromedriver_win32/chromedriver',options=ChromeOptions)
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
        response = requests.get(chobit_url)
        soup = BeautifulSoup(response.text, "html.parser")
        elems = soup.find_all('li')
        for e in elems:
            urls.append(e['data-src'])
        #print(urls)
        return urls