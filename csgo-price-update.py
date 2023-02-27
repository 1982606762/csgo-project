import requests
import datetime
import time
import sqlite3
import os
import configparser

config = configparser.ConfigParser()
config.read('project.cfg')
db = config.get('DATABASE','db')
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
    '摩托手套（★） | 交运 (略有磨损)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=45493&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005486525',
    '刺刀（★） | 澄澈之水 (略有磨损)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=42373&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673005852956',
    '专业手套（★） | 渐变大理石 (久经沙场)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=835939&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673006033934',
    'USP 消音版 | 印花集 (崭新出厂)': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=900565&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673006071444',
    'USP 消音版 | 印花集 (崭新出厂)1': 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=900565&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1673006071444',
}
stock = {
    '火神': [1099,1],
    '爪子刀（★） | 森林 DDPAT (久经沙场': [1340,1],
    '摩托手套（★） | 交运 (略有磨损)': [870,1],
    '刺刀（★） | 澄澈之水 (略有磨损)': [1395,1],
    '专业手套（★） | 渐变大理石 (久经沙场)': [2020,1],
    'USP 消音版 | 印花集 (崭新出厂)': [1400,2],
}

# define some parameters
cost = 0
cur = 0
today=datetime.date.today()

def insert_item(urldict):
    now = datetime.datetime.now()
    timenow = now.strftime("%Y-%m-%d %H:%M:%S")
    ret = ""
    for name, url in urldict.items():
        # check if the item already exists in the database
        c.execute("SELECT itemName FROM items WHERE itemName = ?", (name,))
        result = c.fetchone()
        if result is not None:
            # update the item
            c.execute("UPDATE items SET itemLink = ? WHERE itemName = ?", (url, name))
            conn.commit()
            ret += f"Record {name} updated successfully at {timenow}.\n"
        else:
            # insert a new record for the item
            c.execute("INSERT INTO items (itemName, itemLink) VALUES (?, ?)", (name, url))
            conn.commit()
            ret += f"New record {name} inserted successfully at {timenow}.\n"
    return ret

def update_price():
    now = datetime.datetime.now()
    timenow = now.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    ret = ""
    c.execute('SELECT * FROM items')
    data = c.fetchall()
    for i in data:
        name = i[1]
        goods_id = i[2]
        url = f'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={goods_id}&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_={timestamp}'
        r = requests.get(url, headers=headers, cookies={})
        data = r.json()
        if data['data']['items']:
            price = round(eval(data['data']['items'][0]['price']),2)
            # 判断是否有今天的数据
            c.execute('SELECT * FROM price WHERE itemName = ? AND Date = ?', (name, timenow))
            result = c.fetchone()
            if result is not None:
                # update the price
                c.execute("UPDATE price SET itemPrice = ? WHERE itemName = ? AND Date = ?", (price, name, timenow))
                conn.commit()
                ret += f"Record {name} updated successfully at {timenow}.\n"
            else:
                # insert a new record for the item
                c.execute("INSERT INTO price (itemName,itemPrice, Date) VALUES (?, ?, ?)", (name, price, timenow))
                conn.commit()
                ret += f"New record {name} inserted successfully at {timenow}.\n"
    return ret

def show_notification(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

def insert():
    log = ""
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
                log += "添加" + name + "成功" + "价格：" + str(curprice)
            
            num -=1
    try:
        conn.commit()
    except:
        pass
    # log(log)

def update():
    log = ""
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
                log += "更新" + name + "成功" + "价格：" + str(curprice)
            num -=1
    try:
        conn.commit()
    except:
        pass
    # log(log)

def log(content):
    c.execute("INSERT INTO log (content, date) VALUES (?, ?)", 
        (content, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
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
    priceupdate = update_price()
    show_notification("priceupdate", priceupdate)

def validate():
    sql_text_select = "SELECT * FROM stock WHERE date = '%s'" % today
    c.execute(sql_text_select)
    result = c.fetchall()
    if not result:
        show_notification("Error", "Cookie Maybe Expired, Please Check It")
        
main()
# view()
# validate()

# 关闭数据库连接
conn.close()
