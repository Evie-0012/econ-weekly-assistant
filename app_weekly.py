import streamlit as st
import sqlite3
from datetime import datetime, timedelta
from openai import OpenAI

# ===== 配置 =====
DB_PATH = r'D:\wewe-rss\data\wewe-rss.db'
TARGET_IDS = ['MP_WXS_3271041950', 'MP_WXS_3298479661', 'MP_WXS_3931590079']
MP_NAME_MAP = {
    'MP_WXS_3271041950': '数字经济与商业模式',
    'MP_WXS_3298479661': '新智元',
    'MP_WXS_3931590079': '国家数据局',
}

# ★ 你的固定 API Key，打开页面即自动填入
DEFAULT_API_KEY = "sk-81a96d19d6c94383b3ae4af2143e9336"

st.set_page_config(page_title="数字经济周刊生成器", page_icon="📰", layout="centered")
st.markdown('<div style="text-align:center;font-size:2.5rem;font-weight:700;">📰 数字经济周刊生成器</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#666;margin-bottom:2rem;">课题组内部使用 · 基于微信公众号真实数据</div>', unsafe_allow_html=True)

# 侧边栏
# 在侧边栏开头加上
with st.sidebar:
    password = st.text_input("访问密码", type="password")
    if password != "123456":
        st.stop()
with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=DEFAULT_API_KEY,          # 自动填好你的 Key
        help="已预置默认 Key，你也可以输入其他 Key"
    )
    days = st.slider("时间范围（天）", 1, 30, 7)
    st.divider()
    st.caption("💡 直接从本地数据库生成周刊")

# 主体
if st.button("📝 生成本周数字经济周刊", type="primary", use_container_width=True):
    if not api_key:
        st.error("请先在侧边栏输入 DeepSeek API Key")
    else:
        with st.spinner("正在读取本地数据库..."):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            since = int((datetime.now() - timedelta(days=days)).timestamp())

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

        if not articles:
            st.warning("本周暂无新文章，请先确保 WeWe RSS 已抓取目标公众号的内容。")
        else:
            st.info(f"本周共采集到 {len(articles)} 篇文章")

            # 构建提示词
            article_list = "\n".join([
                f"- [{a['date']}] {a['title']}（来源：{a['source']}）\n  链接：{a['url']}"
                for a in articles
            ])
            prompt = f"""你是一个专业的《数字经济周刊》主编。请根据下面提供的真实文章，生成一期周刊。

要求：
1. 标题格式：数字经济周刊第XXX期·{datetime.now().strftime('%Y.%m.%d')}-{(datetime.now()-timedelta(days=7)).strftime('%Y.%m.%d')}
2. 分为【数字经济政策】、【数字经济热点】、【数字经济学术】三个板块。
3. 每条新闻包含：日期 + 标题，约500字详细摘要，末尾注明来源和链接。
4. 只使用下方提供的真实文章，不要编造。如果某板块无合适文章，写"本周暂无相关动态"。
5. 周刊末尾注明"责任编辑：课题组"及版权信息。

以下是本周采集的文章：
{article_list}

请生成周刊全文："""

            with st.spinner("AI 正在生成周刊..."):
                client = OpenAI(api_key=api_key, base_url='https://api.deepseek.com')
                response = client.chat.completions.create(
                    model='deepseek-chat',
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=0.3,
                    max_tokens=16384
                )
                weekly = response.choices[0].message.content

            st.markdown(weekly)
            st.download_button("📥 下载周刊", weekly,
                               file_name=f"数字经济周刊_{datetime.now().strftime('%Y%m%d')}.md")

st.divider()
st.caption("📰 数字经济周刊生成器 v2.0 内部版 | 数据来源：微信公众号 | 模型：DeepSeek")