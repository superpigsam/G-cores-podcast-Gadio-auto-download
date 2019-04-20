import urllib.request
import re
import os, time

#
# download Gadio podcasts to selected location
# set downloaded title as "date uploaded" + "original title"
# i.e.: 2019-04-07假期干点什么好？GadioNews03.30~04.04.mp3
# Each podcast is 50~100 MB, make sure you have enough disk space XD
# allows to adjust download interval
# allows to restrict download numbers
# allows to update downloaded podcasts 

# set storage directory as current directory, change'os.getcwd()'
# to preferred location if needed, i.e.:'F:\Game\gcores\'
os.chdir(os.path.join(os.getcwd(), 'podcast_download'))
# os.chdir(os.path.join('F:\\test\spider\机核网podcast', 'podcast_download'))


# open the url and read
def getHtml(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    # print(html)
    page.close()
    return html

# compile the regular expressions and find
# all stuff we need
def getUrl(html):
    reg = r'(?:https://www.gcores.com/radios/)\d+' #匹配podcast页面
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8')) #返回匹配的网址
    return(url_lst)

# find download link from gcores.com
def getPodName(html):
    reg = r'(?:<h1 class="story_title" id="j_title_preview">)[\s\S]+(?:<p class="story_desc" id="j_desc_preview">)' #匹配podcast title
    pod_title_re = re.compile(reg)
    pod_title = pod_title_re.findall(html.decode('UTF-8')) #返回匹配的内容
    title = re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>|small)', '', pod_title[0].splitlines()[4].strip()) + re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>)', '', pod_title[0].splitlines()[1].strip())
    reg = r'(?:href="https://alioss.gcores.com/uploads/audio/)[a-zA-Z0-9-]+(?:.mp3)' #匹配podcast download url
    pod_dl_url_re = re.compile(reg)
    pod_dl_url = pod_dl_url_re.findall(html.decode('UTF-8')) #返回匹配的网址
    dl_url = pod_dl_url[0].split('"')[1]
    return([title,dl_url])

# find download link from lizhi.fm (for old podcasts)
def getPodNameLizhi(html):
    reg = r'(?:<h1 class="story_title" id="j_title_preview">)[\s\S]+(?:<p class="story_info">)' #匹配podcast title
    pod_title_re = re.compile(reg)
    pod_title = pod_title_re.findall(html.decode('UTF-8')) #返回匹配的内容
    title = re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>)', '', pod_title[0].splitlines()[1].strip())
    reg = r'(?:<a href="https://cdn.lizhi.fm/audio/)[\s\S]+(?:.mp3" target="_blank">)' #匹配podcast download url
    pod_dl_url_re = re.compile(reg)
    pod_dl_url = pod_dl_url_re.findall(html.decode('UTF-8')) #返回匹配的网址
    if (pod_dl_url):
        dl_url = pod_dl_url[0].split('"')[1]
    else:
        dl_url = "err"
    return([title,dl_url])

def getFile(url, title):
    u = urllib.request.urlopen(url)
    title = title + '.mp3'
    f = open(title, 'wb')

    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        f.write(buffer)
    f.close()
    print ("Sucessful to download" + " " + title)

base_url = 'https://www.gcores.com/categories/9/originals?page='  #podcast页面中相同的部分
base_pod_url = 'https://alioss.gcores.com/uploads/audio/'
count = 0   # to adjust which podcasts to download, i.e. to skip
            # the first %count podcasts, 24 podcasts per page
# count = 29*24
urlpre = ''

# 'range' refers to the range of pages at "https://www.gcores.com/categories/9/originals?page=" to be downloaded
# adjust as needed
# download from new to old
for i in range(1,43):
    print('page: ' + str(i))
    full_base_url =base_url + str(i)
    html = getHtml(full_base_url)
    url_lst = getUrl(html)
    for url in url_lst[:]:
        if urlpre != url:
            count = count + 1
            print('podcast: ' + str(count))
            # numbers of podcasts to downlaod, adjust count as needed
            # remove 'if' structure if no restiction needed
            if count < 999:  
                print(url)
                [title, dl_url] = getPodNameLizhi(getHtml(url))
                if dl_url == "err":
                    [title, dl_url] = getPodName(getHtml(url))
                print(title)
                print(dl_url)
                getFile(dl_url, title)
                # download interval, adjust as needed
                time.sleep(10)
            urlpre = url
                