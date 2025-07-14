# YouTube Translator & Daily Email Summary Bot

This project automatically fetches new videos from a list of YouTube channels, transcribes and summarizes their content using AI, and sends a daily email summary. It also syncs the workflow with a Kaggle notebook. All of this is automated using GitHub Actions.

## Features
- **Fetches new videos** from a configurable list of YouTube channels (including Shorts)
- **Downloads and transcribes audio** using [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [OpenAI Whisper](https://github.com/openai/whisper)
- **Summarizes content** using Gemini (Google Generative AI)
- **Sends a daily email** with the latest video summaries
- **Pushes updates to a Kaggle notebook**
- **Runs automatically every day at 7 PM (UTC+8)** via GitHub Actions

## How It Works
1. **GitHub Actions** runs the workflow daily (or on code push).
2. The workflow:
   - Fetches new YouTube videos from the channel list
   - Downloads and transcribes audio
   - Summarizes the transcript
   - Sends an email with the summaries
   - Updates a Kaggle notebook with the latest script
3. **Authentication** for YouTube (if needed) is handled via browser cookies (see below).

## Setup & Configuration

### 1. **Fork or Clone This Repo**

### 2. **Set Up GitHub Actions Secrets**
Go to your repo's **Settings > Secrets and variables > Actions** and add the following secrets:

| Name                | Description                                      |
|---------------------|--------------------------------------------------|
| `GOOGLE_API_KEY`    | Gemini API key                                   |
| `GOOGLE_MAIL`       | Gmail address (sender)                           |
| `GOOGLE_MAIL_KEY`   | Gmail app password                               |
| `RECEIVER_MAIL`     | Email address to receive the summary             |
| `KAGGLE_JSON`       | Contents of your `kaggle.json` API file          |
| `KAGGLE_NOTEBOOK_ID`| Your Kaggle notebook ID (e.g. `user/notebook`)   |
| `YOUTUBE_COOKIES`   | (Optional, but recommended) Your YouTube cookies |

#### **How to get YouTube cookies**
- Use a browser extension like [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/hnmpcagpplmpfojmgmnngilcnanddlhb) while logged in to YouTube.
- Save as `cookies.txt` and copy the contents into the `YOUTUBE_COOKIES` secret.

#### **How to get Kaggle API credentials**
- Go to your Kaggle account settings, click "Create New API Token", and copy the contents of the downloaded `kaggle.json` file into the `KAGGLE_JSON` secret.
- Your notebook ID is the part after `/` in your notebook URL (e.g., `username/notebook-slug`).

### 3. **Channel List**
- The list of channels is defined in `youtube_fetcher.py` and can be edited as needed.

### 4. **Workflow Schedule**
- The workflow runs daily at 7 PM (UTC+8) and on every push.
- You can change the schedule in `.github/workflows/kaggle-update.yml` by editing the `cron` line.

## Security Notes
- **Secrets are never printed or logged.**
- **Never share your cookies or API keys.**
- If you rotate your cookies or API keys, update the corresponding secret.
- Only trusted maintainers should have access to repo secrets.

## Local Development
- You can run the scripts locally by setting the required environment variables or using a `.env` loader.
- For local YouTube downloads requiring authentication, place your `cookies.txt` in the project root.

## License
MIT

---

**Automate your YouTube news and stay up to date, every day!**
