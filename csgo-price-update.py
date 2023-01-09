import requests
import datetime
import time
import sqlite3
import os

db = '/Users/xuanlang/study/python/csgo-project/csgo.db'
# Connect to the database
conn = sqlite3.connect(db)
c = conn.cursor()

# Define parameters for the request
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}
cookies = {}
# for line in cookie_str.split(';'):
#     name, value = line.strip().split('=', 1)
#     cookies[name] = value

# Define the URLs and the names of the items
urls = {
    '火神': 'https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=33976&page_num=1&_=1672999623684',
    '爪子刀（★） | 森林 DDPAT (久经沙场': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=43003&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1672999692189',
    'AWP | 野火 (略有磨损)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=773720&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1672999732600',
    '摩托手套（★） | 交运 (略有磨损)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=45493&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005486525',
    '沙漠之鹰 | 钴蓝禁锢 (崭新出厂)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=34396&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005525919',
    '沙漠之鹰 | 钴蓝禁锢 (崭新出厂)1': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=34396&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005525919',
    '刺刀（★） | 澄澈之水 (略有磨损)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=42373&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005852956',
    '专业手套（★） | 大腕 (久经沙场)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=45376&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005911415',
    '沙漠之鹰 | 印花集 (崭新出厂)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=781660&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005946734',
    '摩托手套（★） | 嘭！ (久经沙场)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=45432&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005982667',
    '专业手套（★） | 渐变大理石 (久经沙场)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=835939&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673006033934',
    'USP 消音版 | 印花集 (崭新出厂)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=900565&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673006071444',
    'USP 消音版 | 印花集 (崭新出厂)1': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=900565&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673006071444'
}
stock = {
    '火神': [1099,1],
    '爪子刀（★） | 森林 DDPAT (久经沙场': [1340,1],
    'AWP | 野火 (略有磨损)': [404,1],
    '摩托手套（★） | 交运 (略有磨损)': [870,1],
    '沙漠之鹰 | 钴蓝禁锢 (崭新出厂)': [315,2],
    '刺刀（★） | 澄澈之水 (略有磨损)': [1395,1],
    '专业手套（★） | 大腕 (久经沙场)': [1340,1],
    '沙漠之鹰 | 印花集 (崭新出厂)': [590,1],
    '摩托手套（★） | 嘭！ (久经沙场)': [2290,1],
    '专业手套（★） | 渐变大理石 (久经沙场)': [2020,1],
    'USP 消音版 | 印花集 (崭新出厂)': [1400,2],
}

# define some parameters
cost = 0
cur = 0
today=datetime.date.today()


def show_notification(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

def insert():
    for name, status in stock.items():
        num = status[1]
        url = urls[name]
        oldprice = status[0]
        while num:
            time.sleep(0.3)
            r = requests.get(url, headers=headers, cookies=cookies)
            data = r.json()
            
            if data['data']['items']:
                curprice = round(eval(data['data']['items'][0]['price']),2)
                # 写入数据库
                sql_text_insert = "INSERT INTO stock VALUES ('%s', '%s', '%s', '%s')" % (today,name, curprice, oldprice)
                c.execute(sql_text_insert)
            
            num -=1
    conn.commit()

def update():
    for name, status in stock.items():
        num = status[1]
        url = urls[name]
        while num:
            time.sleep(0.3)
            r = requests.get(url, headers=headers, cookies=cookies)
            data = r.json()
            if data['data']['items']:
                curprice = round(eval(data['data']['items'][0]['price']),2)   
                # 写入数据库
                sql_text_update = "UPDATE stock SET CurrentPrice = '%s' WHERE name = '%s' AND date = '%s'" % (curprice, name, today)
                c.execute(sql_text_update)
            num -=1
    conn.commit()

def view():
    sql_text_select = "SELECT SUM(OriginalPrice) FROM stock WHERE date = '%s'" % today
    c.execute(sql_text_select)
    cost = c.fetchall()[0][0]
    sql_text_select = "SELECT SUM(CurrentPrice) FROM stock WHERE date = '%s'" % today
    c.execute(sql_text_select)
    cur = c.fetchall()[0][0]
    str_result = "成本: %s 现价: %s 盈利: %s 盈利率: %s" % (cost, format(cur,".2f"), round(cur-cost,2), round((cur-cost)/cost* 100,2))
    show_notification("csgo track result", str_result)

def main():
    # 判断数据库中是否有今天的数据
    sql_text_select = "SELECT * FROM stock WHERE date = '%s'" % today
    c.execute(sql_text_select)
    result = c.fetchall()
    if result:
        update()
    else:
        insert()

def validate():
    sql_text_select = "SELECT * FROM stock WHERE date = '%s'" % today
    c.execute(sql_text_select)
    result = c.fetchall()
    if not result:
        show_notification("Error", "Cookie Maybe Expired, Please Check It")
        
main()
view()
validate()

# 关闭数据库连接
conn.close()
