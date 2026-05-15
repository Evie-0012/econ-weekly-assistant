import sqlite3, json, os
from datetime import datetime, timedelta

DB_PATH = os.path.join('data', 'wewe-rss.db')
OUT_FILE = 'weekly_articles.json'

# 目标公众号 mp_id（从 WeWe RSS 网页地址栏可获取）
TARGET_MP_IDS = [
    'MP_WXS_1234567890',  # 数字经济与商业模式
    'MP_WXS_2345678901',  # 新智元
    'MP_WXS_3456789012',  # 量子位
    'MP_WXS_4567890123',  # 国家数据局
    'MP_WXS_5678901234'   # 工信微报
]

# 过滤关键词（标题包含以下任意词的跳过）
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
        # 过滤核聚变相关标题
        if any(kw in title for kw in EXCLUDE_KEYWORDS):
            continue
        url = f'https://mp.weixin.qq.com/s/{aid}'
        date_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d')
        articles.append({
            "title": title,
            "url": url,
            "source": mp_id,  # 可后续映射为公众号名称
            "date": date_str
        })

conn.close()

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f'导出 {len(articles)} 篇数字经济文章到 {OUT_FILE}')