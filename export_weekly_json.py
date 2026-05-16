import sqlite3
import json
from datetime import datetime, timedelta

DB_PATH = r'D:\wewe-rss\data\wewe-rss.db'
OUTPUT_FILE = 'weekly_articles.json'

TARGET_IDS = ['MP_WXS_3271041950', 'MP_WXS_3298479661', 'MP_WXS_3931590079']
MP_NAME_MAP = {
    'MP_WXS_3271041950': '数字经济与商业模式',
    'MP_WXS_3298479661': '新智元',
    'MP_WXS_3931590079': '国家数据局',
}

since = int((datetime.now() - timedelta(days=30)).timestamp())

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

articles = []
for mp_id in TARGET_IDS:
    cursor.execute(
        "SELECT title, id, publish_time FROM articles WHERE mp_id=? AND publish_time>=? ORDER BY publish_time DESC",
        (mp_id, since)
    )
    for title, aid, pub_time in cursor.fetchall():
        articles.append({
            'title': title,
            'url': f'https://mp.weixin.qq.com/s/{aid}',
            'source': MP_NAME_MAP.get(mp_id, mp_id),
            'date': datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d')
        })

conn.close()

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f'导出 {len(articles)} 篇文章到 {OUTPUT_FILE}')