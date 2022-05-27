import requests
from bs4 import BeautifulSoup
import re
import jaconv

# amadeus v1.00
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
        self.confidence=100.0
        self.maintext=''
        self.remark=''
        print('コンストラクタを生成しました。')

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
        self.description=self.title+'\n'+txt.split('description_separate_point')[-1]


