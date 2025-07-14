import os
import datetime
from youtube_fetcher import channel, get_recent_videos_with_channel_names
from summarizer import use_url_get_summary
from email_sender import send_email, format_news_email_body
import pandas as pd

def process_unused_videos_and_update_status(df: pd.DataFrame):
    if 'Used' not in df.columns:
        print("錯誤：DataFrame 中沒有 'Used' 欄位。無法執行操作。")
        return df, {}
    unused_videos = df[df['Used'] == False]
    if unused_videos.empty:
        print("目前沒有任何 'Used' 欄位為 False 的影片需要處理。")
        return df, {}
    new_summary = {}
    for index, row in unused_videos.iterrows():
        video_link = row['Link']
        title = row['Title']
        try:
            summary = use_url_get_summary(video_link)
            df.loc[index, 'Used'] = True
            new_summary[title] = [video_link, summary]
        except Exception as e:
            print(f"處理影片 {title} 時發生錯誤: {e}")
            df.loc[index, 'Used'] = True
    return df, new_summary

def main():
    recent_videos_df = get_recent_videos_with_channel_names(channel)
    if recent_videos_df.empty:
        print("沒有找到任何的新影片，或在獲取過程中發生錯誤。")
        return
    recent_videos_df['Used'] = False
    updated_videos_df, new_summary = process_unused_videos_and_update_status(recent_videos_df)
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    email_subject = f"Python 機器人新聞摘要 - {current_date}"
    email_body = format_news_email_body(new_summary, current_date)
    send_email(subject=email_subject, body=email_body)

if __name__ == "__main__":
    main() 