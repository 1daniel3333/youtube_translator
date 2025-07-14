import subprocess
import os
import whisper
import google.generativeai as genai
import feedparser
from datetime import datetime, timedelta, timezone
import pandas as pd # 導入 pandas 函式庫
from google.colab import userdata

data = {
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

channel = pd.DataFrame(data)

def get_new_youtube_videos_last_week_as_dataframe(rss_url, information=False, day_back_track=1):
    try:
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            print("沒有找到影片或RSS Feed解析失敗。")
            return pd.DataFrame() # 返回空的 DataFrame

        videos_data = [] # 用來儲存影片資訊的列表

        # 取得當前時間並計算一週前的時間
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=day_back_track)

        print(f"正在從 {rss_url} 檢查近{day_back_track}天的新影片 (從 {day_ago.strftime('%Y-%m-%d %H:%M:%S %Z')} 到 {now.strftime('%Y-%m-%d %H:%M:%S %Z')})...")

        for entry in feed.entries:
            title = entry.get('title')
            link = entry.get('link')
            published_parsed = entry.get('published_parsed') # 影片發布時間，解析為struct_time

            if published_parsed:
                # 將 struct_time 轉換為 datetime 物件，並設定為UTC時區
                published_dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)

                # 檢查影片發布時間是否在一週內
                if published_dt >= day_ago and published_dt <= now:
                    # if information:
                    #     print(f"  發現新影片（近一週內）：")
                    #     print(f"    標題: {title}")
                    #     print(f"    連結: {link}")
                    #     print(f"    發布時間: {published_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    #     print("-" * 30)

                    # 將影片資訊加入到列表中
                    videos_data.append({
                        'Title': title,
                        'Link': link,
                        'Published_At': published_dt.strftime('%Y-%m-%d %H:%M:%S %Z') # 以字串格式儲存時間
                        # 如果需要，也可以儲存原始的 datetime 物件: 'Published_Datetime_Object': published_dt
                    })
            else:
                print(f"警告：影片 '{title}' 缺少發布時間資訊，無法判斷是否為近一週影片。")

        if not videos_data:
            print("近一週內沒有找到新影片。")

        # 將列表轉換為 Pandas DataFrame
        df = pd.DataFrame(videos_data)
        return df

    except Exception as e:
        print(f"解析RSS Feed時發生錯誤: {e}")
        return pd.DataFrame() # 出錯時返回空的 DataFrame

# --- 主要函式：處理多個頻道並加入頻道名稱 ---
def get_recent_videos_with_channel_names(channels_df, day_back_track=1):
    """
    接收一個包含 'Channel' 和 'Channel_id' 的 DataFrame，
    抓取每個頻道近一週的新影片，並將頻道名稱加入結果 DataFrame 中。

    Args:
        channels_df (pd.DataFrame): 包含以下兩列的 DataFrame：
                                    - 'Channel': 頻道名稱 (str)
                                    - 'Channel_id': 頻道 RSS Feed 網址 (str)

    Returns:
        pd.DataFrame: 包含所有頻道近一週新影片的 DataFrame，
                      額外包含 'Channel_Name' 欄位。
    """
    youtube_base_url = "https://www.youtube.com/feeds/videos.xml?channel_id="
    all_recent_videos = [] # 用來儲存所有頻道的新影片資料

    if channels_df.empty:
        print("輸入的 channels_df 是空的，沒有頻道可以處理。")
        return pd.DataFrame()

    for index, row in channels_df.iterrows():
        channel_name = row['Channel']
        channel_url = youtube_base_url + row['Channel_id']

        print(f"--- 正在處理頻道： {channel_name} ({channel_url}) ---")

        # 呼叫之前的函式來抓取單一頻道的新影片
        recent_videos_for_channel = get_new_youtube_videos_last_week_as_dataframe(channel_url, day_back_track=day_back_track)

        if not recent_videos_for_channel.empty:
            # 將頻道名稱這一列添加到當前頻道的影片 DataFrame 中
            recent_videos_for_channel['Channel_Name'] = channel_name

            # 將這個頻道的影片資料添加到總列表
            all_recent_videos.append(recent_videos_for_channel)
            print(f"  頻道 {channel_name} 找到 {len(recent_videos_for_channel)} 部近{day_back_track}天新影片。")
        else:
            print(f"  頻道 {channel_name} 近{day_back_track}天沒有新影片。")
        print("-" * 50) # 分隔線

    if all_recent_videos:
        # 將所有頻道的 DataFrame 合併成一個大的 DataFrame
        final_df = pd.concat(all_recent_videos, ignore_index=True)
        return final_df
    else:
        print("所有頻道在近一週內都沒有找到新影片。")
        return pd.DataFrame() # 如果沒有任何影片，則返回一個空的 DataFrame


