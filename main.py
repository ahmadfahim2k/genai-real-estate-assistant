import streamlit as st
from rag import process_urls, generate_answer
from scraper import scrape_cnbc_real_estate
from messages import (
    ERROR_NO_URLS,
    ERROR_SCRAPING_NO_ARTICLES,
    SCRAPING_CNBC,
    SCRAPED_ARTICLES_HEADER,
    EMBEDDED_ARTICLES_HEADER,
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
        padding-bottom: 0;
    }
    [data-testid="stSidebarUserContent"] {
        padding-bottom: 1rem;
    }
    [data-testid="stForm"] {
        border: none;
        padding: 0;
    }
    .block-container {
        padding-top: 2rem;
    }
    [data-testid="stSidebarContent"] {
        overflow: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Real Estate Research Tool")

scrape_button = st.sidebar.button("Scrape CNBC Real Estate", use_container_width=True)

st.sidebar.markdown(
    "<div style='text-align:center; color:gray; margin: 8px 0'>─── OR ───</div>"
    "<div style='text-align:center; font-size:0.8rem; color:gray; margin-bottom:8px'>enter custom URLs</div>",
    unsafe_allow_html=True,
)

url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")
url4 = st.sidebar.text_input("URL 4")
url5 = st.sidebar.text_input("URL 5")

process_url_button = st.sidebar.button("Process URLs", use_container_width=True)

placeholder = st.empty()

if "embedded_urls" not in st.session_state:
    st.session_state.embedded_urls = []
if "embedded_urls_header" not in st.session_state:
    st.session_state.embedded_urls_header = ""

if process_url_button:
    urls = [url for url in (url1, url2, url3, url4, url5) if url != '']
    if len(urls) == 0:
        placeholder.text(ERROR_NO_URLS)
    else:
        for status in process_urls(urls):
            placeholder.text(status)
        st.session_state.embedded_urls = urls
        st.session_state.embedded_urls_header = EMBEDDED_ARTICLES_HEADER

if scrape_button:
    try:
        with st.spinner(SCRAPING_CNBC):
            scraped_urls = scrape_cnbc_real_estate()
        if not scraped_urls:
            placeholder.text(ERROR_SCRAPING_NO_ARTICLES)
        else:
            for status in process_urls(scraped_urls):
                placeholder.text(status)
            st.session_state.embedded_urls = scraped_urls
            st.session_state.embedded_urls_header = SCRAPED_ARTICLES_HEADER
    except RuntimeError as e:
        placeholder.text(str(e))

with st.form("query_form"):
    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    with col1:
        query = st.text_input("Question", placeholder="Summarize the latest real estate trends...")
    with col2:
        ask_button = st.form_submit_button("Query")

if st.session_state.embedded_urls:
    st.subheader(st.session_state.embedded_urls_header)
    for url in st.session_state.embedded_urls:
        st.markdown(f"- {url}")

if ask_button and query:
    try:
        answer, sources = generate_answer(query)
        st.header("Answer: ")
        st.write(answer)

        if sources:
            st.subheader("Sources:")
            for source in sources:
                st.write(source)
    except RuntimeError as e:
        placeholder.text(str(e))
