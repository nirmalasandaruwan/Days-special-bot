import requests
from google import genai
from datetime import datetime, timezone, timedelta
import time
import os
import urllib.parse 
import random 
import textwrap 
import re 
import urllib.request
from PIL import Image, ImageDraw, ImageFont 

# --- API Keys ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "YOUR_FB_PAGE_ID_HERE")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "YOUR_FB_ACCESS_TOKEN_HERE")
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "")

client = genai.Client(api_key=GEMINI_API_KEY)

# --- Sri Lanka Timezone Fix (UTC +5:30) ---
sl_tz = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(sl_tz)

month = today.strftime("%m")
day = today.strftime("%d")
month_name = today.strftime("%B")

print(f"ශ්‍රී ලංකා වේලාවෙන් අද දිනය: {month_name} {day}")

HISTORY_FILE = "posted_history.txt"
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("")

def is_already_posted(event_text):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return event_text in f.read()

def save_to_history(event_text):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(event_text + "\n")

def get_cloud_font(size):
    windows_font = "C:\\Windows\\Fonts\\impact.ttf"
    if os.path.exists(windows_font):
        try: return ImageFont.truetype(windows_font, size)
        except: pass

    ubuntu_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if os.path.exists(ubuntu_font):
        try: return ImageFont.truetype(ubuntu_font, size)
        except: pass

    font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/oswald/Oswald-Bold.ttf"
    font_filename = "Oswald-Bold.ttf"
    if not os.path.exists(font_filename):
        try:
            print("ෆොන්ට් එක ඩවුන්ලෝඩ් කරමින් පවතී...")
            urllib.request.urlretrieve(font_url, font_filename)
        except Exception as e:
            return ImageFont.load_default()
    try:
        return ImageFont.truetype(font_filename, size)
    except:
        return ImageFont.load_default()

def add_text_to_image(image_path, title_text, date_text):
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        font_size = 95
        font_title = get_cloud_font(font_size)
        wrapped_title = textwrap.fill(title_text, width=16)
        
        bbox_title = draw.multiline_textbbox((0, 0), wrapped_title, font=font_title, align="center")
        title_w = bbox_title[2] - bbox_title[0]
        
        while title_w > (width - 60) and font_size > 30:
            font_size -= 2
            font_title = get_cloud_font(font_size)
            bbox_title = draw.multiline_textbbox((0, 0), wrapped_title, font=font_title, align="center")
            title_w = bbox_title[2] - bbox_title[0]

        title_h = bbox_title[3] - bbox_title[1]
        
        title_x = (width - title_w) / 2
        title_y = height - title_h - 180 

        font_date = get_cloud_font(45)
        bbox_date = draw.textbbox((0, 0), date_text, font_date)
        date_w = bbox_date[2] - bbox_date[0]
        date_x = (width - date_w) / 2
        date_y = title_y + title_h + 30

        outline_color = "black"
        text_color = "white"
        thickness = 4
        
        for adj_x in range(-thickness, thickness+1):
            for adj_y in range(-thickness, thickness+1):
                draw.multiline_text((title_x+adj_x, title_y+adj_y), wrapped_title, font=font_title, fill=outline_color, align="center")
                draw.text((date_x+adj_x, date_y+adj_y), date_text, font=font_date, fill=outline_color)

        draw.multiline_text((title_x, title_y), wrapped_title, font=font_title, fill=text_color, align="center")
        draw.text((date_x, date_y), date_text, font=font_date, fill=text_color)

        final_path = f"final_{image_path}"
        img.save(final_path)
        return final_path
    except:
        return image_path

