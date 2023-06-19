import re, json, math
from pathlib import Path
import MeCab, jaconv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class VersionInfo:
    def __init__(self):
        print('version 1.0.0')

class AnalizeTextTools:
    def AnalyzeSentence(self,sentence):
        # MeCabでは半角スペースは無視されるので、デルタδに変換する
        sentence=re.sub(' ','δ',sentence)
        # 文を形態素解析する
        m=MeCab.Tagger()
        result=m.parse(sentence)

        # デルタδを半角スペースに戻す
        result=re.sub('δ',' ',result)

        # EOSと空行を削除し、タブで分割する
        result=result.splitlines()
        result=[line.split('\t') for line in result if line != 'EOS' and line != '']
        return result
    
    def NomalizeText(self,text):
        result=re.sub('、',' ',text)
        result=re.sub('\r\n','\n',result)
        result=re.sub('？','?',result)
        result=re.sub('！','!',result)
        return result
    
    def SplitNewLineQuestion(self,text):
        # "。"または"? "で分割し、"? 。"を残す
        sentences = re.split('(?<=\?)|(?<=。)|(?<=!)', text)

        # 空の文字列を削除と。を削除
        sentences = [re.sub("。","",s) for s in sentences if s!='']

        return sentences
    def JapReSub(self,pattern,replace,text):
        # ひらがな、カタカナが混ざっていても文字を置き換える
        # 正規表現には対応していない
        pattern_hira=jaconv.kata2hira(pattern)
        text_hira=jaconv.kata2hira(text)

        match=re.finditer(pattern_hira,text_hira)
        for m in match:
            text=text[0:m.start()]+replace+text[m.end():]
        return text