def append_unique_videos(new_df: pd.DataFrame, old_df: pd.DataFrame) -> pd.DataFrame:
    """
    將新的影片資料 (new_df) 中不重複的條目追加到現有影片資料 (old_df) 中。

    重複的判斷依據為 'Title', 'Link', 'Published_At', 'Channel_Name'。
    新追加的影片條目會自動獲得 'Used' 欄位並預設為 False。

    Args:
        new_df (pd.DataFrame): 包含新影片資訊的 DataFrame，應包含 'Title', 'Link', 'Published_At', 'Channel_Name'。
        old_df (pd.DataFrame): 包含舊影片資訊的 DataFrame，應包含 'Title', 'Link', 'Published_At', 'Channel_Name', 'Used'。

    Returns:
        pd.DataFrame: 合併後且已去重（包含所有不重複影片）的 DataFrame。
    """

    # 定義用於判斷重複的關鍵欄位
    identifying_cols = ['Title', 'Link', 'Published_At', 'Channel_Name']

    # 檢查 new_df 是否包含所有必要的識別欄位
    if not all(col in new_df.columns for col in identifying_cols):
        print("錯誤：new_df 缺少必要的識別欄位。請確保它包含 'Title', 'Link', 'Published_At', 'Channel_Name'。")
        return old_df # 如果 new_df 格式不正確，則返回原來的 old_df

    # 為了方便判斷重複，為兩個 DataFrame 建立一個臨時的唯一鍵
    # 將所有識別欄位的值連接成一個字串作為鍵
    new_df['__temp_key__'] = new_df[identifying_cols].astype(str).agg(''.join, axis=1)
    old_df['__temp_key__'] = old_df[identifying_cols].astype(str).agg(''.join, axis=1)

    # 找出 new_df 中那些 '__temp_key__' 不存在於 old_df 的行
    # 這些就是我們想要追加的「真正新」的影片資料
    truly_new_entries_df = new_df[~new_df['__temp_key__'].isin(old_df['__temp_key__'])].copy()

    # 為這些真正新的影片條目添加 'Used' 欄位，並預設為 False
    # 因為它們是新的，尚未被使用
    if 'Used' not in truly_new_entries_df.columns:
        truly_new_entries_df['Used'] = False

    # 確保 truly_new_entries_df 只包含 old_df 中已有的欄位，並且順序一致
    # 這樣在合併時可以避免額外的 NaN 或欄位順序問題
    final_cols_order = old_df.columns.tolist()

    # 選擇 truly_new_entries_df 中 old_df 所擁有的欄位，並確保它們按 old_df 的順序排列
    # 移除臨時鍵之前處理好欄位
    cols_to_select = [col for col in final_cols_order if col in truly_new_entries_df.columns]
    truly_new_entries_df = truly_new_entries_df[cols_to_select]

    # 移除臨時的 '__temp_key__' 欄位
    truly_new_entries_df.drop(columns=['__temp_key__'], inplace=True)
    old_df.drop(columns=['__temp_key__'], inplace=True)

    # 使用 concat 將現有資料 (old_df) 和真正的新資料 (truly_new_entries_df) 合併
    # ignore_index=True 會重置索引，確保結果 DataFrame 的索引是連續的
    combined_df = pd.concat([old_df, truly_new_entries_df], ignore_index=True)

    print(f"已從 {len(new_df)} 筆新資料中找到 {len(truly_new_entries_df)} 筆唯一新影片。")
    print(f"最終 DataFrame 包含 {len(combined_df)} 筆記錄。")

    return combined_df

# channel = pd.read_csv('Suscribe.csv')
recent_videos_df = get_recent_videos_with_channel_names(channel)

if not recent_videos_df.empty:
    print(f"\n成功取得 {len(recent_videos_df)} 部的新影片")

else:
    print("\n沒有找到任何的新影片，或在獲取過程中發生錯誤。")
# old = pd.read_csv('Channel_list.csv')
# saving = append_unique_videos(recent_videos_df, old)
# 儲存結果到 CSV 檔案
# saving.to_csv('Channel_list.csv', index=False, encoding='utf-8-sig')

