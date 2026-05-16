import streamlit as st
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI

# ===== 配置 =====
DATA_FILE = 'weekly_articles.json'
PASSWORD = "123456"                # 访问密码，可自行修改
DEFAULT_API_KEY = "sk-你的真实密钥"  # 改为你自己的 DeepSeek API Key

st.set_page_config(page_title="数字经济周刊生成器", page_icon="📰", layout="centered")
st.markdown('<div style="text-align:center;font-size:2.5rem;font-weight:700;">📰 数字经济周刊生成器</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#666;margin-bottom:2rem;">课题组内部使用 · 基于微信公众号真实数据</div>', unsafe_allow_html=True)

# 侧边栏：密码 + 配置
with st.sidebar:
    st.header("🔐 验证访问")
    password_input = st.text_input("请输入访问密码", type="password")
    if password_input != PASSWORD:
        st.warning("密码错误，请重试。")
        st.stop()

    st.header("⚙️ 配置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=DEFAULT_API_KEY,
        help="已预置默认 Key，你也可以输入其他 Key"
    )
    days = st.slider("时间范围（天）", 1, 30, 7)  # ← 滑块回来了
    st.divider()
    st.caption("💡 直接从本地数据库生成周刊")

# 主体
if st.button("📝 生成本周数字经济周刊", type="primary", use_container_width=True):
    if not api_key:
        st.error("请先在侧边栏输入 DeepSeek API Key")
    else:
        with st.spinner("正在读取文章数据..."):
            if not os.path.exists(DATA_FILE):
                st.error("未找到 weekly_articles.json，请先上传最新数据。")
            else:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    articles = json.load(f)

        if not articles:
            st.warning("本周暂无新文章。")
        else:
            # 根据滑块筛选时间
            since_date = datetime.now() - timedelta(days=days)
            filtered_articles = [
                a for a in articles
                if a.get('date', '') >= since_date.strftime('%Y-%m-%d')
            ]

            if not filtered_articles:
                st.warning(f"最近 {days} 天内暂无文章。")
            else:
                st.info(f"最近 {days} 天共采集到 {len(filtered_articles)} 篇文章")

                article_list = "\n".join([
                    f"- [{a['date']}] {a['title']}（来源：{a['source']}）\n  链接：{a['url']}"
                    for a in filtered_articles
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
                    try:
                        client = OpenAI(api_key=api_key, base_url='https://api.deepseek.com')
                        response = client.chat.completions.create(
                            model='deepseek-chat',
                            messages=[{'role': 'user', 'content': prompt}],
                            temperature=0.3,
                            max_tokens=16384
                        )
                        weekly = response.choices[0].message.content
                    except Exception as e:
                        st.error(f"生成失败，请检查 API Key 是否正确：{e}")
                        st.stop()

                st.markdown(weekly)
                st.download_button("📥 下载周刊", weekly,
                                   file_name=f"数字经济周刊_{datetime.now().strftime('%Y%m%d')}.md")

st.divider()
st.caption("📰 数字经济周刊生成器 v2.0 云端版 | 数据来源：微信公众号 | 模型：DeepSeek")