import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Body
from typing import Annotated
from urllib.parse import parse_qs
import json

def crawl_teepublic(url):
    data = []
    html = BeautifulSoup(requests.get(url).content, features="lxml")
    products = html.find_all("div", {"class": "jsDesignContainer"})
    for product in products:
        name = product.find("a", {"class": "jsDesignTitle"}).getText()
        image = product.find("a", {"class": "jsDesignLink"}).find("img")['src']
        link = "https://www.teepublic.com" + product.find("a", {"class": "jsDesignLink"})['href']
        category = product.find("a", {"class": "jsDesignLink"})['href'].split("/")[1]
        data.append({"name": name, "image": image, "url": link, "product_type": category})
    return data

app = FastAPI()

@app.post('/crawl/teepublic/')
def post_teepublic(request: Annotated[str, Body()]):
    body = parse_qs(request)
    url = body['url'][0]
    # print(url)
    number = int(body["page"][0]) if "page" in body else 1
    result = []
    if "page=" in url:
        origin_page = int(url.split('page=')[1][0])
        for i in range(origin_page, origin_page + int(number)):
            # print(i)
            new_url = url.split('page=')[0] +"page=" + str(i) + url.split('page=')[1][1:]
            result.extend(crawl_teepublic(new_url))
    elif number > 1:
        for i in range(1, int(number)+1):
            # print(i)
            new_url = url + "&page=" + str(i)
            result.extend(crawl_teepublic(new_url))
    elif number <= 1:
        result.extend(crawl_teepublic(url))
    return result

def find_data_redbubble(script):
    if 'window.__APOLLO_STATE__' in str(script):
        return True
    return False

def crawl_data_red_bubble(url):
    result = []
    html = BeautifulSoup(requests.get(url=url, headers=headers).content, features="lxml")
    resultGrid = html.find("div", {"id": "SearchResultsGrid"})
    url_to_name = {}
    for product in resultGrid.find_all("a", {"element": "a"}):
        url = product.attrs['href']
        name = product.find("span", {"class": "styles__box--2Ufmy styles__text--23E5U styles__display6--3wsBG styles__nowrap--33UtL styles__display-block--3kWC4"}).get_text()
        url_to_name[url] = name
    script = list(filter(find_data_redbubble, html.find("body").find_all("script")))[0]
    dom = BeautifulSoup(str(script).replace("{{%2F}}", "/"), features="lxml")
    # print(dom.find("script").get_text().split("window.__APOLLO_STATE__=")[1][:-1])
    data = (json.loads(dom.find("script").get_text().split("window.__APOLLO_STATE__=")[1][:-1]))
    # print(json.dumps(data))
    for key, value in data.items():
        if 'inventory_InventoryItemsItem' in key and 'attributes' not in key and 'experiencesProductCard' not in key:
            # print(key + ": " + value['previewSet']['id'])
            # print(key + ": " + str(value))
            url = value['productPageUrl']
            name = url_to_name[url]
            image = data[f"{value['previewSet']['id']}.previews.0"]['url']
            category = url.split("/i/")[1].split("/")[0]
            result.append({
                "url": url,
                "name": name,
                "image": image,
                "product_type": category
            })
    return result
            # print(data[f"{value['previewSet']['id']}.previews.0"]['url'])
    # print(script)
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    # 'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
    'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}




# with open("links_get.txt", 'r') as f:
#     link_list = [i.split("\n")[0] for i in f.readlines()]
    # print(link_list)

# print(link_list)
# for link in link_list:

# class CrawlURL(BaseModel):
#     url : str

@app.post('/crawl/redbubble')
async def post_redbubble(request: Annotated[str, Body()]):

    # return parse_qs(request)
    data = parse_qs(request)
    url = data['url'][0]
    number = int(data["page"][0]) if "page" in data else 1

    # return url
    result = []
    if "page=" in url:
        origin_page = int(url.split('page=')[1][0])
        for i in range(origin_page, origin_page + int(number)):
            # print(i)
            new_url = url.split('page=')[0] +"page=" + str(i) + url.split('page=')[1][1:]
            result.extend(crawl_data_red_bubble(new_url))
    elif number > 1:
        for i in range(1, int(number)+1):
            # print(i)
            new_url = url + "&page=" + str(i)
            result.extend(crawl_data_red_bubble(new_url))
    elif number <= 1:
        result.extend(crawl_data_red_bubble(url))
    return result

def get_tags_of_product_teepublic(html) -> dict:
    
    lists_tag = html.find("nav", {"class": "m-design__additional-info-list"})
    tags = list(map(lambda x: x.replace("\n", ""),list(map(lambda x: x.getText(), lists_tag.find_all("a")))))
    return tags
def get_name_of_product_teepublic(html: BeautifulSoup) -> str:
    name = html.find("div", {"class": "m-design__title"}).find("h1", {"class": "h--no-s-b"}).getText()
    return name
def get_author_name_of_product_teepublic(html: BeautifulSoup) -> str:
    author_name = html.find("a", {"class": "m-design__by-name"}).getText()
    return author_name.replace("\n", "")

def filter_script(script):
    if 'dataLayer.push' in script.getText() and ' window.dataLayer.push' not in script.getText():
        return True
    return False

def get_api_image_url_teepublic(html: BeautifulSoup) -> str:
    script = str(list(filter(filter_script,html.find_all("script")))[0])
    script = json.loads(script.split("dataLayer.push(")[1].split(")")[0])
    url = f"{script['request__base_url']}/designs/{script['design__design_id']}/canvas/{script['design__canvas_id']}/product_images"
    return url

@app.post("/crawl/product/teepublic")
def post_product_teepublic(request: Annotated[str, Body()]):
    data = parse_qs(request)
    url = data['url'][0]
    # print(url)
    html = BeautifulSoup(requests.get(url).content, features="lxml")
    tags = get_tags_of_product_teepublic(html)
    name = get_name_of_product_teepublic(html)
    author = get_author_name_of_product_teepublic(html)
    image_api = get_api_image_url_teepublic(html)
    return {'name': name, 'author': author, 'tags': tags, 'image_api': image_api}