def use_url_check_transcript(youtube_url):
  print("用 Whisper 分析音訊...")
  subprocess.run(f'yt-dlp -f bestaudio --extract-audio --audio-format mp3 -o "audio.%(ext)s" "{youtube_url}"', shell=True)
  audio_file = None
  for file in os.listdir():
      if file.endswith(".mp3"):
          audio_file = file
          break
  model = whisper.load_model("small")  # 可改 tiny / base / medium
  result = model.transcribe(audio_file)
  transcript = result["text"]

  # 刪除音訊檔案
  if audio_file and os.path.exists(audio_file):
      os.remove(audio_file)
  return transcript

def use_transcript_get_summary(transcript):
  import google.generativeai as genai

  # 設定 Gemini API 金鑰
  genai.configure(api_key=userdata.get('GOOGLE_API_KEY'))

  model = genai.GenerativeModel("gemini-1.5-flash")

  response = model.generate_content(f"""
  請幫我將以下影片逐字稿進行摘要，條列式列出重點。內容如下：
  {transcript}
  """)

  # print("\n📌 Gemini 摘要結果：")
  # print(response.text)
  return response.text

def use_url_get_summary(url):
  transcript = use_url_check_transcript(url)
  summary = use_transcript_get_summary(transcript)
  return summary

def processing_link(link: str) -> bool:
    """
    這個是一個範例函式，用於模擬處理影片連結。
    您需要將此函式替換為您實際的影片連結處理邏輯。

    Args:
        link (str): 影片的連結。

    Returns:
        bool: 如果連結處理成功返回 True，否則返回 False。
              這個返回值會影響 'Used' 欄位是否被更新。
    """
    print(f"正在處理連結: {link}")
    summary = use_url_get_summary(link)
    return True, summary

def process_unused_videos_and_update_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    找出 DataFrame 中 'Used' 欄位為 False 的影片，
    對其連結執行 processing_link 函式，然後將 'Used' 狀態更新為 True。

    Args:
        df (pd.DataFrame): 包含影片資訊的 DataFrame，應包含 'Title', 'Link', 'Published_At', 'Channel_Name', 'Used'。

    Returns:
        pd.DataFrame: 更新 'Used' 狀態後的 DataFrame。
    """

    if 'Used' not in df.columns:
        print("錯誤：DataFrame 中沒有 'Used' 欄位。無法執行操作。")
        return df

    # 篩選出所有 'Used' 欄位為 False 的影片
    unused_videos = df[df['Used'] == False]

    if unused_videos.empty:
        print("目前沒有任何 'Used' 欄位為 False 的影片需要處理。")
        return df # 如果沒有未使用的影片，直接返回原始 DataFrame
    new_summary = {}
    print(f"找到 {len(unused_videos)} 筆 'Used' 欄位為 False 的影片，準備處理。")

    # 遍歷這些未使用的影片，並對其連結進行處理
    # 使用 .loc 進行基於標籤的選擇和更新，以避免 SettingWithCopyWarning
    for index, row in unused_videos.iterrows():
        video_link = row['Link']
        title = row['Title']

        try:
          # 呼叫您的 processing_link 函式來處理連結
          process_successful, summary = processing_link(video_link)
          print(title)
          print(video_link)
          print(summary)
          print('-'*30)

          # 如果處理成功，則將該筆影片的 'Used' 狀態更新為 True
          if process_successful:
              df.loc[index, 'Used'] = True
              print(f"影片 '{row['Title']}' 的 'Used' 狀態已更新為 True。")
              new_summary[title] = [video_link, summary]
          else:
              print(f"影片 '{row['Title']}' 處理失敗，'Used' 狀態保持 False。")
        except:
          # 遇到問題 強制該row轉為True
          df.loc[index, 'Used'] = True
          print(f"影片 '{row['Title']}' 的 'Used' 狀態已更新為 True。")
          continue
        finally:
          print("-" * 30)

    print("所有未使用的影片處理完成。")
    return df, new_summary

print(f'近期有{len(recent_videos_df)}個更新')
recent_videos_df.head()

recent_videos_df['Used'] = False
updated_videos_df, new_summary = process_unused_videos_and_update_status(recent_videos_df)

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import datetime # 導入 datetime 模組來獲取當前日期

# --- 配置區 --- 請修改以下資訊 ---

# 你的發件人 Gmail 郵箱地址
# 範例: "your_robot_email@gmail.com"
# 請確保這個 Gmail 帳戶已開啟「兩步驟驗證」，並且你為此帳戶生成了「應用程式密碼」。
SENDER_EMAIL = userdata.get('GOOGLE_MAIL')

# 你從 Google 帳戶安全性設定中獲得的 16 位「應用程式密碼」。
# 這是 Gmail 專門為第三方應用程式提供的密碼，不是你 Gmail 的主密碼。
# 範例: "abcd efgh ijkl mnop" (注意，複製時通常沒有空格)
SENDER_PASSWORD = userdata.get('GOOGLE_MAIL_KEY')

# 收件人郵箱地址 (可以是你的主要郵箱，例如你的 Outlook 郵箱)
# 範例: "my_main_email@outlook.com"
RECEIVER_EMAIL = userdata.get('RECEIVER_Mail')

# 郵件主題
# 使用 datetime 模組自動獲取當前日期，讓郵件主題更動態。
current_date = datetime.date.today().strftime("%Y-%m-%d")
EMAIL_SUBJECT = f"Python 機器人新聞摘要 - {current_date}"

# 是否包含附件 (True/False)
ATTACH_FILE = False
# 如果要包含附件，請指定附件的路徑和檔案名稱
# 範例: "D:/MyDocuments/news_report.pdf" 或 "summary_20250609.txt"
# 請確保這個檔案確實存在於指定路徑。
ATTACHMENT_PATH = "你的附件檔案路徑.txt"

# --- SMTP 伺服器配置 (這是 Gmail 的設定，請勿修改) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # Gmail 的 TLS 端口

# 郵件正文內容 (目前設定為純文字。如果你想發送 HTML 郵件，需要調整 MIMEText 的第二個參數為 "html")
# --- 格式化新聞摘要內容 ---
# 這個部分將 new_summary 字典轉換成多行字串
formatted_news_content = []
for title, details in new_summary.items():
    link = details[0]
    summary_text = details[1]
    formatted_news_content.append(f"標題: {title}")
    formatted_news_content.append(f"摘要: {summary_text}")
    formatted_news_content.append(f"詳情: {link}")
    formatted_news_content.append("-" * 40) # 分隔線
# 使用 '\n'.join() 將所有格式化後的行連接成一個單一字串
formatted_news_string = "\n".join(formatted_news_content)

# 你可以把新聞摘要放在這裡。
EMAIL_BODY = f"""尊敬的收件人您好，

