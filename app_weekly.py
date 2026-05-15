import streamlit as st
from generate_weekly import get_weekly_articles, generate_weekly
from fetch_news import fetch_and_store
import os

st.set_page_config(page_title="数字经济周刊生成器", page_icon="📰", layout="centered")

st.markdown('<div style="text-align:center;font-size:2.5rem;font-weight:700;">📰 数字经济周刊生成器</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#666;margin-bottom:2rem;">基于真实新闻源，AI自动编排生成</div>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("⚙️ 操作面板")
    api_key = st.text_input("DeepSeek API Key", type="password")
    st.divider()
    if st.button("🔄 采集本周新闻", use_container_width=True):
        with st.spinner("正在从RSS源抓取新闻..."):
            fetch_and_store()
        st.success("采集完成！")

# 主体
if st.button("📝 生成本周数字经济周刊", type="primary", use_container_width=True):
    if not api_key:
        st.error("请先在侧边栏输入 API Key")
    else:
        with st.spinner("AI正在编排周刊，请稍候..."):
            articles = get_weekly_articles()
            st.info(f"本周共采集到 {len(articles)} 篇文章")
            weekly = generate_weekly(articles)
            st.markdown(weekly)
            
            # 下载按钮
            st.download_button(
                "📥 下载周刊（Markdown格式）",
                weekly,
                file_name=f"数字经济周刊_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.md"
            )