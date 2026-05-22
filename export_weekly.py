import sqlite3, json, os
from datetime import datetime, timedelta

DB_PATH = os.path.join('data', 'wewe-rss.db')
OUT_FILE = 'weekly_articles.json'

one_week_ago = int((datetime.now() - timedelta(days=7)).timestamp())

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT title, id, mp_id, publish_time FROM articles WHERE publish_time >= ? ORDER BY publish_time DESC", (one_week_ago,))
rows = cursor.fetchall()
conn.close()

articles = []
for title, aid, mp_id, pub_time in rows:
    articles.append({
        "title": title,
        "url": f"https://mp.weixin.qq.com/s/{aid}",
        "source": mp_id,          # 可以后面做个映射，把 mp_id 换成公众号名称
        "date": datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d')
    })

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f'导出 {len(articles)} 篇文章到 {OUT_FILE}')