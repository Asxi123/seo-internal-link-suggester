import streamlit as st
import pandas as pd
from crawler.crawler import fetch_page
from engine.link_engine import generate_link_suggestions
from report import save_csv_report

st.set_page_config(page_title="Internal Link Suggestion Tool", layout="wide")

st.title("Internal Link Suggestion Tool")

st.write(
    "Enter a list of URLs from the same website. "
    "The tool will analyze the content and suggest internal links."
)

urls_input = st.text_area(
    "Paste URLs (one per line)",
    height=200
)

analyze_button = st.button("Analyze Pages")

if analyze_button:

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if len(urls) < 2:
        st.warning("Please enter at least two URLs.")
    else:

        st.write("Crawling pages...")

        pages = []

        progress = st.progress(0)

        for i, url in enumerate(urls):
            page_data = fetch_page(url)

            if page_data:
                pages.append(page_data)

            progress.progress((i + 1) / len(urls))

        st.write(f"Crawled {len(pages)} pages.")

        if len(pages) < 2:
            st.error("Not enough pages to analyze.")
        else:

            st.write("Analyzing content similarity...")

            df = generate_link_suggestions(
                pages,
                similarity_threshold=0.05,
                max_suggestions_per_page=5
            )

            if df.empty:
                st.warning("No suggestions found.")
            else:

                st.success(f"{len(df)} link suggestions generated.")

                st.dataframe(df)

                csv = df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="internal_link_suggestions.csv",
                    mime="text/csv",
                )
