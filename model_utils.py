import pandas as pd
from datetime import timezone
from googleapiclient.discovery import build

def get_trending_videos(api_key, region="IN", max_results=50):
    youtube = build("youtube", "v3", developerKey=api_key)

    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region,
        maxResults=max_results
    )
    response = request.execute()

    records = []

    for item in response["items"]:
        records.append({
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "channel_title": item["snippet"]["channelTitle"],
            "publish_time": item["snippet"]["publishedAt"],
            "category_id": item["snippet"]["categoryId"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "tags": "|".join(item["snippet"].get("tags", []))
        })

    df = pd.DataFrame(records)

    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    df["trending_date"] = pd.Timestamp.now(tz=timezone.utc)

    df["video_age_days"] = (df["trending_date"] - df["publish_time"]).dt.days
    df["title_len"] = df["title"].astype(str).apply(len)
    df["title_word_count"] = df["title"].astype(str).apply(lambda x: len(x.split()))
    df["tag_count"] = df["tags"].apply(lambda x: len(x.split("|")) if x else 0)

    df["view_velocity"] = df["views"] / (df["video_age_days"] + 1)

    df["trending_score"] = (
        0.4 * df["views"].rank(pct=True)
        + 0.3 * df["view_velocity"].rank(pct=True)
        + 0.3 * df["tag_count"].rank(pct=True)
    )

    return df