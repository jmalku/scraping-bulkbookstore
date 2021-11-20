import requests
from bs4 import BeautifulSoup
import json
import math
import pandas as pd

req_header = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://bulkbookstore.com',
    'referer': 'https://bulkbookstore.com/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
}
req_payload = {
    'ajaxCatalog': 'v3',
    'resultsFormat': 'native',
    'siteId': '1h09sv',
    'domain': 'https://bulkbookstore.com/search',
    'sort.calculated_price': 'asc',
    'q': '',
    'userId': 'V3-E807C878-0452-436C-A434-5FC861BAFEBF'
}
req_url = f'https://1h09sv.a.searchspring.io/api/search/search.json'
resp = requests.post(req_url, json=req_payload, headers=req_header)
json_data = resp.json()
total_results = json_data['pagination']['totalResults']
get_data = json_data['results']
list_results = []
count = 0
for i in get_data:
    count += 1
    title = i['name']
    isbn = i['isbn_13']
    format = i['format']
    url = i['url']
    uid = i['uid']
    price = i['price']
    urls_ = "https://swymstore-v3pro-01.swymrelay.com/api/v2/provider/getPlatformProducts"
    querystring = {"pid": "GPFrde2/eUCfQWykuUxupELo3ngjCqpCF372SqCPO1A="}
    payload = f"productids=%5B{uid}%5D&regid=V74Z11jIHqkrC59e_RFdtRiL5MmtDkHPmU7aOQ2_tAXFoGxavlD4lTRjbbNd1_BLl4wdfdLWA95PgumLlWlwPhpPMBsT8QWPUsqpGF7_0bpdSLTIz-ZeXecQ9-v25oyDFP5eAN0v4Rr2UlV-lr9KcmI4XPGrIYBGsoyrmuHGwx8&sessionid=mucype0ybsfw73pd4ep6egew35tsokjddme9tbfu4a7guw16otf9d6pl722czw5y"
    headers = {
        'accept': "*/*",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9",
        'content-length': "276",
        'content-type': "application/x-www-form-urlencoded",
        'origin': "https://bulkbookstore.com",
        'referer': "https://bulkbookstore.com/",
        'sec-ch-ua': "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"96\", \"Google Chrome\";v=\"96\"",
        'sec-ch-ua-mobile': "?0",
        'sec-ch-ua-platform': "\"Windows\"",
        'sec-fetch-dest': "empty",
        'sec-fetch-mode': "cors",
        'sec-fetch-site': "cross-site",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        'cache-control': "no-cache",
    }
    response = requests.request("POST", urls_, data=payload, headers=headers, params=querystring)
    json_data = response.json()
    prices = json_data[0]['productdata']['warranty']
    if not prices:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all("script")
        for script in scripts:
            if "var prices" in script.text:
                text = script.text
                m_text = text.split('var prices')[1]
                m_text = m_text.split('prices.sort')[0]
                m_text = m_text.split('=')[1]
                m_text = m_text.split(';')[0]
                data = json.loads(m_text)
                discount = data[0]['discount']['value']
                min = data[0]['min']
                max = data[0]['max']
                dscont = float(price) * int(discount) / 100
                calculate = float(price) - float(dscont)


                def normal_round(n, decimals=0):
                    expoN = n * 10 ** decimals
                    if abs(expoN) - abs(math.floor(expoN)) < 0.5:
                        return math.floor(expoN) / 10 ** decimals
                    return math.ceil(expoN) / 10 ** decimals


                newRounding = normal_round(calculate, 2)
                prices = f'{newRounding:.2f}'
    else:
        prices = prices

    goal_data = {
        'title': title,
        'ISBN': isbn,
        'price': f'${prices}',
        'url': url,
    }
    list_results.append(goal_data)
    print(f'{count}. {goal_data}')
    df = pd.DataFrame(list_results)
    df.to_csv(f'sample_bulkbookstore.csv', index=False)
