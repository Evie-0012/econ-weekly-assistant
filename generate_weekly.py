import json, os
from datetime import datetime, timedelta
from openai import OpenAI

DATA_FILE = 'weekly_articles.json'   # 改成从 JSON 读

def get_weekly_articles():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    return articles

# ... 后面生成周刊的函数保持不变

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
   prompt = f"""你是一个专业的《数字经济周刊》主编。请根据下面提供的真实文章，生成一期周刊。

要求：
1. 标题格式：数字经济周刊第XXX期·{datetime.now().strftime('%Y.%m.%d')}-{(datetime.now()-timedelta(days=7)).strftime('%Y.%m.%d')}
2. 分为【数字经济政策】、【数字经济热点】、【数字经济学术】三个板块。
3. 每条新闻包含：
   - 日期 + 新闻标题
   - 正文：写一段约500字的详细摘要，要求语言专业、信息完整，适合课题组成员快速把握要点。可以适当补充背景知识，但核心事实必须基于原文。
   - 在正文末尾另起一行，注明来源和原文链接，格式为：（来源：公众号名称，链接：URL）
4. 只使用下方提供的真实文章，不要编造任何新闻。如果某个板块没有合适的文章，写“本周暂无相关动态”。
5. 周刊末尾注明“责任编辑：课题组”及版权信息。

以下是本周采集的文章（每一条包括标题、日期、来源、链接）：
{article_list}

请生成周刊全文："""