# --- පොදු පෝස්ට් කිරීමේ ශ්‍රිතය (Wikipedia සහ DayOfTheYear දෙකටම වැඩ) ---
def create_and_publish_post(topic_text, display_date, article_link=""):
    print(f"\nතෝරාගන්නා ලදී: {topic_text[:60]}...")
    
    master_prompt = f"""
    Analyze this event or special day: {topic_text}
    You must provide 3 things in EXACTLY the following format:
    [TITLE]
    A short 2 to 4 word punchy English title for this (UPPERCASE).
    [IMAGE_PROMPT]
    A highly detailed, cinematic background image prompt in English representing this. DO NOT INCLUDE ANY TEXT IN THE IMAGE PROMPT.
    [SINHALA_POST]
    Write a highly detailed, exciting Facebook post in Sinhala about this. If it's a historical event, start with "අද වගේ දවසක...". If it's a special day/holiday, start with an exciting hook celebrating the day. Add 4 relevant hashtags. No external links.
    """
    
    short_title = "ON THIS DAY"
    detailed_img_prompt = ""
    post_content = ""
    
    for attempt in range(3):
        try:
            ai_response = client.models.generate_content(model='gemini-flash-latest', contents=master_prompt)
            res_text = ai_response.text
            
            title_match = re.search(r'\[TITLE\](.*?)\[IMAGE_PROMPT\]', res_text, re.DOTALL)
            img_match = re.search(r'\[IMAGE_PROMPT\](.*?)\[SINHALA_POST\]', res_text, re.DOTALL)
            post_match = re.search(r'\[SINHALA_POST\](.*)', res_text, re.DOTALL)
            
            if title_match: short_title = title_match.group(1).strip()
            if img_match: detailed_img_prompt = img_match.group(1).strip()
            if post_match: post_content = post_match.group(1).strip()
            print("✅ AI දත්ත ලබාගැනීම සාර්ථකයි!")
            break 
        except Exception as e:
            print(f"⚠️ AI දෝෂයක්. තත්පර 20කින් නැවත බලයි... ({e})")
            time.sleep(20) 

    if not post_content: 
        return False
        
    if not detailed_img_prompt: 
        detailed_img_prompt = f"A cinematic scene representing: {short_title}. NO TEXT."

    final_image_filename = None 
    print(f"FLUX AI මගින් පින්තූරය අඳිමින් පවතී...")
    encoded_prompt = urllib.parse.quote(detailed_img_prompt)
    random_seed = random.randint(1, 1000000)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true&model=flux&seed={random_seed}"
    
    for attempt in range(3):
        try:
            img_data = requests.get(image_url).content
            base_filename = f"base_temp_{random_seed}.jpg"
            with open(base_filename, "wb") as f: f.write(img_data)
            
            print("පින්තූරය මත අකුරු සටහන් කරමින් පවතී...")
            final_image_filename = add_text_to_image(base_filename, short_title, display_date)
            
            if os.path.exists(base_filename): os.remove(base_filename)
            break 
        except:
            time.sleep(5)
    
    if article_link:
        final_post_text = f"{post_content}\n\n🔗 වැඩිදුර කියවන්න (Wikipedia): {article_link}"
    else:
        final_post_text = f"{post_content}"

    upload_success = False
    try:
        print("Facebook පිටුවට පෝස්ට් කරමින් පවතී...")
        fb_base_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}"
        if final_image_filename and os.path.exists(final_image_filename):
            fb_response = requests.post(f"{fb_base_url}/photos", data={'message': final_post_text, 'access_token': FB_ACCESS_TOKEN}, files={'source': open(final_image_filename, 'rb')})
        else:
            fb_response = requests.post(f"{fb_base_url}/feed", data={'message': final_post_text, 'access_token': FB_ACCESS_TOKEN})
        
        if fb_response.status_code == 200: 
            print("✅ ✅ ✅ පෝස්ට් එක සාර්ථකව Facebook පිටුවට පළ කරන ලදී!")
            upload_success = True
        else:
            print(f"❌ Facebook දෝෂයක්: {fb_response.text}")
    except Exception as e:
        print(f"❌ Upload දෝෂයක්: {e}")
    
    if final_image_filename and os.path.exists(final_image_filename):
        try: os.remove(final_image_filename)
        except: pass
        
    if upload_success:
        save_to_history(topic_text)
        return True
    return False

