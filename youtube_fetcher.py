import feedparser
import pandas as pd
from datetime import datetime, timedelta, timezone

# Channel list
channel_data = {
    "Channel": [
        "TODAY 看世界", "非凡新聞", "堆金積玉", "90後創業家掃地僧", "Emmy追劇時間", "Better Leaf 好葉", "啟點文化",
        "商業周刊", "cheap", "超級房仲學院", "小Lin说", "Wisdom Bread 智慧麵包", "Lester 萊斯特", "裝修小武郎",
        "PanSci 泛科學", "本子在隔壁 Benzi", "喵星律師-施宇宸", "曲博科技教室", "財訊", "范琪斐的美國時間",
        "蒼藍鴿的醫學天地", "TED"
    ],
    "Channel_id": [
        "UCmMnzrvnsSnv-0u9M1Rxiqw", "UCYIVkruUoN04UjV9pkBTswg", "UCeXxT_PoNOzS5dMOmmNk-6A", "UCWMxmoBhchU3swFAciqagnw",
        "UCUkwvRrpvWkocNdk9qIpRSw", "UChjHWpmNm-3HbLFkQ3TPXaA", "UCywBTF8MXwyQU21F1vHMnfw", "UCwlpC8vX_GkRngPYSnwkJxg",
        "UCGGrblndNzi86WY5lJkQJiA", "UCvj1qp0qh7VQY4Bz5VGdCVA", "UCilwQlk62k1z7aUEZPOB6yw", "UC-qwAKnBVzUlbNwol3UCZIA",
        "UCOI5JDEGupfDv5whYzlthPQ", "UCHDok5IzApSeLOJHHhqey8A", "UCuHHKbwC0TWjeqxbqdO-N_g", "UC-J5ksuTsGzqAbemiLRgcSw",
        "UCBkLBa86e5kscEGkZDyNxQQ", "UCq8Xi8muhehxRMIK76I1jog", "UCh2hilgoPIY-kiy1yFCc-xA", "UC2VKL-DkRvXtWkfjMzkYvmw",
        "UCUn77_F5A65HViL9OEvIpLw", "UCAuUUnT6oDeKwE6v1NGQxug"
    ]
}

channel = pd.DataFrame(channel_data)

def get_new_youtube_videos_last_week_as_dataframe(rss_url, information=False, day_back_track=1):
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            print("沒有找到影片或RSS Feed解析失敗。")
            return pd.DataFrame()
        videos_data = []
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=day_back_track)
        for entry in feed.entries:
            title = entry.get('title')
            link = entry.get('link')
            published_parsed = entry.get('published_parsed')
            if published_parsed:
                published_dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                if published_dt >= day_ago and published_dt <= now:
                    videos_data.append({
                        'Title': title,
                        'Link': link,
                        'Published_At': published_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
                    })
        df = pd.DataFrame(videos_data)
        return df
    except Exception as e:
        print(f"解析RSS Feed時發生錯誤: {e}")
        return pd.DataFrame()

def get_recent_videos_with_channel_names(channels_df, day_back_track=1):
    youtube_base_url = "https://www.youtube.com/feeds/videos.xml?channel_id="
    all_recent_videos = []
    if channels_df.empty:
        print("輸入的 channels_df 是空的，沒有頻道可以處理。")
        return pd.DataFrame()
    for index, row in channels_df.iterrows():
        channel_name = row['Channel']
        channel_url = youtube_base_url + row['Channel_id']
        recent_videos_for_channel = get_new_youtube_videos_last_week_as_dataframe(channel_url, day_back_track=day_back_track)
        if not recent_videos_for_channel.empty:
            recent_videos_for_channel['Channel_Name'] = channel_name
            all_recent_videos.append(recent_videos_for_channel)
    if all_recent_videos:
        final_df = pd.concat(all_recent_videos, ignore_index=True)
        return final_df
    else:
        return pd.DataFrame()

def append_unique_videos(new_df: pd.DataFrame, old_df: pd.DataFrame) -> pd.DataFrame:
    identifying_cols = ['Title', 'Link', 'Published_At', 'Channel_Name']
    if not all(col in new_df.columns for col in identifying_cols):
        print("錯誤：new_df 缺少必要的識別欄位。請確保它包含 'Title', 'Link', 'Published_At', 'Channel_Name'。")
        return old_df
    new_df['__temp_key__'] = new_df[identifying_cols].astype(str).agg(''.join, axis=1)
    old_df['__temp_key__'] = old_df[identifying_cols].astype(str).agg(''.join, axis=1)
    truly_new_entries_df = new_df[~new_df['__temp_key__'].isin(old_df['__temp_key__'])].copy()
    if 'Used' not in truly_new_entries_df.columns:
        truly_new_entries_df['Used'] = False
    final_cols_order = old_df.columns.tolist()
    cols_to_select = [col for col in final_cols_order if col in truly_new_entries_df.columns]
    truly_new_entries_df = truly_new_entries_df[cols_to_select]
    truly_new_entries_df.drop(columns=['__temp_key__'], inplace=True)
    old_df.drop(columns=['__temp_key__'], inplace=True)
    combined_df = pd.concat([old_df, truly_new_entries_df], ignore_index=True)
    return combined_df 