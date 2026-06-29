import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
from model_utils import get_trending_videos
from ui import metric_card
from ui import render_hero
from ui import video_card
from ui import human
from datetime import datetime
# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="YouTube InsightX",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)
def load_css():
    with open("assets/css/style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ==================================================
# SECURE API KEY
# ==================================================
api_key = st.secrets.get("YOUTUBE_API_KEY")
if not api_key:
    st.error("API key not found. Configure Streamlit secrets.")
    st.stop()

# ==================================================
# CATEGORY MAP
# ==================================================
CATEGORY_MAP = {
    "1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music",
    "15": "Pets & Animals", "17": "Sports", "20": "Gaming",
    "22": "People & Blogs", "23": "Comedy", "24": "Entertainment",
    "25": "News & Politics", "26": "Howto & Style",
    "27": "Education", "28": "Science & Technology"
}


REGION_FLAGS = {
    "IN": "🇮🇳 India",
    "US": "🇺🇸 United States",
    "CA": "🇨🇦 Canada",
    "GB": "🇬🇧 United Kingdom",
    "JP": "🇯🇵 Japan",
    "DE": "🇩🇪 Germany",
    "FR": "🇫🇷 France"
}
# ==================================================
# HERO SECTION
# ==================================================

render_hero()

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.markdown("## ⚙️ Dashboard Controls")

region = st.sidebar.selectbox(
    "Region",
    ["IN", "US", "CA", "GB", "JP", "DE", "FR"]
)

max_videos = st.sidebar.slider(
    "Trending Videos",
    10, 50, 50, step=5
)

st.sidebar.markdown("---")
st.sidebar.success("🔐 Secure API Connected")

# ==================================================
# LOAD ML MODELS
# ==================================================
@st.cache_resource
def load_models():
    return (
        joblib.load("random_forest_model_api.pkl"),
        joblib.load("scaler_api.pkl")
    )

rf_model, scaler = load_models()

# ==================================================
# MAIN ACTION
# ==================================================
st.markdown("### 🚀 Start Analysis")

if not st.button(
    "Analyze Trending Videos",
    use_container_width=True,
    type="primary"
):
    st.stop()
with st.spinner("Collecting YouTube data..."):
    df = get_trending_videos(api_key, region, max_videos)
    
if df.empty:
    st.warning("No data returned.")
    st.stop()

last_updated = datetime.now().strftime("%d %b %Y • %I:%M:%S %p")

st.markdown(f"""
<div style="
    background:#111827;
    border:1px solid rgba(255,255,255,0.08);
    padding:12px 18px;
    border-radius:12px;
    color:#9ca3af;
    font-size:14px;
    margin-bottom:18px;
">
🌍 <b>{REGION_FLAGS[region]}</b>
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
🕒 <b>Last Updated:</b> {last_updated}
</div>
""", unsafe_allow_html=True)
 
# --------------------------------------------------
 # FEATURE ENGINEERING
# --------------------------------------------------
df["category_name"] = df["category_id"].astype(str).map(CATEGORY_MAP).fillna("Other")
df["youtube_url"] = "https://www.youtube.com/watch?v=" + df["video_id"]

# ==================================================
# KPI CARDS
# ==================================================
c1, c2, c3, c4 = st.columns(4)

cards = [
    ("📹", "Trending Videos", f"{len(df)}", "🟢 Live Data"),
    ("👁️", "Average Views", human(df["views"].mean()), "📈 Per Video"),
    ("🔥", "Highest Views", human(df["views"].max()), "🚀 Peak Reach"),
    ("⚡", "View Velocity", f"{human(df['view_velocity'].mean())}/day", "📊 Avg Growth"),
]

for col, (icon, title, value, footer) in zip([c1, c2, c3, c4], cards):
    with col:
       metric_card(icon, title, value, footer)    
# ==================================================
# TABS
# ==================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Videos",
    "📊 Analytics",
    "🚀 Growth",
    "🤖 Predictions",
    "🧠 AI Insights"
])
# ---------------- VIDEOS ----------------
with tab1:

    
    videos = (
        df.reset_index(drop=True)
    )
    st.subheader(f"🔥 Top {len(videos)} Trending Videos")
    for i in range(0, len(videos), 2):
        col1, col2 = st.columns(2)

        with col1:
            video_card(videos.iloc[i])

        if i + 1 < len(videos):
            with col2:
                video_card(videos.iloc[i + 1])
    # ---------------- ANALYTICS ----------------
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚀 View Velocity Distribution")

            fig = px.histogram(
                df,
                x="view_velocity",
                nbins=15,
                color_discrete_sequence=["#3b82f6"],
                template="plotly_dark"
            )

            fig.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#0f172a",
                font_color="white",
                height=420,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📈 Video Age vs Views")

            fig = px.scatter(
                df,
                x="video_age_days",
                y="views",
                size="views",
                color="view_velocity",
                hover_name="title",
                color_continuous_scale="Turbo",
                template="plotly_dark"
            )

            fig.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#0f172a",
                font_color="white",
                height=420,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Category Distribution")
        category_counts = (
            df["category_name"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = ["Category", "Count"]

        fig = px.pie(
            category_counts,
            values="Count",
            names="Category",
            hole=0.55,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font_color="white",
            height=450,
            legend_title="Categories"
        )

        st.plotly_chart(fig, use_container_width=True)
    # ---------------- GROWTH ----------------
    with tab3:
        gdf = df.sort_values("view_velocity", ascending=False).head(10).copy()
        st.subheader("🚀 Top 10 Fastest Growing Videos")

        gdf = (
            df.sort_values("view_velocity", ascending=False)
            .head(10)
            .sort_values("view_velocity")
        )

        gdf["short_title"] = gdf["title"].apply(
            lambda x: x[:45] + "..." if len(x) > 45 else x
        )

        fig = px.bar(
            gdf,
            x="view_velocity",
            y="short_title",
            orientation="h",
            color="view_velocity",
            color_continuous_scale="Turbo",
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font_color="white",
            height=600,
            yaxis_title="",
            xaxis_title="Views per Day",
        )
        gdf["title"] = gdf.apply(
            lambda x: f'<a class="video-link" href="{x["youtube_url"]}" target="_blank">{x["title"]}</a>',
            axis=1
        )
        gdf["views"] = gdf["views"].apply(lambda x: f"{int(x):,}")

        gdf["view_velocity"] = gdf["view_velocity"].apply(
            lambda x: f"{int(x):,} views/day"
        )
        st.write(
            gdf[["title", "channel_title", "views", "view_velocity"]]
                .to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- PREDICTIONS ----------------
    with tab4:
        X = df[["video_age_days", "title_len", "title_word_count", "tag_count"]]
        Xs = scaler.transform(X)
        probs = rf_model.predict_proba(Xs)[:, 1]

        pdf = df.copy()
        pdf["Prediction"] = np.where(probs >= 0.5, "🔥 High", "⬇ Low")
        high = (pdf["Prediction"] == "🔥 High").sum()
        low = (pdf["Prediction"] == "⬇ Low").sum()

        c1, c2 = st.columns(2)

        with c1:
            st.metric("🔥 High Growth Predicted", high)

        with c2:
            st.metric("⬇ Low Growth Predicted", low)
        pdf["Confidence"] = probs * 100
        def confidence_label(conf):
            if conf >= 90:
                return f"🟢 {conf:.1f}% (Very High)"
            elif conf >= 75:
                return f"🟢 {conf:.1f}% (High)"
            elif conf >= 50:
                return f"🟡 {conf:.1f}% (Medium)"
            elif conf >= 25:
                return f"🟠 {conf:.1f}% (Low)"
            else:
                return f"🔴 {conf:.1f}% (Very Low)"

        pdf["Confidence"] = pdf["Confidence"].apply(confidence_label)
        st.subheader("🤖 Prediction Confidence")

        fig = px.histogram(
            pdf,
            x="Confidence",
            color="Prediction",
            nbins=20,
            color_discrete_map={
                "🔥 High": "#22c55e",
                "⬇ Low": "#ef4444"
            },
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font_color="white",
            height=420,
        )

        st.plotly_chart(fig, use_container_width=True)

        pdf["title"] = pdf.apply(
            lambda x: f'<a class="video-link" href="{x["youtube_url"]}" target="_blank">{x["title"]}</a>',
            axis=1
        )
        st.write(
            pdf[["title", "Prediction", "Confidence"]]
            .to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
    # ---------------- PREDICTIONS ----------------
    with tab5:

        st.header("🧠 AI Report")

        top_video = df.loc[df["views"].idxmax()]
        fastest = df.loc[df["view_velocity"].idxmax()]
        popular_category = df["category_name"].mode()[0]

        high = (pdf["Prediction"] == "🔥 High").sum()
        low = (pdf["Prediction"] == "⬇ Low").sum()

        avg_views = int(df["views"].mean())
        avg_velocity = int(df["view_velocity"].mean())

        st.subheader("📊 Executive Summary")
        st.info(f"""
        ### Today's Trending Insights

        🔥 Highest Viewed Video:
        **{top_video['title']}**

        👀 Views:
        **{top_video['views']:,}**

        🚀 Fastest Growing Video:
        **{fastest['title']}**

        ⚡ View Velocity:
        **{fastest['view_velocity']:,.0f} views/day**

        🎯 Dominant Category:
        **{popular_category}**

        🤖 Machine Learning Prediction:
        **{high} High Growth**
        **{low} Low Growth**
        """)

        st.subheader("💡 AI Recommendations")

        recommendations = []

        if popular_category == "Music":
            recommendations.append("🎵 Music content currently dominates the trending list.")

        if avg_velocity > 500000:
            recommendations.append("🚀 Trending videos are gaining views extremely quickly.")

        if high > 0:
            recommendations.append("🔥 One or more videos have strong viral potential.")

        if df["video_age_days"].mean() < 4:
            recommendations.append("📅 New uploads dominate the trending page.")

        for rec in recommendations:
            st.success(rec)
        score = min(100, int(avg_velocity / 10000))

        st.subheader("⭐ Overall Trend Score")

        st.progress(score)
        
        st.metric("Trend Score", f"{score}/100")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Average Views", f"{avg_views:,}")

        with col2:
            st.metric("Average Velocity", f"{avg_velocity:,}")

        with col3:
            st.metric("Trending Category", popular_category)

        st.markdown("---")

        st.success("""
        ### 🤖 AI Conclusion

        • Trending videos are growing at a rapid pace.

        • Entertainment and Music dominate the current trends.

        • Videos published within the last few days receive the highest engagement.

        • The Random Forest model predicts only a small number of videos with exceptionally high growth potential.

        • Content creators should focus on timely uploads, engaging titles, and trending categories to maximize reach.
        """)    
st.markdown("---")

st.markdown("""
<div style="text-align:center; color:#9ca3af; padding:20px 0;">

<h3 style="margin-bottom:10px;">
📺 YouTube InsightX v1.0
</h3>

<p style="font-size:17px; margin-bottom:10px;">
Real-Time Analytics • AI Insights • Growth Prediction
</p>

<p style="font-size:15px;">
Built with ❤️ using Python • Streamlit • YouTube Data API • Scikit-learn • Plotly
</p>

<p style="font-size:14px; color:#6b7280;">
© 2026 Chintasankarraj
</p>

</div>
""", unsafe_allow_html=True)