# ==========================================
# PHASE 1: WIKIPEDIA HISTORY (ප්‍රධාන කේතය)
# ==========================================
print("\n--- PHASE 1: WIKIPEDIA HISTORY ---")
url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/all/{month}/{day}"
headers = {'accept': 'application/json', 'User-Agent': 'DaySpecialBot/6.0'}

try:
    response = requests.get(url, headers=headers)
except:
    response = None

if response and response.status_code == 200:
    data = response.json()
    events_list = data.get('events', [])
    random.shuffle(events_list)
    
    for event in events_list:
        english_text = event.get('text', '')
        if not is_already_posted(english_text):
            historical_year = event.get('year', '')
            display_date = f"{month_name} {day}, {historical_year}" if historical_year else f"{month_name} {day}"
            article_link = "https://en.wikipedia.org/wiki/Main_Page"
            if 'pages' in event and len(event['pages']) > 0:
                article_link = event['pages'][0].get('content_urls', {}).get('desktop', {}).get('page', article_link)
            
            if create_and_publish_post(english_text, display_date, article_link):
                break # එකක් සාර්ථක වුණාම ඊළඟ Phase එකට යයි

# ==========================================
# PHASE 2: DAY OF THE YEAR (අලුත් කේතය)
# ==========================================
if SCRAPER_API_KEY:
    print("\n--- PHASE 2: DAYOFTHEYEAR.COM ---")
    print("මිනිත්තුවක් රැඳී සිටින්න (Facebook Spam වීම වැළැක්වීමට)...")
    time.sleep(60) # විනාඩියක් ඉන්නවා දෙවෙනි එක දාන්න කලින්
    
    target_url = f"https://www.daysoftheyear.com/days/{today.strftime('%Y/%m/%d')}/"
    scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={target_url}"
    
    try:
        doty_resp = requests.get(scraper_url, timeout=60)
        if doty_resp.status_code == 200:
            html_content = doty_resp.text
            # HTML ටැග් මකා දමා පිරිසිදු පාඨය ලබාගැනීම
            text_content = re.sub(r'<style.*?</style>', ' ', html_content, flags=re.DOTALL)
            text_content = re.sub(r'<script.*?</script>', ' ', text_content, flags=re.DOTALL)
            text_content = re.sub(r'<[^>]+>', ' ', text_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Gemini හරහා විශේෂ දින ටික වෙන්කරගැනීම
            extract_prompt = f"Extract all the special holidays, fun days, or observances celebrated today from the following text. Return ONLY a comma-separated list of their names in English (e.g. National Mutt Day, Avocado Day). Do not add any other text. Text: {text_content[:20000]}"
            
            ai_ext_resp = client.models.generate_content(model='gemini-flash-latest', contents=extract_prompt)
            days_list_raw = ai_ext_resp.text
            
            special_days = [d.strip() for d in days_list_raw.split(',') if len(d.strip()) > 3]
            random.shuffle(special_days)
            
            doty_posted = False
            for s_day in special_days:
                clean_day = s_day.replace("'", "").replace("[", "").replace("]", "").replace('"', '')
                if not is_already_posted(clean_day):
                    display_date = f"{month_name} {day}"
                    if create_and_publish_post(clean_day, display_date):
                        doty_posted = True
                        break
                        
            if not doty_posted:
                print("අද දිනට අදාළ අලුත් විශේෂ දිනයක් සොයාගැනීමට නොහැකි විය.")
        else:
            print("ScraperAPI දෝෂයක්!")
    except Exception as e:
        print(f"DayOfTheYear ලබාගැනීමේ දෝෂයක්: {e}")
else:
    print("\nSCRAPER_API_KEY නොමැති බැවින් DayOfTheYear කොටස මඟහරින ලදී.")

print("\n🎉 සියලුම ක්‍රියාවලීන් සම්පූර්ණයි! Cloud Automation සඳහා කේතය නතර වේ.")