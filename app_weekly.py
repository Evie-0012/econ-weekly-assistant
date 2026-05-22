import streamlit as st
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI

# ==============================
#  InSight Weekly 配置
# ==============================
DATA_FILE = 'weekly_articles.json'
PASSWORD = "123456"
DEFAULT_API_KEY = "sk-81a96d19d6c94383b3ae4af2143e9336"         # 请替换为你的真实密钥

# ==============================
#  页面基础设置
# ==============================
st.set_page_config(
    page_title="InSight Weekly",
    page_icon="📰",
    layout="centered"
)

# ==============================
#  自定义 CSS：打造清爽呼吸感
# ==============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #f8f9fa;
    }

    /* 隐藏 Streamlit 默认页脚 */
    footer {visibility: hidden;}
    .stApp {margin-top: 0;}

    /* Logo 区域 */
    .logo-container {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .logo-text {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .logo-sub {
        font-size: 1rem;
        color: #6B7280;
        font-weight: 400;
        margin-top: 0.2rem;
        letter-spacing: 0.3px;
    }
    .divider-light {
        width: 60px;
        height: 3px;
        background: linear-gradient(to right, #4F46E5, #A78BFA);
        margin: 0.8rem auto 1rem auto;
        border-radius: 20px;
    }

    /* 主内容卡片 */
    .main-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.04);
        margin: 1.5rem 0;
    }

    /* 侧边栏控制面板 */
    .sidebar-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }

    /* 按钮样式 */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        font-weight: 600;
        padding: 0.7rem 1.2rem;
        transition: all 0.2s ease;
        border: none;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        font-size: 1.1rem;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(79, 70, 229, 0.3);
    }

    /* 周报内容排版优化 */
    .weekly-content h1, .weekly-content h2, .weekly-content h3 {
        color: #1F2937;
        font-weight: 600;
    }
    .weekly-content p {
        color: #374151;
        line-height: 1.7;
        font-size: 1rem;
    }
    .weekly-content blockquote {
        border-left: 4px solid #4F46E5;
        padding-left: 1rem;
        color: #6B7280;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
#  Logo 与 Slogan
# ==============================
st.markdown("""
<div class="logo-container">
    <div class="logo-text">InSight Weekly</div>
    <div class="logo-sub">From Information to Insight</div>
    <div class="divider-light"></div>
</div>
""", unsafe_allow_html=True)

# ==============================
#  侧边栏 - 控制面板
# ==============================
with st.sidebar:
    st.markdown("### 🔐 访问控制")
    password_input = st.text_input("请输入访问密码", type="password", placeholder="password")
    if password_input != PASSWORD:
        st.warning("密码错误，请重试。")
        st.stop()

    st.markdown("### ⚙️ 引擎配置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=DEFAULT_API_KEY,
        help="已预置默认 Key，你也可以输入自己的 Key"
    )
    days = st.slider("周刊时间范围（天）", 1, 30, 7)

    st.divider()
    st.caption("💡 点击下方按钮，立即生成本周周刊")

    # 生成按钮（放在侧边栏，视觉更集中）
    generate_btn = st.button("✨ 生成 InSight 周刊", use_container_width=True)

# ==============================
#  主界面 - 周刊生成与展示
# ==============================
if generate_btn:
    if not api_key:
        st.error("请先在侧边栏输入 DeepSeek API Key")
    else:
        # 读取数据
        with st.spinner("🧠 正在从数据中提炼洞察..."):
            if not os.path.exists(DATA_FILE):
                st.error("未找到 weekly_articles.json，请先上传最新数据。")
            else:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    articles = json.load(f)

        if not articles:
            st.warning("本周暂无新文章。")
        else:
            # 时间筛选
            since_date = datetime.now() - timedelta(days=days)
            filtered = [a for a in articles if a.get('date', '') >= since_date.strftime('%Y-%m-%d')]

            if not filtered:
                st.warning(f"最近 {days} 天内暂无文章。")
            else:
                st.info(f"📊 最近 {days} 天共采集到 {len(filtered)} 篇文章")

                # 构建文章列表
                article_list = "\n".join([
                    f"- [{a['date']}] {a['title']}（来源：{a['source']}）\n  链接：{a['url']}"
                    for a in filtered
                ])

                # 构建 Prompt
                prompt = f"""你是一位资深的《数字经济周刊》主编，请基于下方真实文章生成一期周刊。

格式要求：
1. 标题：数字经济周刊第X期 · {datetime.now().strftime('%Y.%m.%d')} - {(datetime.now()-timedelta(days=7)).strftime('%Y.%m.%d')}
2. 分为【数字经济政策】【数字经济热点】【数字经济学术】三个板块。
3. 每条新闻包含日期+标题，一段约500字专业摘要，末尾标注来源与链接。
4. 只使用下方提供的真实文章，不编造任何信息。若某板块无合适内容，写“本周暂无相关动态”。
5. 周刊末尾标注“责任编辑：课题组”及版权信息。

以下是本周采集的文章：
{article_list}

请生成周刊全文："""

                with st.spinner("📝 AI 正在撰写周刊..."):
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
                        st.error(f"生成失败，请检查 API Key 或网络：{e}")
                        st.stop()

                # 展示周刊
                st.markdown("## 📰 本期 InSight 周刊")
                with st.container():
                    st.markdown('<div class="weekly-content">' + weekly + '</div>', unsafe_allow_html=True)

                # 下载按钮
                st.download_button(
                    label="📥 下载 Markdown 周刊",
                    data=weekly,
                    file_name=f"InSight_Weekly_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )

# 页脚
st.divider()
st.caption("© InSight Weekly · 课题组内部工具 · 基于 DeepSeek 与 WeWe RSS 构建")