import logging
import requests
import json
from queue import Queue
from threading import Thread
from time import sleep
import pandas as pd
import re
import time

# crawl Tiki first

# books
cookies = {
    '_trackity': '04921f86-8f55-99f4-4fab-e9166040d64c',
    'TOKENS': '{%22access_token%22:%22MDz5J9CVLdmSR8lNqa4utAxsjBYw6o03%22}',
    'delivery_zone': 'Vk4wMzQwMjQwMTM=',
    'tiki_client_id': '',
    'TKSESSID': '0b1b4f2a77c9027cb1bf2e26728acb07',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'origin': 'https://tiki.vn',
    'referer': 'https://tiki.vn/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'x-guest-token': 'MDz5J9CVLdmSR8lNqa4utAxsjBYw6o03',
}

# get all categories

categories_params = {
    'platform': 'desktop',
}

category_response = requests.get('https://api.tiki.vn/raiden/v2/menu-config',
                                 params=categories_params, cookies=cookies, headers=headers)

# hard code


def getMultipleInfoThreeLevel(datas, fields):
  jsonDatas = []
  for data in datas:
    jsonData = {}
    jsonData['name'] = data['name']
    jsonData['attributes'] = []

    attributes = data['attributes']
    for attribute in attributes:
      attributeJson = {}
      for field in fields:
        attributeJson[field] = attribute[field]
    jsonDatas.append(jsonData)
  return jsonDatas


def getMultipleInfo(datas, fields):
  res = []
  for data in datas:
    jsonData = {}
    for field in fields:
      if field == 'original_id':
        jsonData[field] = data['id']
      else:
        jsonData[field] = data[field]
    res.append(jsonData)
  return res


def replaceIdToOriginalId(data):
  return json.loads(json.dumps(data).replace('"id":', '"original-id":'))


def tryCatchInfo(field, data):
  try:
    if field == 'images':
      return data[field][0]['medium_url']
    return data[field]
  except:
    print(f'Error when get {field}')
    return None


def getInfo(data):
  original_id = tryCatchInfo('id', data)
  name = tryCatchInfo('name', data)
  price = tryCatchInfo('price', data)
  original_price = tryCatchInfo('original_price', data)
  discount = tryCatchInfo('discount', data)
  discount_rate = tryCatchInfo('discount_rate', data)
  rating_average = tryCatchInfo('rating_average', data)
  review_count = tryCatchInfo('review_count', data)
  review_text = tryCatchInfo('review_text', data)
  image = tryCatchInfo('images', data)
  description = tryCatchInfo('description', data)
  if description:
    description = re.sub('<.+?>',  '', description, flags=re.A).strip()
    description = re.sub('\s+',  ' ', description, flags=re.A).strip()
  return f'{original_id}|{name}|{price}|{original_price}|{discount}|{discount_rate}|{rating_average}|{review_count}|{review_text}|{image}|{description}'
#   jsonRes['warranty_policy'] = tryCatchInfo('warranty_policy', data)
#   jsonRes['short_url'] = tryCatchInfo('short_url', data)
#   jsonRes['short_description'] = tryCatchInfo(
#       'short_description', data)
#   jsonRes['thumbnail_url'] = tryCatchInfo('thumbnail_url', data)
#   jsonRes['day_ago_created'] = tryCatchInfo('day_ago_created', data)
#   jsonRes['all_time_quantity_sold'] = tryCatchInfo(
#       'all_time_quantity_sold', data)
  # jsonRes['warranty_info'] = tryCatchInfo('warranty_info', data)
  # jsonRes['authors'] = tryCatchInfo(
  #     'authors', replaceIdToOriginalId(data))
  # jsonRes['specifications'] = tryCatchInfo('specifications', data)
  # jsonRes['configurable_options'] = tryCatchInfo(
  #     'configurable_options', data)
  # jsonRes['highlight'] = tryCatchInfo('highlight', data)
  # jsonRes['quantity_sold'] = tryCatchInfo('quantity_sold', data)
  # jsonRes['categories'] = tryCatchInfo(
  #     'categories', replaceIdToOriginalId(data))
  # jsonRes['brand'] = tryCatchInfo('brand', replaceIdToOriginalId(data))


product_params = {
    'platform': 'web',
    'version': '3',
}


def getDetailProduct(product, category, logger, retry=1):
  global queues
  try:
    ecommerce = 'TIKI'
    logger.info('sending request...')
    product_response = requests.get(f'https://tiki.vn/api/v2/products/{product["id"]}',
                                    params=product_params, cookies=cookies, headers=headers)
    data = product_response.json()
    logger.info('Handling info...')
    infoReturn = getInfo(data)
    res = f'{ecommerce}|{category}|{infoReturn}'
    # print(jsonRes)
    queues.put(res)
    # logging.info(jsonRes)
    logger.info('Done...')
  except Exception as e:
    print(e)
    if retry >= 1:
      return
    return getDetailProduct(product, logger, retry+1)


LIMIT = 20

products_params = {
    'limit': LIMIT,
    'include': 'advertisement',
    'page': '1',
    'category': '8322',
}


def getListProducts(i, category_id, category, logger):
  global logging

  threads = []
  products_params['page'] = i
  products_params['category'] = category_id
  logger.info('Request list products...')
  products_response = requests.get('https://tiki.vn/api/v2/products',
                                   params=products_params, cookies=cookies, headers=headers)
  # print(products_response.json())
  products = products_response.json()['data']
  for idx, product in enumerate(products):
    logger.info('Request product...')
    subLogger = logging.getLogger(f'Thread {i}.{idx}')
    thread = Thread(target=getDetailProduct, args=(
        product, category, subLogger))
    thread.start()
    threads.append(thread)
    sleep(1)

  for thread in threads:
    thread.join()


df = pd.read_csv('data.csv', names=['ecommerce', 'category', 'original_id',
                                    'name',
                                    'price',
                                    'original_price',
                                    'discount',
                                    'discount_rate',
                                    'rating_average',
                                    'review_count',
                                    'review_text', 'image', 'description'])


def writeToFile():
  global queues, concurrency, logging

  cnt = 0
  while True:
    if not queues.empty():
      value = queues.get()
      if value == None:
        break
      cnt += 1
      df.loc[len(df)] = str(value).split('|')
    else:
      logging.info(f'Queue: Counting: {cnt}, queue-size: {queues._qsize()}')
      sleep(2)

  df.to_csv('data.csv', mode='w+')
  logging.info('Write to file success...')


# get list products
strings = time.strftime("%Y,%m,%d,%H,%M,%S")
timeFormat = '_'.join(strings.split(','))
logging.basicConfig(filename=f'./logs/log_{timeFormat}_.txt',
                    filemode='w+',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


capacity = 1000000
totalRows = 0
threads = []
queues = Queue(capacity)

# get categories
url = "https://api.tiki.vn/raiden/v2/menu-config?platform=desktop"

payload = {}

response = requests.get(url, headers=headers,
                        cookies=cookies, data=payload).json()
categories = response['menu_block']['items']

fileThread = Thread(target=writeToFile)
fileThread.start()

for category in categories:
  category_splitted = category['link'].split('/')
  category_id = category_splitted[-1][1:]
  category_name = category_splitted[-2]

  # print(category_id, category_name)

  for i in range(1, (2000//LIMIT)+1):
    logger = logging.getLogger(f'Thread {i}')
    thread = Thread(target=getListProducts, args=(
        i, category_id, category_name, logger))
    thread.start()
    threads.append(thread)
    sleep(20)

  for thread in threads:
    thread.join()
  queues.put(None)
  logging.info('Done...')
  sleep(20)
