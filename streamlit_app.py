import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt

# Setup pytrends
pytrends = TrendReq(hl='fa', tz=330)  # Persian language, Iran timezone

st.title("📊 Iranian Protest Sentiment Tracker")
st.markdown("Track Google search trends related to Iranian dissent or anti-regime sentiment in real time.")

# User input
kw = st.text_input("📝 Enter a search phrase (Farsi or English)", value="مرگ بر خامنه‌ای")
timeframe = st.selectbox("Select time range", ["now 7-d", "now 1-d", "today 3-m", "today 12-m"])
geo = st.selectbox("Target country", ["IR", "US", "TR", "GB"], index=0)

# Trigger
import time

# Session rate limit setup
if "last_search_time" not in st.session_state:
    st.session_state.last_search_time = 0

cooldown = 30  # seconds between user queries
now = time.time()
time_since_last = now - st.session_state.last_search_time

if st.button("🔍 Track Now"):
    if time_since_last < cooldown:
        st.warning(f"⏱️ Please wait {int(cooldown - time_since_last)} seconds before trying again.")
        st.stop()

    # Update time only if allowed to proceed
    st.session_state.last_search_time = now

    try:
        # Call Google Trends
        pytrends.build_payload([kw], cat=0, timeframe=timeframe, geo=geo, gprop='')
        df = pytrends.interest_over_time()

        if df.empty:
            st.warning("No data found for this phrase. Try alternative spelling or phrasing.")
        else:
            st.success("Trend data fetched.")
            st.line_chart(df[[kw]])

            # Show peak
            peak = df[kw].idxmax()
            peak_val = df[kw].max()
            st.markdown(f"📈 **Highest spike:** {peak.strftime('%Y-%m-%d %H:%M')} — Value: {peak_val}")

            if st.checkbox("📄 Show raw trend data"):
                st.dataframe(df)
                trend_url = f"https://trends.google.com/trends/explore?q={kw}&geo={geo}"
                st.markdown(f"🔗 Source: [View on Google Trends]({trend_url})")

    except Exception as e:
        st.error("⚠️ Google blocked too many requests temporarily (Error 429). Try again later.")
        fallback_url = f"https://trends.google.com/trends/explore?q={kw}&geo={geo}"
        st.markdown(f"🔗 You can view the trend manually: [Google Trends →]({fallback_url})")
        st.stop()
