# -*- coding: utf-8 -*-
#   网易buff爬虫
import sqlite3
import configparser
import requests
import datetime
import random
import time
import re

# 读取配置文件
config = configparser.ConfigParser()
config.read('project.cfg')
db = config.get('DATABASE','db')
conn = sqlite3.connect(db)
c = conn.cursor()
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
# 添加某个饰品的180天历史价格
def insert_price_history(id):
    goods_id = id
    c.execute("SELECT itemName FROM items WHERE goods_id = ?", (goods_id,))
    item_name = c.fetchone()[0]
    # 获取当前时间戳
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    # 获取饰品的180天历史价格JSON
    url = f'https://buff.163.com/api/market/goods/price_history/buff?game=csgo&goods_id={goods_id}&currency=CNY&days=180&_={timestamp}'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    cookies = '__bid_n=18496259992cf2e3214207; vinfo_n_f_l_n3=49e4cead60e9d3de.1.0.1672862690279.0.1672862890719; NTES_CMT_USER_INFO=480722779%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B0sFPZr%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CeWQuYzA3MDdhZGE4NmJlNDAxMTlAMTYzLmNvbQ%3D%3D; Device-Id=B4v5yZkG89Z4oLnrEpqE; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=kpgEhR_CvxG4qW85ubT88o8.Py5yQg5OpM5J.k9sh4NsAS_c35FfLNxtEudpVkRflDGec0xCvjqvt430fYw42_YyD8U6pQC0CPsL4_bjCml6BvjTiYC1SJp4wpl7NPJxM4uLHVCLFfXm2Wl3CA76TF32eqgR5eftKcTYLRM0ECchYjCzaefiHZYMfTGwEiJpGd5LnBF5Pq3HRAV1WTJww.Geq2QBEDfCtYjSdWfm4buGz; S_INFO=1677419221|0|0&60##|17302206700; P_INFO=17302206700|1677419221|1|netease_buff|00&99|null&null&null#DK&null#10#0|&0||17302206700; remember_me=U1094623157|Xym8pO81NTnHP91stIRKuA0fSLVOSDTA; session=1-kjeKj96a1UTPbkOccy9-cwL7FmUWKKH62N3WBjCiom6Q2045772013; csrf_token=ImFiZWU4ZjI3ZTk0YjAyMzE0MTVmZTBmMmUzMWVkZmJlOTRhNmYzZDUi.Ft2MwA.lXrcg6XGkAfsiz-vxlysLypeVzM'
    cookie = {}
    for line in cookies.split(';'):
        name, value = line.strip().split('=', 1)
        cookie[name] = value
    # 随机休眠
    sleep_time = random.randint(1, 3)
    time.sleep(sleep_time)
    r = requests.get(url, headers=headers, cookies=cookie)
    data = r.json()
    print("处理饰品: " + item_name + "，休眠时间: " + str(sleep_time) + "秒"+ "，获取到的价格数量: " + str(len(data['data']['price_history'])) + "条")
    # 对每个价格进行插入操作
    added = 0
    for i in data['data']['price_history']:
        local_name = item_name
        pricetime = i[0]
        price = i[1]
        timeArray = datetime.datetime.utcfromtimestamp(pricetime / 1000)
        otherStyleTime = timeArray.strftime("%Y-%m-%d %H:%M:%S")
        # 判断是否已经存在
        c.execute("SELECT * FROM price WHERE itemName = ? AND Date = ?", (local_name, otherStyleTime))
        if c.fetchone() is None:
            c.execute("INSERT INTO price (itemName, Date, itemPrice, goods_id) VALUES (?, ?, ?, ?)", (local_name, otherStyleTime, price, goods_id))
            print(f'添加成功！{local_name} {otherStyleTime} {price} added')
            added += 1
        else:
            print(f'添加失败！{local_name} {otherStyleTime} already exists')
    conn.commit()
    print(f'{added} rows added')

