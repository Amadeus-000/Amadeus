import requests
from bs4 import BeautifulSoup
import re,os,time,random
import jaconv
import urllib.request

# m4a_tools
from selenium import webdriver

# ModifyText
import functools
from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

import spacy



# amadeus v3.65
class WorkInfo:
    def __init__(self,url=''):
        category=(url.split('/')[-1].split('.')[0])[0:2] in ['RJ','VJ']
        self.sale_now=not ('announce' in url.split('/') )
        if(category and self.sale_now):
            response = requests.get(self.modify_url(url))
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
        elem_tr=soup.find_all('tr')
        for tr in elem_tr:
            try:
                # print(tr.find('th'))
                if( (tr.find('th')).text=='販売日'):
                    self.release_date=self.remove_end_spaces(tr.find('td').text)
                    # print(self.release_date)
                if( (tr.find('th')).text=='年齢指定'):
                    self.adult=self.remove_end_spaces(tr.find('td').text)
                    # print(self.adult)
                if( (tr.find('th')).text=='作品形式'):
                    worktypes=[]
                    for type in tr.find('td').find_all('a'):
                        worktypes.append(self.remove_end_spaces(type.text))
                    if('ボイス・ASMR' in worktypes):
                        self.type='ボイス・ASMR'
                    else:
                        self.type='ボイス・ASMRではない'
                    self.type.append(self.remove_end_spaces(type.text))
                    print(self.type)
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
            except AttributeError:
                pass


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

        circle=self.circle
        if(re.search('[\/:*?"<>|.]',circle)):
            circle=re.sub('[\/:*?"<>|.]','',circle)
            circle=circle+'_edited'
        os.makedirs(os.path.join('downloads',circle),exist_ok=True)

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
        circle=self.remove_end_spaces(elems.get_text())
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
    def __init__(self,text='',text_type='XXX'):
        self.text=text
        self.text_type=text_type
        self.maru_pattern = re.compile(r'●|○|◯|〇|☆|★|◎')
        if(text_type=='TSW' or text_type=='TSW_v2' or text_type=='TSW_v3'):
            self.put_newline_ginga()
            self.replace_rn2n()
            self.convert2hira()
        elif(text_type=='description'):
            self.replace_rn2n()
            self.text=self.replace_fuseji(self.text)
            self.convert2hira()
        else:
            self.replace_rn2n()
            self.convert2hira()
    def correct_text(self):
        pass
    def put_newline(self):
        split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
        concat_tail_no = functools.partial(concatenate_matching, former_matching_rule=r"^(?P<result>.+)(の)$", remove_former_matched=False)
        segmenter = make_pipeline(normalize, split_newline, concat_tail_no, split_punc2)

        lines=(self.text).split('\n')
        for n in range(len(lines)):
            lines[n]='\n'.join( list(segmenter(lines[n])) )
        
        self.text='\n'.join(lines)
    def put_newline_ginga(self):
        nlp = spacy.load('ja_ginza')
        try:
            if(len(self.text.encode('utf-8')) < 49000): # 49149 bytes 以下のとき
                doc = nlp(self.text)
                results=''
                for sent in doc.sents:
                    results=results + str(sent) + '\n'
            else:
                text_splitline=(self.text).splitlines()
                text_res=[]
                for oneline in text_splitline:
                    res_tmp=''
                    doc=nlp(oneline)
                    for sent in doc.sents:
                        res_tmp=res_tmp + str(sent) + '\n'
                    text_res.append(res_tmp)
                results='\n'.join(text_res)
        except:
            results='Tokenization error'
                    
        # print(results)
        
        self.text=results
    def replace_fuseji(self,text):
        maru_list=['●','○','◯','〇','☆','★','◎']
        fuseji_dict={
            'マ●コ':'マンコ',
            'ま●こ':'まんこ',
            'チ●ポ':'チンポ',
            'ち●ぽ':'ちんぽ',
            'チ●コ':'チンコ',
            'ち●こ':'ちんこ',
            'チ●チン':'チンチン',
            'ち●ちん':'ちんちん',
            'オ●ンチン':'オチンチン',
            'お●んちん':'おちんちん',
            'ちん●ん':'ちんちん',
            'セッ●ス':'セックス',
            'せっ●す':'せっくす',
            'レ●プ':'レイプ',
            'J●':'JK',
            '●K':'JK',
            'ザー●ン':'ザーメン',
        }
        for fuseji in fuseji_dict:
            for maru in maru_list:
                replacement_moji=fuseji.replace('●',maru)
                text=text.replace(replacement_moji,fuseji_dict[fuseji])

        return text
                
    def add_info(self):
        pass
    def convert2hira(self):
        # text=repr(text_input)
        # text=re.sub(r'\\u3000',' ',text) #removing zenkaku space
        # clean_text=eval(text)
        self.text_conv=jaconv.kata2hira(self.text)
    def replace_rn2n(self):
        self.text=re.sub('\r\n','\n',self.text)