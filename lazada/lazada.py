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
    '__wpkreporterwid_': 'b098fe6c-b575-4d33-9072-e8ec00cc27ec',
    't_fv': '1705896906459',
    't_uid': 'IlpHkJ7rzS1Yj4tR85liRloE35Qglibc',
    'lzd_cid': '6645c160-b4d1-49a1-bfe8-9a2c566f9c58',
    'lwrid': 'AQGNL2Gxp6eXtXZooAkv2RpuIyxx',
    '_bl_uid': '5gly5r5RoI9ew1zyqxbwe8ntkjds',
    '__itrace_wid': '6c630741-865a-4782-1413-91059f0b1b61',
    'hng': 'VN|vi|VND|704',
    'userLanguageML': 'vi',
    't_sid': 'N53JRQCLzD94F4GHWum7QmPKZAiJ8tvC',
    'utm_channel': 'NA',
    'lzd_sid': '125761204bc12dbc56af4f8923428aec',
    '_tb_token_': 'e880ee173e9e1',
    '_m_h5_tk': '26c2db219f281878c0c132e6e4341875_1711932943300',
    '_m_h5_tk_enc': '92bb8cd14776e6af5acb4e982bd4dd0f',
    'x5sec': '7b22617365727665722d6c617a6164613b33223a22617c4350725470374147454a6a62346f514849676c795a574e686348526a61474577744c71433041464b4d4441784d446c6d5a6a41774d4441774d4449774d4441774d4441774d4441774e444a684e7a4a685954426a4d6d45784f4445305a6a45344f4459334f44426c5a513d3d222c22733b32223a2266356363636165383633396237656166227d',
    'lzd_uid': '200098101834',
    'lzd_b_csg': 'f23dee20',
    'sgcookie': 'E100rcLr8otJqAqiCtMDfpRMcvmPebVwGMKX8igykRf9rvqx2RFDONmca2cpPly3kRhJcRg7n4579E%2BXqp91fENxLojcf0xKffYg46rMTaz46Uc%3D',
    'lzd_uti': '%7B%22fpd%22%3A%229999-99-99%22%2C%22lpd%22%3A%229999-99-99%22%2C%22cnt%22%3A%220%22%7D',
    'bubufcc': '7',
    'isg': 'BI6OU0BkZPB_pdNwA7TJ7a3r321QD1IJTssSHLjXVhFMGy91JJ-YGY2aU193BUoh',
    'tfstk': 'fdss1aYW-LAUfeTtzteFFLtkmV-bL1ZPWx9AEtnZHhKtMjBJTnyiuPvXcB6yuCFc7m_XTTC2_PbNAK1wOiRN3G5IIM1S0cPgStnX0nFzaurPIAxDD7oX6EFksKXpMfagsCWMmnFU2cS4gOfWfH5eGneBvKJ9BnntXJGp3Bn9Hcpx9J9D58auVfrdFRnibmVnW7NfamnAvPY6NO3qDmIBCFsPBB6FLM965QTI-E-lcT6AbH_SMPBWxg8VvUEjxhW5JHpfm83XGU_RchjLfbv1JTtp_3USRh6FsgtOV5iwLHAMyZBaX0KNOCxCysyxPIXFPEQySfszc0R5IUgjdUmXdQyQdq0D3QAsrAt81M89Kp-4dJgPaFpHdhyQdq0DWpvn8JwIz_5..',
    'epssw': '1*GAdO11isM5EZT7GSIA7SZ-FFh2esNAkGZe789zU4IAfnxzL7N4UV7zFQsbhJH1B56T1j379A6TsGTp4Mw-BL33qi6T_0ov621TsGiX9WNZA0OQjUyzcPIbbwZOqMerUOTBddn_jnWtWujkDW34QRegt3xDmnetrnxJsGdLHpe4GW_Gwb_4-2EsNltsCZFCuIR1k17DmnY4QRetyR35..',
    '_m_h5_tk': '9aea390ff49d671507f17f431eebae83_1711909867730',
    '_m_h5_tk_enc': '230d594bf6f05c4e697f025178f372cd',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'referer': 'https://www.lazada.vn/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'x-csrf-token': 'e880ee173e9e1',
    'x-requested-with': 'XMLHttpRequest',
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