# def insert_price_history(data):
#     added = 0
#     for i in data['data']['price_history']:
#         time = i[0]
#         price = i[1]
#         timeArray = datetime.datetime.utcfromtimestamp(time / 1000)
#         otherStyleTime = timeArray.strftime("%Y-%m-%d %H:%M:%S")
#         # 判断是否已经存在
#         c.execute("SELECT * FROM price WHERE itemName = ? AND Date = ?", (name, otherStyleTime))
#         if c.fetchone() is None:
#             c.execute("INSERT INTO price (itemName, Date, itemPrice) VALUES (?, ?, ?)", (name, otherStyleTime, price))
#             added += 1
#         else:
#             print(f'{name} {otherStyleTime} already exists')
#     conn.commit()
#     print(f'{added} rows added')
# add columns to table items named exterior, rarity, type, weapon
# c.execute("ALTER TABLE items ADD COLUMN exterior TEXT")
# c.execute("ALTER TABLE items ADD COLUMN rarity TEXT")
# c.execute("ALTER TABLE items ADD COLUMN type TEXT")
# c.execute("ALTER TABLE items ADD COLUMN weapon TEXT")
# conn.commit()

# delete column from table items named itemLink
# c.execute("ALTER TABLE items DROP COLUMN itemLink")

# 添加某个类别物品的信息
def insert_item_info(category):
    num = 15
    added = 0
    for i in range(num):
        print(f'page {i+1} is processing...')
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        url = f'https://buff.163.com/api/market/goods?game=csgo&page_num={i+1}&category={category}&use_suggestion=0&_={timestamp}'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        cookies = '__bid_n=18496259992cf2e3214207; vinfo_n_f_l_n3=49e4cead60e9d3de.1.0.1672862690279.0.1672862890719; NTES_CMT_USER_INFO=480722779%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B0sFPZr%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CeWQuYzA3MDdhZGE4NmJlNDAxMTlAMTYzLmNvbQ%3D%3D; Device-Id=B4v5yZkG89Z4oLnrEpqE; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=kpgEhR_CvxG4qW85ubT88o8.Py5yQg5OpM5J.k9sh4NsAS_c35FfLNxtEudpVkRflDGec0xCvjqvt430fYw42_YyD8U6pQC0CPsL4_bjCml6BvjTiYC1SJp4wpl7NPJxM4uLHVCLFfXm2Wl3CA76TF32eqgR5eftKcTYLRM0ECchYjCzaefiHZYMfTGwEiJpGd5LnBF5Pq3HRAV1WTJww.Geq2QBEDfCtYjSdWfm4buGz; S_INFO=1677419221|0|0&60##|17302206700; P_INFO=17302206700|1677419221|1|netease_buff|00&99|null&null&null#DK&null#10#0|&0||17302206700; remember_me=U1094623157|Xym8pO81NTnHP91stIRKuA0fSLVOSDTA; session=1-kjeKj96a1UTPbkOccy9-cwL7FmUWKKH62N3WBjCiom6Q2045772013; csrf_token=ImFiZWU4ZjI3ZTk0YjAyMzE0MTVmZTBmMmUzMWVkZmJlOTRhNmYzZDUi.Ft2MwA.lXrcg6XGkAfsiz-vxlysLypeVzM'
        cookie = {}
        for line in cookies.split(';'):
            name, value = line.strip().split('=', 1)
            cookie[name] = value
        sleeptime = random.randint(2, 5)
        print("sleeping for " + str(sleeptime) + " seconds")
        time.sleep(sleeptime)
        try:
            r = requests.get(url, headers=headers, cookies=cookie)
            data = r.json()
            if len(data['data']['items']) == 0:
                print("page " + str(i+1) + " is empty, skipping...")
                continue
            print("request successful, fetched " + str(len(data['data']['items'])) + " items")
        except:
            time.sleep(10)
            print("request failed, retrying...")
            r = requests.get(url, headers=headers, cookies=cookie)
            data = r.json()
            print("request successful, fetched " + str(len(data['data']['items'])) + " items")

        for items in data['data']['items']:
            itemName = items['name']
            goods_id = items['id']
            exterior = items['goods_info']['info']['tags']['exterior']['localized_name']
            rarity = items['goods_info']['info']['tags']['rarity']['localized_name']
            type = items['goods_info']['info']['tags']['type']['localized_name']
            try:
                weapon = items['goods_info']['info']['tags']['weapon']['localized_name']
            except:
                weapon = items['goods_info']['info']['tags']['type']['localized_name']
            print("adding item: " + itemName)
            # 如果当前goods_id没有就插入数据
            c.execute("SELECT * FROM items WHERE goods_id = ?", (goods_id,))
            if c.fetchone() is None:
                c.execute("INSERT INTO items (itemName, goods_id, exterior, rarity, type, weapon) VALUES (?, ?, ?, ?, ?, ?)", (itemName, goods_id, exterior, rarity, type, weapon))
                added += 1
            else:
                print("Insert failed: item already exists")
    print("added " + str(added) + " items in total")
    conn.commit()   
