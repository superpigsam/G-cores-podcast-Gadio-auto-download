import urllib.request
import re
import os
import time
import shutil

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
    # reg = r'(?:https://www.gcores.com/radios/)\d+' #匹配podcast页面
    reg = r'(?:/radios/)\d+'  # 匹配podcast页面
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8'))  # 返回匹配的网址
    return(url_lst)

# find download link from gcores.com


def getPodName(html):
    # reg = r'(?:<h1 class="story_title" id="j_title_preview">)[\s\S]+(?:<p class="story_desc" id="j_desc_preview">)' #匹配podcast title
    # reg = r'(?:<h1 class="originalPage_title">)[\s\S]+(?:<p class="originalPage_desc">)'    #匹配podcast title
    # 匹配podcast title
    reg = r'(?:<h1 class="originalPage_title">)[\s\S]+(?:<div class="articlePage_content")'
    pod_title_re = re.compile(reg)
    pod_title = pod_title_re.findall(html.decode('UTF-8'))  # 返回匹配的内容
    # date + title + sub_title
    title = re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>|small)', '', pod_title[0].split('>')[7])[:-4] + '_' + re.sub(
        r'(\/|\||\\|\:|\*|\?|\"|\<|\>)', '', pod_title[0].split('>')[1])[:-2] + '_' + re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>)', '', pod_title[0].split('>')[3])[:-1]
    # date + title
    # title = re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>|small)', '', pod_title[0].split('>')[7])[:-4] + '_' + re.sub(
    #     r'(\/|\||\\|\:|\*|\?|\"|\<|\>)', '', pod_title[0].split('>')[1])[:-2]
    
    # category
    category = re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>|small)',
                      '', pod_title[0].split('>')[9])[:-1]
    # 匹配podcast download url
    reg = r'(?:href="https://alioss.gcores.com/uploads/audio/)[a-zA-Z0-9-]+(?:.mp3)'
    # reg = r'(?:<a class="originalButton originalButton-circle ml-3" target="_blank" href=")[\s\S]+(?:.mp3"><svg aria-hidden="true")'
    pod_dl_url_re = re.compile(reg)
    pod_dl_url = pod_dl_url_re.findall(html.decode('UTF-8'))  # 返回匹配的网址
    if not pod_dl_url:
        reg = r'(?:href="https://cdn.lizhi.fm/audio/)[\s\S]+(?:.mp3">)'
        pod_dl_url_re = re.compile(reg)
        pod_dl_url = pod_dl_url_re.findall(html.decode('UTF-8'))  # 返回匹配的网址
        if not pod_dl_url:
            return([title, [], category])
    dl_url = pod_dl_url[0].split('"')[1]
    return([title, dl_url, category])

# find download link from lizhi.fm (for old podcasts)

# def getPodNameLizhi(html):
#     # 匹配podcast title
#     reg = r'(?:<h1 class="story_title" id="j_title_preview">)[\s\S]+(?:<p class="story_info">)'
#     pod_title_re = re.compile(reg)
#     pod_title = pod_title_re.findall(html.decode('UTF-8'))  # 返回匹配的内容
#     title = re.sub(r'(\/|\||\\|\:|\*|\?|\"|\<|\>)', '',
#                    pod_title[0].splitlines()[1].strip())
#     # 匹配podcast download url
#     reg = r'(?:<a href="https://cdn.lizhi.fm/audio/)[\s\S]+(?:.mp3" target="_blank">)'
#     pod_dl_url_re = re.compile(reg)
#     pod_dl_url = pod_dl_url_re.findall(html.decode('UTF-8'))  # 返回匹配的网址
#     if (pod_dl_url):
#         dl_url = pod_dl_url[0].split('"')[1]
#     else:
#         dl_url = "err"
#     return([title, dl_url])


def getFile(url, title, category):
    try:
        u = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        print(urllib.error.HTTPError)
        return False
    title = title + '.mp3'
    # creat category if not exist
    path = os.path.join(os.getcwd(), category)
    if not os.path.isdir(path):
        os.makedirs(path)
    print(title.split('_')[1])
    # check if already downloaded; if exist as old version
    old_file_path = os.path.join(os.getcwd(), title.split('_')[1] + '.mp3')
    new_file_path = os.path.join(os.getcwd(), category, title)
    if os.path.exists(new_file_path):
        print("downloaded")
        return True
    elif os.path.exists(old_file_path):
        shutil.copy(old_file_path, new_file_path)
        print('copyed from old files')
        return True
    else:
        path = os.path.join(os.getcwd(), category)
        f = open(os.path.join(path, title), 'wb')

        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            f.write(buffer)
        f.close()
        print("Download Sucessful: " + title)
        time.sleep(10)
        return True


# log error information
def log_error(title, url, category):
    f = open(os.path.join(os.path.abspath(
        os.path.dirname(os.getcwd())), 'missing.txt'), 'a')
    f.write(title + '\r\n' + url + '\r\n' + category + '\r\n' )
    f.close()
    print('error logged')

base_url = 'https://www.gcores.com/radios?page='  # podcast页面中相同的部分
base_pod_url = 'https://alioss.gcores.com/uploads/audio/'
count = 0   # to adjust which podcasts to download, i.e. to skip
# the first %count podcasts, 24 podcasts per page
# count = 29*24
urlpre = ''

# 'range' refers to the range of pages at "https://www.gcores.com/categories/9/originals?page=" to be downloaded
# adjust as needed
# download from new to old
for i in range(1, 9):
    print('page: ' + str(i))
    full_base_url = base_url + str(i)
    html = getHtml(full_base_url)
    url_lst = getUrl(html)
    for url in url_lst[:]:
        url = 'https://www.gcores.com'+url
        if urlpre != url:
            count = count + 1
            print('podcast: ' + str(count))
            # numbers of podcasts to downlaod, adjust count as needed
            # remove 'if' structure if no restiction needed
            if count < 999 and count > 0:
                print(url)
                # [title, dl_url] = getPodNameLizhi(getHtml(url))
                # if dl_url == "err":
                #     [title, dl_url] = getPodName(getHtml(url))
                [title, dl_url, category] = getPodName(getHtml(url))
                if not dl_url:
                    print('not found')
                    log_error(title, url, category)
                    time.sleep(1)
                else:
                    if len(title) > 127:
                        title = title[:127]
                    print(title, '\r\n', category, '\r\n', dl_url)
                    # print(category)
                    # print(dl_url)
                    if getFile(dl_url, title, category):
                        # download interval, adjust as needed
                        time.sleep(1)
                    else:
                        log_error(title, url, category)
                        time.sleep(1)
            urlpre = url
