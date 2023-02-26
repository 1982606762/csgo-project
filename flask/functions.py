import sqlite3
import datetime
import os

def show_notification(text, title=""):
    # echo text into a log file
    os.system("echo '%s' >> /root/csgo-project/notify.log" % text)
def insert_item(urldict,db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
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

def select_all_items(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT itemName,itemLink FROM items")
    items = c.fetchall()
    c.close()
    return items