def replaceIdToOriginalId(data):
  return json.loads(json.dumps(data).replace('"id":', '"original_id":'))

# %%


def tryCatchInfo(field, data):
  try:
    if field == 'discount':
      return int(str(data[field]).split(' ')[0][:-1])
    if field == 'name':
      return data[field]
    return int(data[field])
  except:
    # print(f'Error when get {field}')
    if field == 'name':
      return None
    return 0

# %%


def getInfo(data, logger, category):
  global queues

  logger.info('Handling data...')
  original_id = tryCatchInfo('nid', data)
  name = tryCatchInfo('name', data)
  price = tryCatchInfo('price', data)
  discount_rate = tryCatchInfo('discount', data)
  # print(price, discount_rate)
  original_price = price
  discount = 0
  if price and discount_rate:
    original_price = round(price/(1-discount_rate/100))
    discount = original_price-price
  logger.info('Return data...')
  queues.put(
      f'LAZADA,{category},{original_id},"{name}",{price},{original_price},{discount},{discount_rate}')


# %%
LIMIT = 40

products_params = {
    'ajax': 'true',
    'page': '1',
}


def getListProducts(i, category, retry=1):
  threads = []

  try:
    logger = getLogging(f'Thread {i}-{category}')

    products_params['page'] = i
    logger.info('Request list products...')
    products_response = requests.get(f'https://www.lazada.vn/{category}/',
                                     params=products_params, cookies=cookies, headers=headers)
    # print(products_response.json())
    products = products_response.json()['mods']['listItems']
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

    # logger.info(f'Before join {threads}')
    for thread in threads:
      thread.join()
    # logger.info(f'After join {threads}')
  except:
    if retry >= 3:
      logger.error('Can not request products')
      return
    sleep(10)
    logger.warning('Retry request products')
    return getListProducts(i, category, retry+1)


# %%
columns = ['ecommerce', 'category', 'original_id', 'name', 'price',
           'original_price', 'discount', 'discount_rate']


def writeToFile():
  global queues, concurrency

  logger = getLogging('FILE')
  fileName = datetime.now().astimezone().strftime('%Y_%m_%d_%H_%M_%S')

  f = open(f'LAZADA_TEST_{fileName}.csv', 'w+')
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

  # print(category_id, category_name)
  logger.info('Get list of products')

  for i in range(1, 101):
    thread = Thread(target=getListProducts, args=(i, category))
    thread.start()
    threads.append(thread)
    # break
    sleep(0.5)
    # sleep(random.randint(5, 10))
  # logger.info(f'Before join: {threads}')
  for thread in threads:
    thread.join()
  # logger.info(f'After join: {threads}')


# %%
# get categories
with open('lazada_categories.json', 'r') as f:
  categories = json.loads(
      f.read())['data']['resultValue']['categoriesLpMultiFloor']['data']

categoriesUrl = []
for category in categories:
  for subCategory in category['level2TabList']:
    url = subCategory['categoryUrl']
    categoriesUrl.append(f'https:{url}')

# %%
print(categoriesUrl)

# %%
fileThread = Thread(target=writeToFile)
fileThread.start()

logger = getLogging('ROOT')
for url in categoriesUrl:
  category = url.split('/')[-1]
  thread = Thread(target=crawlMultipleCategories, args=(category,))
  threads.append(thread)
  thread.start()
  # break
  sleep(40)
  # sleep(random.randint(10, 20))
# logger.info(f'Before join: {threads}')
for thread in threads:
  thread.join()
# logger.info(f'After join: {threads}')
# sleep(10*60)
queues.put(None)
logger.info('Done...')