class FaureModifyText(AnalizeTextTools):
    def __init__(self,modelpath="rinna/japanese-gpt-neox-3.6b"):
        self.tokenizer = AutoTokenizer.from_pretrained(modelpath, use_fast=False)
        self.model = AutoModelForCausalLM.from_pretrained(modelpath)

        #ワードリスト読み込み
        filename_json='wordlist.json'
        module_dir = Path(__file__).parent
        file_path = module_dir / filename_json
        with open(file_path,encoding='utf-8') as f:
            self.wordlist = json.load(f)

    def InsertNewLine(self,text):
        if(len(text)<50):
            return text
        def PutPeriod(text):
            # 入力した文章に句点を１つだけ入れる
            threshold=self.ScoreSentence(text)*1.01
            print("基準点数: "+str(threshold))
            scores={}
            for i in range(10,len(text)-10):
                text_tmp=text[0:i]+'。'+text[i:]
                scores[i]=self.ScoreSentence(text_tmp)

            min_key=min(scores, key=scores.get)

            if(scores[min_key]<threshold):
                return text[0:min_key]+'。'+text[min_key:]
            else:
                return text
            
        newlineNum=math.ceil(len(text)/50)-1

        result_text=text
        for _ in range(0,newlineNum):
            result_text=PutPeriod(result_text)

            # テキストが変化していなかったら終了
            if(result_text==text):
                break
        return result_text

    def ProofReadSentences(self):
        self.ProofReadSentencesDirect()
        self.ProofReadSentencesVerb()
        self.ProofReadSentencesNoun()

        self.JoinSentence()
        self.ProofReadSentencesAbsolute()

    def ProofReadSentencesDirect(self):
        print("文字校正...")
        sentences_proofreaded=[]
        direct_wordlist=self.wordlist["direct"]
        direct_wordlist=dict(sorted(direct_wordlist.items(), key=lambda item: len(item[0]), reverse=True))
        # sentencesを校正する
        for sentence in self.sentences:
            sentence_tmp=sentence
            # ワードリストにある単語を置換する
            for word in direct_wordlist:
                # print('文字校正... {0} -> {1}'.format(word,direct_wordlist[word]))
                # sentence_tmp=re.sub(word,direct_wordlist[word],sentence_tmp)
                sentence_tmp=self.JapReSub(word,direct_wordlist[word],sentence_tmp)
            
            # 文が変化したときだけスコアリングする
            if(sentence!=sentence_tmp):
                sentences_proofreaded.append(self.CompareSentences(sentence,sentence_tmp))
            else:
                sentences_proofreaded.append(sentence)
        print(sentences_proofreaded)
        self.sentences=sentences_proofreaded

    def ProofReadSentencesVerb(self):
        print("動詞校正...")
        sentences_proofreaded=[]
        verb_wordlist=self.wordlist["verb"]
        verb_wordlist=dict(sorted(verb_wordlist.items(), key=lambda item: len(item[0]), reverse=True))
        # sentencesを校正する
        for sentence in self.sentences:
            sentence_tmp=''
            morphemes=self.AnalyzeSentence(sentence)
            for morpheme in morphemes:
                if(morpheme[4].split('-')[0]=='動詞'):
                    # ワードリストにある単語を置換する
                    morpheme_tmp=morpheme[0]
                    for word in verb_wordlist:
                        # print('動詞校正... {0} -> {1}'.format(word,verb_wordlist[word]))
                        morpheme_tmp=self.JapReSub(word,verb_wordlist[word],morpheme_tmp)
                    sentence_tmp+=morpheme_tmp
                else:
                    sentence_tmp+=morpheme[0]
            
            # 文が変化したときだけスコアリングする
            if(sentence!=sentence_tmp):
                sentences_proofreaded.append(self.CompareSentences(sentence,sentence_tmp))
            else:
                sentences_proofreaded.append(sentence)

        print(sentences_proofreaded)
        self.sentences=sentences_proofreaded

    def ProofReadSentencesNoun(self):
        print("名詞校正...")
        sentences_proofreaded=[]
        noun_wordlist=self.wordlist["noun"]
        noun_wordlist=dict(sorted(noun_wordlist.items(), key=lambda item: len(item[0]), reverse=True))
        # sentencesを校正する
        for sentence in self.sentences:
            sentence_tmp=''
            morphemes=self.AnalyzeSentence(sentence)
            for morpheme in morphemes:
                if(morpheme[4].split('-')[0]=='名詞'):
                    # ワードリストにある単語を置換する
                    morpheme_tmp=morpheme[0]
                    for word in noun_wordlist:
                        # print('名詞校正... {0} -> {1}'.format(word,noun_wordlist[word]))
                        morpheme_tmp=self.JapReSub(word,noun_wordlist[word],morpheme_tmp)
                    sentence_tmp+=morpheme_tmp
                else:
                    sentence_tmp+=morpheme[0]
            
            # 文が変化したときだけスコアリングする
            if(sentence!=sentence_tmp):
                sentences_proofreaded.append(self.CompareSentences(sentence,sentence_tmp))
            else:
                sentences_proofreaded.append(sentence)

        print(sentences_proofreaded)
        self.sentences=sentences_proofreaded

    def ProofReadSentencesAbsolute(self):
        print("絶対校正...")
        text=self.text
        absolute_wordlist=self.wordlist["absolute"]
        for word in absolute_wordlist:
            re.sub(word,absolute_wordlist[word],text)
        self.text=text
        self.text_conv=jaconv.kata2hira(self.text)

    def SetText(self,text="",premise_text=""):
        # メインテキスト
        self.text=self.NomalizeText(text)
        
        # 前提文
        if(len(premise_text)<=1500):
            self.premise_text=premise_text
        else:
            self.premise_text=premise_text[:1500]
        self.premise_text=premise_text

        # メインテキストを句点、クエスチョン、エクスクラメーションで分割する
        self.sentences=self.SplitNewLineQuestion(self.text)
    
    def JoinSentence(self):
        # １行が50文字を超える場合は改行する
        sentences=[self.InsertNewLine(sentence) if len(sentence)>50 else sentence for sentence in self.sentences]
        # 文章を結合する
        self.text='\n'.join(sentences)
        self.text_conv=jaconv.kata2hira(self.text)

    def ScoreSentence(self,sentence,premise_text=""):
        # 入力した文字がどれだけ自然な文章かをスコアリングする
        # 前提分は引数として入力する
        # スコアは低いほうがよい
        if(premise_text==""):
            tokenize_input = self.tokenizer.tokenize(sentence)
        else:
            tokenize_input = self.tokenizer.tokenize(premise_text+'\n'+sentence)
        tensor_input = torch.tensor([self.tokenizer.convert_tokens_to_ids(tokenize_input)])
        loss=self.model(tensor_input, labels=tensor_input)[0]
        print('sentence : {0} score : {1}'.format(sentence,loss.item()))
        return loss.item()
    
    def CompareSentences(self,sentence1,sentence2):
        # 2つの文のスコアを比較する。前提分はself.premise_textが入力される
        # スコアが低いほうがよい
        score1=self.ScoreSentence(sentence1,self.premise_text)
        score2=self.ScoreSentence(sentence2,self.premise_text)
        if(score1<score2):
            return sentence1
        else:
            return sentence2