這是來自您的雲端新聞摘要機器人，為您提供 {current_date} 的新聞重點。

{formatted_news_string}

祝您一天愉快！

您的新聞摘要機器人
"""

# --- 寄信函數 ---
def send_email(sender, password, receiver, subject, body, attach_file=False, attachment_path=None):
    """
    發送電子郵件的函數。
    支持純文字和附件。
    """
    # 創建一個多部分郵件，這樣可以包含文本和附件
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    # 添加郵件正文
    msg.attach(MIMEText(body, "plain", "utf-8")) # 如果是 HTML 內容，改為 "html"

    # 添加附件
    if attach_file and attachment_path:
        if not os.path.exists(attachment_path):
            print(f"警告: 附件檔案 '{attachment_path}' 不存在。將不發送附件。")
        else:
            try:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part) # 進行 Base64 編碼

                    # 設定附件的檔名
                    filename = os.path.basename(attachment_path)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )
                    msg.attach(part)
                print(f"附件 '{filename}' 已成功添加到郵件。")
            except Exception as e:
                print(f"添加附件失敗: {e}")

    try:
        # 創建一個安全的 SSL 上下文
        context = ssl.create_default_context()

        # 連接到 SMTP 伺服器並發送郵件
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)  # 啟動 TLS 加密
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"郵件已成功發送！")
    except smtplib.SMTPAuthenticationError as e:
        print(f"郵件發送失敗: 認證錯誤。請檢查你的發件人郵箱和應用程式密碼是否正確。\n錯誤訊息: {e}")
    except smtplib.SMTPException as e:
        print(f"郵件發送失敗: SMTP 錯誤。\n錯誤訊息: {e}")
    except Exception as e:
        print(f"郵件發送失敗: 未知錯誤。\n錯誤訊息: {e}")

send_email(
    sender=SENDER_EMAIL,
    password=SENDER_PASSWORD,
    receiver=RECEIVER_EMAIL,
    subject=EMAIL_SUBJECT,
    body=EMAIL_BODY,
    attach_file=ATTACH_FILE,
    attachment_path=ATTACHMENT_PATH
)