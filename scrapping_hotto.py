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
import random

# ========== Input ==========
start_date = input("開始日期 (2025-07-01):")
end_date = input("結束日期 (YYYY-MM-DD):")
keywords_input = input("關鍵字 (用逗號分隔): bitcoin,BTC,blockchain")
keywords = [kw.strip() for kw in keywords_input.split(",")]

# ========== Setup Chrome ==========
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Aktifkan jika ingin tanpa tampilan browser
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ========== Manual Login ==========
print("🌐 請登入 Twitter，登入完成後按 ENTER...")
driver.get("https://twitter.com/login")
input("✅ 如果您已經登入，請按 ENTER 鍵： ")

# ========== Scraping ==========
all_data = []

for keyword in keywords:
    print(f"\n🔍 Scraping: {keyword}")
    query = f'{keyword} until:{end_date} since:{start_date}'
    search_url = f"https://twitter.com/search?q={quote(query)}&src=typed_query&f=live"

    driver.get(search_url)
    time.sleep(10)

    seen_urls = set()
    stable_scroll = 0
    last_seen = 0

    for i in range(100):  # jumlah scroll
        tweets = driver.find_elements(By.XPATH, '//article[@role="article"]')
        print(f"📄 Scroll {i+1} | Tweet terlihat: {len(tweets)} | Total unik: {len(seen_urls)}")

        if len(seen_urls) == last_seen:
            stable_scroll += 1
        else:
            stable_scroll = 0
            last_seen = len(seen_urls)

        if stable_scroll >= 4:
            print("⚠️ Tidak ada tweet baru ditemukan setelah beberapa scroll. Berhenti.")
            break

        for tweet in tweets:
            try:
                tweet_url = tweet.find_element(By.XPATH, './/time/parent::a').get_attribute("href")
                if tweet_url in seen_urls:
                    continue
                seen_urls.add(tweet_url)

                time_posted = tweet.find_element(By.XPATH, './/time').get_attribute("datetime")
                created_at = datetime.fromisoformat(time_posted.replace("Z", "+00:00")) + timedelta(hours=7)
                id_str = tweet_url.split("/")[-1]

                # Ambil hanya isi tweet, bukan semua text
                try:
                    full_text = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text.strip()
                except:
                    full_text = ''

                lines = tweet.text.splitlines()

                try:
                    username = tweet.find_element(By.XPATH, './/div[@data-testid="User-Name"]//span[contains(text(), "@")]').text
                except:
                    username = ''

                try:
                    lang = detect(full_text)
                except:
                    lang = 'und'

                try:
                    polarity = TextBlob(full_text).sentiment.polarity
                    sentiment = 'Positif' if polarity >= 0 else 'Negatif'
                except:
                    sentiment = 'Positif'  # default jika error

                def parse_number(text):
                    text = text.strip()
                    if 'K' in text:
                        return int(float(text.replace('K', '').replace(',', '.')) * 1000)
                    elif 'M' in text:
                        return int(float(text.replace('M', '').replace(',', '.')) * 1000000)
                    try:
                        return int(text.replace(',', ''))
                    except:
                        return 0

                reply = retweet = like = view = 0
                try:
                    numbers = lines[-4:]
                    numbers = [parse_number(n) for n in numbers if n.strip() and any(c.isdigit() for c in n)]
                    if len(numbers) == 4:
                        reply, retweet, like, view = numbers
                    elif len(numbers) == 3:
                        reply, retweet, like = numbers
                    elif len(numbers) == 2:
                        reply, retweet = numbers
                    elif len(numbers) == 1:
                        reply = numbers[0]
                except:
                    pass

                try:
                    image_url = tweet.find_element(By.XPATH, './/img[contains(@src,"pbs.twimg.com/media")]').get_attribute("src")
                except:
                    image_url = ''

                all_data.append({
                    'keyword': keyword,
                    'id_str': id_str,
                    'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'full_text': full_text,
                    'sentiment': sentiment,
                    'favorite_count': like,
                    'retweet_count': retweet,
                    'reply_count': reply,
                    'view_count': view,
                    'image_url': image_url,
                    'tweet_url': tweet_url,
                    'username': username,
                    'lang': lang
                })
            except Exception as e:
                print("❌ Error parsing tweet:", e)
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(5, 10))  # 用隨機時間代替固定等待

driver.quit()

# ========== Simpan ke CSV ==========
df = pd.DataFrame(all_data)
filename = f'tweet_result_{start_date}_to_{end_date}.csv'
df.to_csv(filename, index=False, encoding='utf-8-sig')
print(f"\n✅ Scraping selesai! Data disimpan ke: {filename}")