class PremiseText(AnalizeTextTools):
    def __init__(self,text):
        self.text=self.NomalizeText(text)
        self.sentences=( self.text ).splitlines()
        self.DELETE_RANGE=3

        self.RemoveCreditInfo()
        self.text='\n'.join(self.sentences)
        if(len(self.text)>1500):
            print('文字数が１５００文字を超えています。カットします')
            self.CutText()

    def RemoveCreditInfo(self):
        # クレジット情報をが含まれると思われる行とその前後の行を削除する
        delete_row_num=[]
        for idx in range(len(self.sentences)):
            if(self.SearchCreditInfo(self.sentences[idx])):
                for row in self.GetRowRange(idx,self.DELETE_RANGE,len(self.sentences)):
                    delete_row_num.append(row)
        
        # 重複を削除して、降順に並び替える
        delete_row_num=sorted(list(set(delete_row_num)), reverse=True)
        # 削除する
        for idx in delete_row_num:
            self.sentences.pop(idx)

    def CutText(self):
        THRESHOLD=0.00
        char_count=self.CountCharactersInSentences(self.sentences)

        while(char_count>1500):
            sentence_metadata=[]
            sentences_cut=[]
            for sentence in self.sentences:
                if((self.CountEffectiveWord(sentence)/len(sentence))>THRESHOLD):
                    sentences_cut.append(sentence)
                sentence_metadata.append({
                    'sentence':sentence,
                    'char_count':len(sentence),
                    'effective_word_count':self.CountEffectiveWord(sentence),
                    'word_ratio':self.CountEffectiveWord(sentence)/len(sentence)
                })
            THRESHOLD+=0.01
            char_count=self.CountCharactersInSentences(sentences_cut)

            # 確認用
            # for i in sentence_metadata:
            #     print(i)
            # print("全体文字数 {0}".format(char_count))
        
        self.sentences=sentences_cut
        self.text='\n'.join(self.sentences)
    
    def CountCharactersInSentences(self,sentences):
        return len('\n'.join(sentences))

    def CountEffectiveWord(self,sentence):
        words=self.AnalyzeSentence(sentence)
        count=0
        for word in words:
            hinshi=word[4].split('-')[0]
            if(hinshi in ['名詞','動詞','形容詞','代名詞']):
                count+=1
        return count

    def NomalizeText(self,text):
        text = super().NomalizeText(text)

        # 改行を1つにする
        text=re.sub(r'\n+', '\n', text)
        return text
    
    def GetRowRange(self,num,rowrange,listsize):
        # 入力した数字の前後RANGE行を返す
        result=[]
        for i in range(-rowrange,rowrange+1):
            if (num+i > 0 and num+i < listsize):
                result.append(num+i)
        return result
    
    def SearchCreditInfo(self,text):
        words=['http','@','クレジット','mp3','wav','txt']
        for word in words:
            if(re.search(word,text,flags=re.IGNORECASE)):
                return True
        return False
    
