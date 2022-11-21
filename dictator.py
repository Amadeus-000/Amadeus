from unittest import result
from Amadeus import amadeus
import whisper
import os,time,pathlib
import gc
import shutil
from mutagen.mp4 import MP4



def get_filepaths(dir):
    path_list=[]
    p=pathlib.Path(dir)

    #ファイル名取得
    for f in sorted(list(p.glob("**/*"))):
        ext=str(f).split('.')[-1]
        if(all( [os.path.isfile(f), ext in ['mp3','wav','flac','m4a','mp4','aif']]) ):
            #print(f)
            if '__MACOSX' in str(f).split('\\'):
                print('__MACOSX')
            else:
                path_list.append(str(f))
    return path_list

def ave_compression_ratio(result):
    sum=0
    count=0
    for s in result["segments"]:
        count+=1
        sum+=s['compression_ratio']
    if(count==0):
        return 0
    else:
        # print(sum/count)
        return sum/count


def start():
    start_time=time.strftime('%Y/%m/%d %H:%M:%S')
    modelsize='large'
    compression_ratio_threshold=1.0

    circles=sorted(os.listdir('voicedata'))
    print(circles)

    for circle in circles:
        works=sorted([i for i in os.listdir('voicedata/'+circle) if os.path.isdir('voicedata/{0}/{1}'.format(circle,i)) ])
        print(works)
        for work in works:
            filepaths=[]
            output_text=[]

            current_dir='voicedata/'+circle+'/'+work+'/'
            output_dir='outputdata/'+circle+'/'+'workinfo/'+work+'/'
            os.makedirs(output_dir,exist_ok=True)

            #URLから作品情報を取得
            url='https://www.dlsite.com/maniax/work/=/product_id/'+ work.split('_')[0] +'.html'
            info=amadeus.WorkInfo(url)
            info.write2txt(output_dir)


            filepaths=get_filepaths(current_dir)

            #ファイルネームを取得、ファイル書き出し
            tmp_results=[]
            for i in filepaths:
                if(os.path.splitext(os.path.basename(i))[1]=='.m4a'):
                    mp4 = MP4(i)
                    try:
                        tmp_results.append(mp4['©nam'][0])
                    except KeyError:
                        tmp_results.append(os.path.splitext(os.path.basename(i))[0])
                else:
                    tmp_results.append(os.path.splitext(os.path.basename(i))[0])

            filename_str='ΦΦΦΦΦ'.join(tmp_results)
            with open(output_dir+'filename_str.txt','w',encoding='utf-8') as f:
                f.write(filename_str)


            for filepath in filepaths:
                print(filepath)
                model=whisper.load_model(modelsize)
                result_t10 = model.transcribe(
                    filepath,
                    language='ja',
                    # verbose=True,
                    # temperature=0.8,
                )
                result=result_t10["text"]
                cmp_ratio=ave_compression_ratio(result_t10)
                print('Temperature=1.0 : ' + str(cmp_ratio))
                print(result_t10['text'])
                del result_t10
                del model
                gc.collect()

                if(cmp_ratio>compression_ratio_threshold):
                    model= whisper.load_model(modelsize)
                    result_t08 = model.transcribe(
                        filepath,
                        language='ja',
                        # verbose=True,
                        temperature=0.8,
                    )
                    if( cmp_ratio > ave_compression_ratio( result_t08) ):
                        result=result_t08["text"]
                        cmp_ratio=ave_compression_ratio(result_t08)
                    print('Temperature=0.8 : ' + str(ave_compression_ratio(result_t08)))
                    print(result_t08['text'])
                    del result_t08
                    del model
                    gc.collect()


                with open(output_dir+'compression_ratio.txt','a',encoding='utf-8') as f:
                    f.write(str(cmp_ratio) +'\n')
                
                # for s in result["segments"]:
                #     print(s['text'] +' : ' +str(s['compression_ratio']))
                print('@@@@result text@@@@')
                print(result)
                output_text.append(result)

                gc.collect()

            with open(output_dir+'output.txt','w',encoding='utf-8') as f:
                f.write('\nΦΦΦΦΦ'.join(output_text))
        
        #workinfoをzipにする
        # shutil.make_archive('outputdata/{0}/workinfo'.format(circle), format='zip', root_dir='outputdata/{0}'.format(circle), base_dir='workinfo')
        with open('outputdata/{0}/log.txt'.format(circle),'w',encoding='utf-8') as f:
            f.write('end time {0}'.format(time.strftime('%Y/%m/%d %H:%M:%S')))
        

    with open('outputdata/log.txt','w',encoding='utf-8') as f:
        f.write('start time {0}\nend time {1}'.format(start_time,time.strftime('%Y/%m/%d %H:%M:%S')))

    print('Process is completed.')

start()