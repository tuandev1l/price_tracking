import requests
import json
from queue import Queue
from threading import Thread
from time import sleep
import logging

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


def getInfo(data, jsonRes):
  jsonRes['original_id'] = tryCatchInfo('id', data)
  jsonRes['name'] = tryCatchInfo('name', data)
#   jsonRes['short_url'] = tryCatchInfo('short_url', data)
#   jsonRes['short_description'] = tryCatchInfo(
#       'short_description', data)
  jsonRes['price'] = tryCatchInfo('price', data)
  jsonRes['original_price'] = tryCatchInfo('original_price', data)
  jsonRes['discount'] = tryCatchInfo('discount', data)
  jsonRes['discount_rate'] = tryCatchInfo('discount_rate', data)
  jsonRes['rating_average'] = tryCatchInfo('rating_average', data)
  jsonRes['review_count'] = tryCatchInfo('review_count', data)
  jsonRes['review_text'] = tryCatchInfo('review_text', data)
#   jsonRes['thumbnail_url'] = tryCatchInfo('thumbnail_url', data)
#   jsonRes['day_ago_created'] = tryCatchInfo('day_ago_created', data)
#   jsonRes['all_time_quantity_sold'] = tryCatchInfo(
#       'all_time_quantity_sold', data)
  jsonRes['description'] = tryCatchInfo('description', data)
#   jsonRes['warranty_policy'] = tryCatchInfo('warranty_policy', data)
  jsonRes['images'] = tryCatchInfo('images', data)
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

  return jsonRes


product_params = {
    'platform': 'web',
    'version': '3',
}


def getDetailProduct(product, category, logger, retry=1):
  global queues
  try:
    jsonRes = {}
    jsonRes['category'] = category
    # jsonRes['seller_name'] = product['seller_name']
    jsonRes['ecommerce'] = 'TIKI'
    logger.info('sending request...')
    product_response = requests.get(f'https://tiki.vn/api/v2/products/{product["id"]}',
                                    params=product_params, cookies=cookies, headers=headers)
    data = product_response.json()
    logger.info('Handling info...')
    getInfo(data, jsonRes)
    print(jsonRes)
    # queues.put(jsonRes)
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
  threads = []
  products_params['page'] = i
  products_params['category'] = category_id
  logger.info('Request list products...')
  products_response = requests.get('https://tiki.vn/api/v2/products',
                                   params=products_params, cookies=cookies, headers=headers)
  products = products_response.json()['data']
  for product in products:
    logger.info('Request product...')
    thread = Thread(target=getDetailProduct, args=(
        product, category, logger))
    thread.start()
    threads.append(thread)
    sleep(0.5)
    break

  for thread in threads:
    thread.join()


# def writeToFile():
#   global queues, concurrency, logging

#   cnt = 0
#   data = []
#   while True:
#     if not queues.empty():
#       value = queues.get()
#       if value == None:
#         break
#       cnt += 1
#       data.append(value)
#     else:
#       logging.info(f'Queue: Counting: {cnt}, queue-size: {queues._qsize()}')
#       sleep(2)

#   jsonData = {'data': data}
#   with open('data.json', 'w+', encoding='utf-8') as f:
#     # logging.info(data)
#     f.write(json.dumps(jsonData))
#   logging.info('Write to file success...')


# get list products
logging.basicConfig(filename=f'log.txt',
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

# fileThread = Thread(target=writeToFile)
# fileThread.start()

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
    sleep(10)
    break

  for thread in threads:
    thread.join()
  logging.warning(f'Threads: {threads}')
  queues.put(None)
  logging.info('Done...')
  break
