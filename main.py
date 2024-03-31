# %%
import requests
import json
from queue import Queue
from threading import Thread
from time import sleep
import pandas as pd
import re
import logging
import coloredlogs
from datetime import datetime
import sys
import random

sys.tracebacklimit = 0
logging.raiseExceptions = False

# %%
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

capacity = 1000000
totalRows = 0
threads = []
queues = Queue(capacity)

# %%


def getLogging(threadName):
  logger = logging.getLogger(threadName)
  coloredlogs.install(level='INFO', logger=logger, isatty=True,
                      fmt='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s')
  return logger

# %%
# get all categories


categories_params = {
    'platform': 'desktop',
}

category_response = requests.get('https://api.tiki.vn/raiden/v2/menu-config',
                                 params=categories_params, cookies=cookies, headers=headers)

# %%
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

# %%


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

# %%


def replaceIdToOriginalId(data):
  return json.loads(json.dumps(data).replace('"id":', '"original_id":'))

# %%


def tryCatchInfo(field, data):
  try:
    if field == 'images':
      return data[field][0]['medium_url']
    return data[field]
  except:
    print(f'Error when get {field}')
    return None

# %%


def getInfo(data, logger, category):
  global queues

  logger.info('Handling data...')
  original_id = tryCatchInfo('id', data)
  name = tryCatchInfo('name', data)
  price = tryCatchInfo('price', data)
  original_price = tryCatchInfo('original_price', data)
  discount = tryCatchInfo('discount', data)
  discount_rate = tryCatchInfo('discount_rate', data)
  # rating_average = tryCatchInfo('rating_average', data)
  # review_count = tryCatchInfo('review_count', data)
  # review_text = tryCatchInfo('review_text', data)
  # image = tryCatchInfo('images', data)
  # description = tryCatchInfo('description', data)
  # if description:
  #   description = re.sub('<.+?>',  '', description, flags=re.A).strip()
  #   description = re.sub('\s+',  ' ', description, flags=re.A).strip()
  # return f'{original_id},{name},{price},{original_price},{discount},{discount_rate},{rating_average},{review_count},{review_text},{image},{description}'
  logger.info('Return data...')
  queues.put(
      f'TIKI,{category},{original_id},"{name}",{price},{original_price},{discount},{discount_rate}')

# %%
# product_params = {
#     'platform': 'web',
#     'version': '3',
# }


# def getDetailProduct(product, category, logger, retry=1):
#   global queues
#   try:
#     ecommerce = 'TIKI'
#     logger.info('sending detail product request...')
#     product_response = requests.get(f'https://tiki.vn/api/v2/products/{product["id"]}',
#                                     params=product_params, cookies=cookies, headers=headers)
#     data = product_response.json()
#     logger.info('Handling info...')
#     infoReturn = getInfo(data)
#     # res = f'{ecommerce},{category},{infoReturn}'
#     # print(jsonRes)
#     # queues.put(res)
#     # logging.info(jsonRes)
#     logger.info('Done...')
#   except Exception as e:
#     # logger.error(e)
#     if retry >= 3:
#       return
#     sleep(random.randint(30, 60))
#     logger.warning('Retry request detail product')
#     return getDetailProduct(product, logger, retry+1)

# %%
LIMIT = 40

products_params = {
    'limit': LIMIT,
    'include': 'advertisement',
    'page': '1',
    'category': '8322',
}


def getListProducts(i, category_id, category, retry=1):
  threads = []

  try:
    logger = getLogging(f'Thread {i}-{category}')

    products_params['page'] = i
    products_params['category'] = category_id
    logger.info('Request list products...')
    products_response = requests.get('https://tiki.vn/api/v2/products',
                                     params=products_params, cookies=cookies, headers=headers)
    # print(products_response.json())
    products = products_response.json()['data']
    logger.info('DONE request list products...')
    for idx, product in enumerate(products):
      subLogger = getLogging(f'Thread {i}.{idx}-{category}')
      thread = Thread(target=getInfo, args=(product, subLogger, category))
      threads.append(thread)
      thread.start()

      # handle detail product
      # thread = Thread(target=getDetailProduct, args=(
      #     product, category, subLogger))
      # thread.start()
      # threads.append(thread)
      # break
      # sleep(random.randint(40, 70))

    logger.info(f'Before join {threads}')
    for thread in threads:
      thread.join()
    logger.info(f'After join {threads}')
  except:
    if retry >= 3:
      logger.error('Can not request products')
      return
    sleep(10)
    logger.warn('Retry request products')
    return getListProducts(i, category_id, category, retry+1)


# %%
columns = ['ecommerce', 'category', 'original_id', 'name', 'price',
           'original_price', 'discount', 'discount_rate']
# df = pd.read_csv('./data/data.csv', names=[])


def writeToFile():
  global queues, concurrency

  logger = getLogging('FILE')
  fileName = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

  f = open(f'./data/{fileName}.csv', 'w+')
  f.write(','.join(columns)+'\n')

  cnt = 0
  while True:
    if not queues.empty():
      value = queues.get()
      if value == None:
        break
      cnt += 1
      f.write(f'{value}\n')
      # try:
      #   pd.concat(value, df, axis=1, ignore_index=True)
      # except Exception as e:
      #   logger.error(e)
      #   logger.error(f'VALUE RECEIVE: {value}')
    else:
      logger.info(f'Queue: Counting: {cnt}, queue-size: {queues._qsize()}')
      sleep(10)

  # df.to_csv(f'./data/{fileName}.csv', mode='w+')
  f.close()
  logger.info('Write to file success...')

# %%


def crawlMultipleCategories(category):
  threads = []

  logger = logging.getLogger(f'{category}')
  category_splitted = category['link'].split('/')
  category_id = category_splitted[-1][1:]
  category_name = category_splitted[-2]

  # print(category_id, category_name)

  for i in range(1, (2000//LIMIT)+1):
    thread = Thread(target=getListProducts, args=(
        i, category_id, category_name))
    thread.start()
    threads.append(thread)
    # break
    sleep(1)
    # sleep(random.randint(5, 10))
  logger.info(f'Before join: {threads}')
  for thread in threads:
    thread.join()
  logger.info(f'After join: {threads}')


# %%
# get categories
url = "https://api.tiki.vn/raiden/v2/menu-config?platform=desktop"

payload = {}

logger = getLogging('ROOT')
logger.info('Request all categories...')
response = requests.get(url, headers=headers,
                        cookies=cookies, data=payload).json()
categories = response['menu_block']['items']
logger.info('DONE Request categories...')
fileThread = Thread(target=writeToFile)
fileThread.start()

for category in categories:
  thread = Thread(target=crawlMultipleCategories, args=(category,))
  threads.append(thread)
  thread.start()
  # break
  sleep(40)
  # sleep(random.randint(10, 20))
logger.info(f'Before join: {threads}')
for thread in threads:
  thread.join()
logger.info(f'After join: {threads}')
sleep(10*60)
queues.put(None)
logger.info('Done...')
