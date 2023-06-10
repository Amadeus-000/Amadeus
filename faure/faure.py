# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import MeCab

class VersionInfo:
    def __init__(self):
        print('faure is working')

# class FaureModifyText:
#     def __init__(self,modelpath="rinna/japanese-gpt-neox-3.6b"):
#         self.tokenizer = AutoTokenizer.from_pretrained(modelpath, use_fast=False)
#         self.model = AutoModelForCausalLM.from_pretrained(modelpath)

#     def ScoreSentence(self,sentence):
#         # 入力した文字がどれだけ自然な文章かをスコアリングする
#         tokenize_input = self.tokenizer.tokenize(sentence)
#         tensor_input = torch.tensor([self.tokenizer.convert_tokens_to_ids(tokenize_input)])
#         loss=self.model(tensor_input, labels=tensor_input)[0]
#         return loss.item()
    
#     def AnalyzeSentence(self,sentence):
#         # 文を形態素解析する
#         m=MeCab.Tagger()
#         result=m.parse(sentence)
#         return result
    