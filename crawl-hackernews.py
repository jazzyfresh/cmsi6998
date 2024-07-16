import requests
import sqlite3

id = 8863

url_base = "https://hacker-news.firebaseio.com/v0/item/"
# url = f"{url_base}{id}.json"
url = lambda : f"{url_base}{id}.json"
page = requests.get(url())
payload = page.json()
print(payload)


connection = sqlite3.connect("hackernews.db")
cursor = connection.cursor()
columns = ["id","score","time","title","type","by","url"]
columns_sql = ",".join(columns)
print(columns_sql)

cursor.execute(f"create table items  ({columns_sql})")
# cursor.execute("create table kids (parent_id, kid_id)")

values = [ str(payload[key]) for key in columns ]
values_sql = ",".join(values)
insert_sql = f"insert into items ({columns_sql}) values (?,?,?,?,?,?,?)"
print(insert_sql)
print(tuple(values))

cursor.execute(insert_sql, tuple(values))
connection.commit()

