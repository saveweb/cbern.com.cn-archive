import os
import requests

resultFile = 'temp_result.txt'
downloadDir = 'download'
'''example
https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/bdc00134-465d-454b-a541-dcd0cec4d86e.pkg/pdf.pdf
  out=教材/电子教材/小学/道德与法治/统编版/一年级/上册/义务教育教科书·道德与法治一年级上册.pdf
'''
def getLinks(resultFile):
    links = {}
    with open(resultFile, 'r') as f:
        for line in f:
            if line.startswith('https'):
                link = line.strip()
            if line.startswith('  out='):
                path = line.strip()[4:]
                links[link] = path
                yield (link, path)

def download(link, path, session = requests.Session()):
    donwloadFilename = os.path.join(downloadDir, path)
    if not os.path.exists((os.path.dirname(donwloadFilename))):
        os.makedirs(os.path.dirname(donwloadFilename))

    with session.get(link, stream=True) as r:
        with open(donwloadFilename, 'wb') as f:
            r.raw.decode_content = True
            downloadedSize = 0
            for chunk in r.iter_content(chunk_size=1024*1024*1024):
                f.write(chunk)
                downloadedSize += len(chunk)
                print(donwloadFilename.split('/')[-1],downloadedSize,'/', r.headers['Content-Length'], end='\r')

if __name__ == '__main__':
    import threading
    subThreads = threading.Semaphore(8)
    def downloadThread(link, path):
        subThreads.acquire()
        print('Download: ', link, path)
        download(link, path)
        subThreads.release()
        print('Done: ', link, path, 'done')

    for link, path in getLinks(resultFile):
        t = threading.Thread(target=downloadThread, args=(link, path))
        t.start()
