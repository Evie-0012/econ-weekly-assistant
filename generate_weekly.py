import sqlite3
from openai import OpenAI
from datetime import datetime, timedelta
import os

# 配置
DB_PATH = os.path.join('data', 'wewe-rss.db')  # WeWe RSS 数据库路径
API_KEY = '你的DeepSeek API Key'               # 替换为真实密钥，或改为从环境变量读取

def get_weekly_articles():
    """从 WeWe RSS 数据库获取最近 7 天的文章"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 计算 7 天前的时间戳（WeWe RSS 的 publish_time 是整数秒）
    one_week_ago = int((datetime.now() - timedelta(days=7)).timestamp())
    
    cursor.execute('''
        SELECT title, mp_id, id, publish_time 
        FROM articles 
        WHERE publish_time >= ? 
        ORDER BY publish_time DESC
    ''', (one_week_ago,))
    
    articles = []
    for title, mp_id, article_id, pub_time in cursor.fetchall():
        # 拼出微信公众号文章链接
        url = f'https://mp.weixin.qq.com/s/{article_id}'
        # 将时间戳转为日期字符串
        date_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d')
        # 公众号名称可以事先映射，这里先用 mp_id 代替，后续可优化
        source = mp_id
        articles.append((title, source, date_str, url))
    
    conn.close()
    return articles

def generate_weekly(articles, api_key=None):
    """调用大模型生成周刊"""
    if not api_key:
        # 如果没传 key，尝试从环境变量读取
        api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        if not api_key:
            return "未配置 DeepSeek API Key，请先在侧边栏输入。"
    
    if not articles:
        return "本周暂无新文章，请确保 WeWe RSS 已订阅相关公众号并正常抓取。"
    
    # 组装文章列表（简化版，只给标题、日期、来源、链接）
    article_list = "\n".join([
        f"- [{a[2]}] {a[0]}（来源：{a[1]}）\n  链接：{a[3]}"
        for a in articles
    ])
    
    # 构造提示词（复制你之前成功的周刊格式）
    prompt = f"""你是一个专业的数字经济周刊编辑。请根据以下本周真实采集的新闻文章，生成一期数字经济周刊。

格式要求：
1. 标题格式：数字经济周刊第XXX期·{datetime.now().strftime('%Y.%m.%d')}-{(datetime.now() - timedelta(days=7)).strftime('%Y.%m.%d')}
2. 分为【数字经济政策】、【数字经济热点】、【数字经济学术】三个板块
3. 每条新闻格式：日期 标题（来源），然后附一段简短摘要
4. 只使用下方提供的真实文章，不要编造任何新闻
5. 如果某个板块没有相关文章，写"本周暂无相关动态"
6. 周刊末尾注明责任编辑和版权信息

以下是本周采集的文章：
{article_list}

请生成周刊全文："""
    
    client = OpenAI(
        api_key=api_key,
        base_url='https://api.deepseek.com'
    )
    
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.3,
        max_tokens=8192
    )
    
    return response.choices[0].message.content

if __name__ == '__main__':
    articles = get_weekly_articles()
    weekly = generate_weekly(articles)
    
    filename = f'周刊_{datetime.now().strftime("%Y%m%d")}.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(weekly)
    
    print(f'周刊已生成：{filename}')
    print('\n' + weekly)
    print('\n' + weekly)
