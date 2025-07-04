# 🕊 Twitter Scraper with Selenium

This repository contains a Python script to scrape tweets from Twitter using **Selenium WebDriver**, with support for **manual login**, **multi-keyword search**, **date filtering**, and **sentiment analysis**.

---

## ✨ Features

- ✅ Manual login to Twitter (no API required)
- 🕵️ Scrape tweets based on keyword and date range
- 🗣 Extract:
  - `created_at` (date of tweet)
  - `full_text` (clean tweet content)
  - `username` (Twitter handle)
  - `language` (auto-detected)
  - `sentiment` (positive / neutral / negative using TextBlob)
  - `like`, `retweet`, `reply` counts
  - `image_url` (if available)
  - `tweet_url`, `id_str`
- 📀 Export results to CSV file

---

## ⚙️ Requirements

Install dependencies:

```bash
pip install selenium webdriver-manager pandas textblob langdetect
```

Make sure **Google Chrome** is installed on your system.

---

## 🚀 How to Use

1. Run the script:

   ```bash
   python scrapping_hotto.py
   ```

2. Input:

   - Start date (format: `YYYY-MM-DD`)
   - End date (format: `YYYY-MM-DD`)
   - Keywords (comma-separated)

3. A Chrome window will open. **Manually log in** to Twitter.

4. Press **ENTER** after you have successfully logged in.

5. The script will begin scraping tweets and save the result to a CSV file named:

   ```
   tweet_result_YYYY-MM-DD_to_YYYY-MM-DD.csv
   ```

---

## 📌 Notes

- This script avoids the Twitter API and is meant for educational or research purposes.
- Scraping large amounts of data may violate Twitter’s terms of service. Use responsibly.

---

## 🧑‍💻 Author

Created with ❤️ by salma aufadina

