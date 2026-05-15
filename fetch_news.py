import feedparser
import sqlite3
import time
from datetime import datetime, timedelta

DB_PATH = 'news.db'

# 配置你的RSS源（以下是示例，可换成真实的数字经济相关RSS）
RSS_FEEDS = [
    'http://www.caict.ac.cn/rss/',
    'https://www.cls.cn/rss',
    'https://www.thepaper.cn/rss_news',
]

def fetch_and_store():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                published = entry.get('published', entry.get('updated', ''))
                
                # 只存近7天的
                if published and published[:10] < one_week_ago:
                    continue
                
                cursor.execute('''
                    INSERT OR IGNORE INTO news_articles (title, source, url, publish_date, summary, category)
                    VALUES (?, ?, ?, ?, ?, '未分类')
                ''', (title, feed.feed.get('title', '未知来源'), url, published[:10], summary))
            
            print(f'✅ {feed.feed.get("title", feed_url)} 抓取完成')
        except Exception as e:
            print(f'❌ {feed_url} 抓取失败: {e}')
    
    conn.commit()
    conn.close()
    print('全部抓取完成！')

if __name__ == '__main__':
    fetch_and_store()