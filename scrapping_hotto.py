from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
from langdetect import detect
from textblob import TextBlob
from datetime import datetime, timedelta
import time
import pandas as pd

# ========== Input Manual ==========
start_date = input("Tanggal mulai (YYYY-MM-DD): ")
end_date = input("Tanggal akhir (YYYY-MM-DD): ")
keywords_input = input("Kata kunci (pisahkan dengan koma): ")
keywords = [kw.strip() for kw in keywords_input.split(",")]

# ========== Setup Chrome ==========
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Aktifkan jika ingin tanpa tampilan browser
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ========== Login Manual ==========
print("🌐 Silakan login ke Twitter, lalu tekan ENTER jika sudah selesai login...")
driver.get("https://twitter.com/login")
input("✅ Tekan ENTER jika kamu sudah login: ")

# ========== Scraping ==========
all_data = []

for keyword in keywords:
    print(f"\n🔍 Scraping: {keyword}")
    query = f'"{keyword}" since:{start_date} until:{end_date}'
    search_url = f"https://twitter.com/search?q={quote(query)}&src=typed_query&f=live"

    driver.get(search_url)
    time.sleep(4)

    seen_urls = set()
    for _ in range(35):  # scroll 25x
        tweets = driver.find_elements(By.XPATH, '//article[@role="article"]')
        for tweet in tweets:
            try:
                tweet_url = tweet.find_element(By.XPATH, './/time/parent::a').get_attribute("href")
                if tweet_url in seen_urls:
                    continue
                seen_urls.add(tweet_url)

                time_posted = tweet.find_element(By.XPATH, './/time').get_attribute("datetime")
                created_at = datetime.fromisoformat(time_posted.replace("Z", "+00:00")) + timedelta(hours=7)

                id_str = tweet_url.split("/")[-1]

                # Full Text
                try:
                    full_text = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                except:
                    full_text = ''

                # Username
                try:
                    username = tweet.find_element(By.XPATH, './/div[@data-testid="User-Name"]//span[contains(text(), "@")]').text
                except:
                    username = ''

                # Bahasa
                try:
                    lang = detect(full_text)
                except:
                    lang = 'und'

                # Sentimen
                try:
                    polarity = TextBlob(full_text).sentiment.polarity
                    sentiment = 'Positif' if polarity > 0 else 'Negatif' if polarity < 0 else 'Netral'
                except:
                    sentiment = 'Tidak Terdeteksi'

                # Hitungan like/retweet/reply
                def get_count(testid):
                    try:
                        el = tweet.find_element(By.XPATH, f'.//div[@data-testid="{testid}"]')
                        count_text = el.text.strip()
                        if count_text == '':
                            return 0
                        if 'K' in count_text:
                            return int(float(count_text.replace('K', '')) * 1000)
                        if 'M' in count_text:
                            return int(float(count_text.replace('M', '')) * 1000000)
                        return int(count_text.replace(',', ''))
                    except:
                        return 0

                like = get_count("like")
                retweet = get_count("retweet")
                reply = get_count("reply")

                # Gambar
                try:
                    image_url = tweet.find_element(By.XPATH, './/img[contains(@src,"pbs.twimg.com/media")]').get_attribute("src")
                except:
                    image_url = ''

                # Simpan data
                all_data.append({
                    'keyword': keyword,
                    'id_str': id_str,
                    'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'full_text': full_text,
                    'sentiment': sentiment,
                    'favorite_count': like,
                    'retweet_count': retweet,
                    'reply_count': reply,
                    'quote_count': '',  # Tidak bisa diakses dari UI langsung
                    'image_url': image_url,
                    'tweet_url': tweet_url,
                    'username': username,
                    'lang': lang
                })
            except Exception as e:
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

driver.quit()

# ========== Simpan ke CSV ==========
df = pd.DataFrame(all_data)
filename = f'tweet_result_{start_date}_to_{end_date}.csv'
df.to_csv(filename, index=False, encoding='utf-8-sig')
print(f"\n✅ Scraping selesai! Data disimpan ke: {filename}")
