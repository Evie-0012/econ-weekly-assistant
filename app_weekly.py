import streamlit as st
from generate_weekly import get_weekly_articles, generate_weekly
import os

# ===== 页面配置 =====
st.set_page_config(
    page_title="数字经济周刊生成器",
    page_icon="📰",
    layout="centered"
)

# ===== 标题 =====
st.markdown(
    '<div style="text-align:center;font-size:2.5rem;font-weight:700;">📰 数字经济周刊生成器</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div style="text-align:center;color:#666;margin-bottom:2rem;">基于真实新闻源，AI自动编排生成</div>',
    unsafe_allow_html=True
)

# ===== 侧边栏：配置 =====
with st.sidebar:
    st.header("⚙️ 操作面板")

    # 从 Streamlit Secrets 读取默认 Key（如果有），否则留空
    default_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=default_key,
        help="已预置默认 Key，也可输入你自己的 Key"
    )

    st.divider()
    st.caption("💡 提示：点击下方按钮采集本周新闻，然后生成周刊")

# ===== 主体区域 =====
if st.button("📝 生成本周数字经济周刊", type="primary", use_container_width=True):
    if not api_key:
        st.error("请先在侧边栏输入 DeepSeek API Key")
    else:
        with st.spinner("正在读取文章数据，生成周刊..."):
            articles = get_weekly_articles()
            if not articles:
                st.warning("本周暂无新文章，请先运行 fetch_news.py 或上传最新的 weekly_articles.json。")
            else:
                st.info(f"本周共采集到 {len(articles)} 篇文章")
                weekly = generate_weekly(articles, api_key=api_key)
                st.markdown(weekly)

                # 下载按钮
                st.download_button(
                    label="📥 下载周刊（Markdown 格式）",
                    data=weekly,
                    file_name=f"数字经济周刊_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.md"
                )

# ===== 底部 =====
st.divider()
st.caption("📰 数字经济周刊生成器 v1.0 | 数据来源：微信公众号 | 模型：DeepSeek")