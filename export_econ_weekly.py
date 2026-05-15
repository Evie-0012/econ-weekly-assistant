import sqlite3, json, os
from datetime import datetime, timedelta

# ---------- 映射字典（公众号ID -> 名称）----------
MP_NAME_MAP = {
    'MP_WXS_3271041950': '数字经济与商业模式',
    'MP_WXS_3298479661': '新智元',
    'MP_WXS_3931590079': '国家数据局',
    # 把你另外两个已有文章的公众号 ID 和名称填在下面：
    # 'MP_WXS_……': '……',
    # 'MP_WXS_……': '……',
}

DB_PATH = r'D:\wewe-rss\data\wewe-rss.db'
OUT_FILE = 'weekly_articles.json'

TARGET_MP_IDS = list(MP_NAME_MAP.keys())   # 目标公众号ID列表自动从字典获取

# 过滤关键词
EXCLUDE_KEYWORDS = ['核聚变', '聚变', '托卡马克', '仿星器', '等离子体', '人造太阳']

one_week_ago = int((datetime.now() - timedelta(days=7)).timestamp())

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

articles = []
for mp_id in TARGET_MP_IDS:
    cursor.execute('''
        SELECT title, id, publish_time FROM articles 
        WHERE mp_id = ? AND publish_time >= ?
        ORDER BY publish_time DESC
    ''', (mp_id, one_week_ago))
    for title, aid, pub_time in cursor.fetchall():
        if any(kw in title for kw in EXCLUDE_KEYWORDS):
            continue
        url = f'https://mp.weixin.qq.com/s/{aid}'
        date_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d')
        source_name = MP_NAME_MAP.get(mp_id, mp_id)  # 使用映射后的名称
        articles.append({
            "title": title,
            "url": url,
            "source": source_name,
            "date": date_str
        })

conn.close()

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f'导出 {len(articles)} 篇数字经济文章到 {OUT_FILE}')