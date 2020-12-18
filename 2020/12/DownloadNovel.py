import os
import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup,Tag

base_url = 'https://www.qu.la'
base_dir = 'novel/' 

def get_html_content(url): 
    r = requests.get(url)
    r.raise_for_status
    r.encoding = 'utf-8'
    return BeautifulSoup(r.text,'html.parser')

def get_class_book_url_list(content):
    books = list()
    main = content.find_all('div',{'id':'main'})[0]
    divs = chooice_tags(main.contents)
    for div in divs:
        contents = chooice_tags(div.contents)
        name = contents[0].find_all('span')[0].string
        books_list = chooice_tags(contents[1].contents)[0]
        li_list = books_list.find_all('li')
        b_list = list()
        for li in li_list:
            a = li.find_all('a')[0]
            url = a.attrs['href']
            book_name = a.string
            b_list.append({'url':base_url + url,'name':book_name})
        books.append({'name':name,'books':b_list})
    return books

def chooice_tags(tags):
    tag_list = list()
    for tag in tags:
        if isinstance(tag,Tag):
            tag_list.append(tag)
    return tag_list

def make_dir(name):
    name = base_dir + name.strip()
    if not os.path.exists(name):
        os.makedirs(name)
    return name

def download_book_list(class_books):
    groups = list()
    for node in class_books:
        name = node['name']
        books = node['books']
        path = make_dir(name)
        tasks = [download_book(book['url'],path,book['name']) for book in books]
        groups.append(asyncio.gather(*tasks))
    return groups

async def download_book(url,path,name):
    print('download book [{}] start...'.format(name))
    content = await get_content(url)
    chapter_list = content.find_all('div',{'id':'list'})[0].find_all('dl')[0].contents
    chapter_list = chooice_tags(chapter_list)
    text_file = open(path + '/' + name + '.txt','w',encoding='utf-8')
    sem = asyncio.Semaphore(10)
    is_download = True
    for chapter in chapter_list:
        if chapter.name == 'dt':
            if chapter.string.find('最新章节') is not -1:
                is_download = False
            else:
                is_download = True
            continue
        if is_download:
            async with sem:
                await download_chapter(text_file,url,chapter)
    text_file.close()
    print('download book [{}] end...'.format(name))

async def download_chapter(text_file,url,node):
    a = node.find_all('a')[0]
    title = a.string
    print('download chapter [{}] start...'.format(title))
    uri = a.attrs['href']
    content = await get_content(url + uri)
    attr = content.find_all('div',{'id':'content'})[0]
    text = attr.get_text()
    text_file.write(title + '\n')
    text_file.write(text + '\n')
    print('download chapter [{}] end...'.format(title))

async def fetch(session,url):
    count = 10
    while count > 0:
        try:
            async with session.get(url) as response:
                return await response.text()
        except BaseException as e:
            print('Error',e)
            count -= 1
    return ''

async def get_content(url):
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        html = await fetch(session,url)
        return BeautifulSoup(html,'html.parser')

def main():
    content = get_html_content(base_url + '/paihangbang/')
    class_books = get_class_book_url_list(content)
    loop = asyncio.get_event_loop()
    groups = download_book_list(class_books)
    loop.run_until_complete(asyncio.gather(*groups))
    loop.close()

if __name__ == '__main__':
    main()
