import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def format_news_email_body(news_summary_dict, current_date):
    formatted_news_content = []
    for title, details in news_summary_dict.items():
        link = details[0]
        summary_text = details[1]
        formatted_news_content.append(f"標題: {title}")
        formatted_news_content.append(f"摘要: {summary_text}")
        formatted_news_content.append(f"詳情: {link}")
        formatted_news_content.append("-" * 40)
    formatted_news_string = "\n".join(formatted_news_content)
    return f"""尊敬的收件人您好，\n\n這是來自您的雲端新聞摘要機器人，為您提供 {current_date} 的新聞重點。\n\n{formatted_news_string}\n\n祝您一天愉快！\n\n您的新聞摘要機器人\n"""

def send_email(subject, body, attach_file=False, attachment_path=None):
    sender = os.environ.get('GOOGLE_MAIL')
    password = os.environ.get('GOOGLE_MAIL_KEY')
    receiver = os.environ.get('RECEIVER_MAIL')
    if not all([sender, password, receiver]):
        raise ValueError('Missing one or more required email environment variables.')
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    if attach_file and attachment_path:
        if not os.path.exists(attachment_path):
            print(f"警告: 附件檔案 '{attachment_path}' 不存在。將不發送附件。")
        else:
            try:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
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
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"郵件已成功發送！")
    except smtplib.SMTPAuthenticationError as e:
        print(f"郵件發送失敗: 認證錯誤。請檢查你的發件人郵箱和應用程式密碼是否正確。\n錯誤訊息: {e}")
    except smtplib.SMTPException as e:
        print(f"郵件發送失敗: SMTP 錯誤。\n錯誤訊息: {e}")
    except Exception as e:
        print(f"郵件發送失敗: 未知錯誤。\n錯誤訊息: {e}") 