# get_item_info('weapon_knife_karambit', 15)


# 获取所有物品类别
def get_category(): 
    global category_list
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    cookies = '__bid_n=18496259992cf2e3214207; vinfo_n_f_l_n3=49e4cead60e9d3de.1.0.1672862690279.0.1672862890719; NTES_CMT_USER_INFO=480722779%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B0sFPZr%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CeWQuYzA3MDdhZGE4NmJlNDAxMTlAMTYzLmNvbQ%3D%3D; Device-Id=B4v5yZkG89Z4oLnrEpqE; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=kpgEhR_CvxG4qW85ubT88o8.Py5yQg5OpM5J.k9sh4NsAS_c35FfLNxtEudpVkRflDGec0xCvjqvt430fYw42_YyD8U6pQC0CPsL4_bjCml6BvjTiYC1SJp4wpl7NPJxM4uLHVCLFfXm2Wl3CA76TF32eqgR5eftKcTYLRM0ECchYjCzaefiHZYMfTGwEiJpGd5LnBF5Pq3HRAV1WTJww.Geq2QBEDfCtYjSdWfm4buGz; S_INFO=1677419221|0|0&60##|17302206700; P_INFO=17302206700|1677419221|1|netease_buff|00&99|null&null&null#DK&null#10#0|&0||17302206700; remember_me=U1094623157|Xym8pO81NTnHP91stIRKuA0fSLVOSDTA; session=1-kjeKj96a1UTPbkOccy9-cwL7FmUWKKH62N3WBjCiom6Q2045772013; csrf_token=ImFiZWU4ZjI3ZTk0YjAyMzE0MTVmZTBmMmUzMWVkZmJlOTRhNmYzZDUi.Ft2MwA.lXrcg6XGkAfsiz-vxlysLypeVzM'
    cookie = {}
    for line in cookies.split(';'):
        name, value = line.strip().split('=', 1)
        cookie[name] = value
    source_page_url = "https://buff.163.com/market/?game=csgo#tab=selling&page_num=1"
    cat_response = requests.get(url=source_page_url, headers=headers, cookies=cookie)
    html_text0 = cat_response.text
    category_list = re.findall( r'li value="weapon_(.+?)">', html_text0, re.M)
    for i in range(len(category_list)):
        category_list[i] = "weapon_" + category_list[i]
    return(category_list)

def main():
    # 获取category最后8项
    category_list = get_category()
    list = category_list[-8:]
    # 计算所需时间
    # timennow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # # 获取物品信息
    # for i in list:
    #     insert_item_info(i)
    #     print("finished " + i)
    # timeend = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # print("get item info time cost: " + str((time.mktime(time.strptime(timeend, "%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(timennow, "%Y-%m-%d %H:%M:%S"))) / 60) + " minutes")
    # 获取历史价格
    c.execute("SELECT goods_id FROM items")
    goods_id_list = c.fetchall()
    timennow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    num = 0
    for i in goods_id_list:
        num += 1
        pricelist = insert_price_history(i[0])
        timenew = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("进度："+ str(num) + "/" + str(len(goods_id_list)) + " " + str((time.mktime(time.strptime(timenew, "%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(timennow, "%Y-%m-%d %H:%M:%S"))) / 60) + " minutes")
    timeend = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("get history price time cost: " + str((time.mktime(time.strptime(timeend, "%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(timennow, "%Y-%m-%d %H:%M:%S"))) / 60) + " minutes")

if __name__ == '__main__':
    main()
    # 给price表添加列
    # c.execute("DELETE FROM price")
    # 删除数据库20-855行
    # c.execute("DELETE FROM items WHERE itemId BETWEEN 13 AND 19")
    # conn.commit()
    conn.close()    
