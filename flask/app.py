from flask import Flask, render_template, request, redirect, url_for,Response,jsonify
import sqlite3
import json
import subprocess
import chardet
import time
import configparser

config = configparser.ConfigParser()
config.read('../project.cfg')
db = config.get('DATABASE','db')
url = config.get('WEBSITE','url')
today = time.strftime("%Y-%m-%d", time.localtime())
# duplicate = ["USP 消音版 | 印花集 (崭新出厂)","沙漠之鹰 | 钴蓝禁锢 (崭新出厂)"]

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html",url=url)

@app.route('/home', methods=['GET'])
def home():
    return render_template("index.html",url=url)

@app.route('/profit', methods=['GET'])
def profit():
    return render_template("profit.html",url=url)

@app.route('/log', methods=['GET'])
def log():
    return render_template("log.html")


@app.route('/api/logs')
def get_logs():
    output = subprocess.check_output(['tail', '-n', '50', '/root/qbitdown/log'])
    logs = output.decode('utf-8', 'ignore').split('\n')
    return jsonify({'logs': logs})

@app.route('/stock', methods=['GET'])  
def stock():
    # 链接数据库
    conn = sqlite3.connect(db)
    c = conn.cursor()
    # 取数据
    c.execute('SELECT * FROM stock ORDER BY date ASC , CurrentPrice DESC')
    data = c.fetchall()

    # 辅助数组
    dates = []
    names = []
    # 向前端返回的数据
    datalist = {"Date":[], "Name": [], "data1":[],"profitlist":[],"cost":0,"curr":0,"profit":0,"profitrate":0}
    for i in data:
        dates.append(i[0])
        names.append(i[1])
    # 向数组中添加数据
    temp = []
    for i in dates:
        if i not in temp:
            temp.append(i)
    datalist["Date"] = temp
    temp = []
    for i in names:
        if i not in temp:
            temp.append(i)
    datalist["Name"] = temp
    for i in datalist["Name"]:
        temp = {"name": "", "type": "", "stack": "", "data":[]}
        temp["name"] = i
        temp["type"] = "line"
        # if i in duplicate:
        #     flag = 0
        #     for j in data:
        #         if i == j[1]:
        #             if flag % 2 == 0:
        #                 temp["data"].append(j[2])
        #             flag += 1
        # else:  
        for j in data:
            if i == j[1]:
                temp["data"].append(j[2])
        datalist["data1"].append(temp)
    # 计算成本，现价，盈利，盈利率
    c.execute("SELECT SUM(OriginalPrice) FROM stock WHERE date = '%s'" % today)
    cost = c.fetchall()[0][0]
    datalist["cost"] = cost
    datalist["cost"] = round(datalist["cost"],2)
    c.execute("SELECT SUM(CurrentPrice) FROM stock WHERE date = '%s'" % today)
    curr = c.fetchall()[0][0]
    datalist["curr"] = curr
    datalist["curr"] = round(datalist["curr"],2)
    datalist["profit"] = round(datalist["curr"] - datalist["cost"],2)
    datalist["profitrate"] = str(round(datalist["profit"] / datalist["cost"] * 100,2)) + "%"
    # 计算每天的收益率
    c.execute('''SELECT 
         ROUND(SUM(CurrentPrice - OriginalPrice)/SUM(OriginalPrice),5) as DailyProfit
        FROM 
        stock
        GROUP BY 
        Date
        ORDER BY 
        Date
        ''')
    data = c.fetchall()
    for i in data:
        datalist["profitlist"].append(i[0])
    
    return Response(json.dumps(datalist), mimetype='application/json')
    # return Response(json.dumps(data), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
