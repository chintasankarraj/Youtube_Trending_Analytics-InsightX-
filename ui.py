import streamlit as st
import textwrap

def human(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))

def metric_card(icon, title, value, footer):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            <div class="card-footer">{footer}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    
def render_hero():
    st.markdown(
        textwrap.dedent("""
<div style="
    background:linear-gradient(135deg,#1e293b,#0f172a);
    border:1px solid rgba(255,255,255,.08);
    border-radius:22px;
    padding:34px;
    margin-bottom:28px;
    box-shadow:0 8px 30px rgba(0,0,0,.35);
">

<h1 style="
margin:0;
color:white;
font-size:46px;
font-weight:800;">
📺 YouTube InsightX
</h1>

<p style="
margin-top:12px;
margin-bottom:0;
color:#94a3b8;
font-size:18px;
line-height:1.7;">
Real-Time Analytics • AI Insights • Growth Prediction
</p>

</div>
"""),
        unsafe_allow_html=True,
    )
def video_card(video):
    st.image(
    f"https://img.youtube.com/vi/{video['video_id']}/mqdefault.jpg",
    width=320
    )
    title = video["title"]

    if len(title) > 70:
        title = title[:70] + "..."

    st.markdown(f"### 🎬 {title}")
    age = int(video["video_age_days"])

    age_text = f"{age} day ago" if age == 1 else f"{age} days ago"

    st.caption(
        f"📺 {video['channel_title']}  •  📅 {age_text}"
    )

    if video["view_velocity"] >= 2_000_000:
        st.success("🔥 Viral Growth")

    elif video["view_velocity"] >= 1_000_000:
        st.info("📈 Fast Growing")

    else:
        st.caption("🌱 Normal Growth")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div style="padding:12px;border-radius:12px;background:#111827;">
            <div style="font-size:14px;color:#9ca3af;">👁️ Views</div>
            <div style="font-size:24px;font-weight:700;color:#60a5fa;">
                {human(video["views"])}
            </div>
            <div style="font-size:12px;color:#6b7280;">
                {int(video["views"]):,} total views
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div style="padding:12px;border-radius:12px;background:#111827;">
            <div style="font-size:14px;color:#9ca3af;">⚡ Velocity</div>
            <div style="font-size:24px;font-weight:700;color:#f59e0b;">
                {human(video["view_velocity"])}/day
            </div>
            <div style="font-size:12px;color:#94a3b8;">
                {int(video["view_velocity"]):,} views/day
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)   

    st.link_button(
        "▶ Watch on YouTube",
        f"https://www.youtube.com/watch?v={video['video_id']}"
    )

    st.divider()    