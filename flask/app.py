from flask import Flask, render_template, request, redirect, url_for,Response
import sqlite3
import json

duplicate = ["USP 消音版 | 印花集 (崭新出厂)","沙漠之鹰 | 钴蓝禁锢 (崭新出厂)"]
db = '/Users/xuanlang/study/python/csgo-project/csgo.db'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/stock', methods=['GET'])  
def stock():
    # 链接数据库
    conn = sqlite3.connect(db)
    c = conn.cursor()
    # 取数据
    c.execute('SELECT * FROM stock ORDER BY date ASC')
    data = c.fetchall()
    
    # 辅助数组
    dates = []
    names = []
    # 向前端返回的数据
    datalist = {"Date":[], "Name": [], "data1":[],"cost":"","curr":"","profit":"","profitrate":""}
    for i in data:
        dates.append(i[0])
        names.append(i[1])
    # 向数组中添加数据
    temp = []
    for i in dates:
        if i not in temp:
            temp.append(i)
    datalist["Date"] = temp
    datalist["Name"] = list(set(names))
    for i in datalist["Name"]:
        temp = {"name": "", "type": "", "stack": "", "data":[]}
        temp["name"] = i
        temp["type"] = "line"
        if i in duplicate:
            flag = 0
            for j in data:
                if i == j[1]:
                    if flag % 2 == 0:
                        temp["data"].append(j[2])
                    flag += 1
        else:  
            for j in data:
                if i == j[1]:
                    temp["data"].append(j[2])
        datalist["data1"].append(temp)
    # 计算成本，现价，盈利，盈利率
    c.execute("SELECT SUM(OriginalPrice) FROM stock WHERE date = '%s'" % datalist["Date"][0])
    datalist["cost"] = c.fetchall()[0][0]
    datalist["cost"] = round(datalist["cost"],2)
    c.execute("SELECT SUM(CurrentPrice) FROM stock WHERE date = '%s'" % datalist["Date"][0])
    datalist["curr"] = c.fetchall()[0][0]
    datalist["curr"] = round(datalist["curr"],2)
    datalist["profit"] = datalist["curr"] - datalist["cost"]
    datalist["profitrate"] = str(round(datalist["profit"] / datalist["cost"] * 100,2)) + "%"

    return Response(json.dumps(datalist), mimetype='application/json')
    # return Response(json.dumps(data), mimetype='application/json')

if __name__ == '__main__':
    app.run()
