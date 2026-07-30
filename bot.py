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

client = genai.Client(api_key=GEMINI_API_KEY)

# --- Sri Lanka Timezone Fix (UTC +5:30) ---
sl_tz = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(sl_tz)

month = today.strftime("%m")
day = today.strftime("%d")
month_name = today.strftime("%B")

print(f"ශ්‍රී ලංකා වේලාවෙන් අද දිනය: {month}/{day}")

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
            print(f"ෆොන්ට් ඩවුන්ලෝඩ් දෝෂයක්: {e}")
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
    except Exception as e:
        print(f"පින්තූරයේ අකුරු ලිවීමේදී දෝෂයක්: {e}")
        return image_path

url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/all/{month}/{day}"
headers = {'accept': 'application/json', 'User-Agent': 'DaySpecialBot/4.0'}

try:
    response = requests.get(url, headers=headers)
except:
    response = None

if response and response.status_code == 200:
    data = response.json()
    
    # සිදුවීම් සහ විශේෂ දින වෙන වෙනම වෙන් කරගැනීම
    events_list = data.get('events', [])
    holidays_list = data.get('holidays', [])
    
    random.shuffle(events_list)
    random.shuffle(holidays_list)
    
    selected_event = None
    event_type = ""

    # පළමුවෙන්ම අද දවසට අදාළ විශේෂ දිනයක් (Holiday/Observance) තියෙනවද බලයි
    for holiday in holidays_list:
        english_text = holiday.get('text', '')
        if not is_already_posted(english_text):
            selected_event = holiday
            event_type = "විශේෂ දිනයක්"
            break

    # විශේෂ දින මුකුත් නැත්නම් (හෝ ඒ ඔක්කොම කලින් දාලා නම්), ඉතිහාස කතාවක් තෝරගනී
    if not selected_event:
        for event in events_list:
            english_text = event.get('text', '')
            if not is_already_posted(english_text):
                selected_event = event
                event_type = "ඉතිහාස සිදුවීමක්"
                break
                
    if selected_event:
        english_text = selected_event.get('text', '')
        historical_year = selected_event.get('year', '')
        display_date = f"{month_name} {day}, {historical_year}" if historical_year else f"{month_name} {day}"
            
        article_link = "https://en.wikipedia.org/wiki/Main_Page"
        if 'pages' in selected_event and len(selected_event['pages']) > 0:
            article_link = selected_event['pages'][0].get('content_urls', {}).get('desktop', {}).get('page', article_link)

        print(f"\n{event_type} තෝරාගන්නා ලදී: {english_text[:60]}...")
        
        # AI Prompt එක පොඩ්ඩක් වෙනස් කළා විශේෂ දින වලටත් ගැලපෙන්න
        master_prompt = f"""
        Analyze this event or special day: {english_text}
        You must provide 3 things in EXACTLY the following format:
        [TITLE]
        A short 2 to 4 word punchy English title for this (UPPERCASE).
        [IMAGE_PROMPT]
        A highly detailed, cinematic background image prompt in English representing this. DO NOT INCLUDE ANY TEXT IN THE IMAGE PROMPT.
        [SINHALA_POST]
        Write a highly detailed Facebook post in Sinhala. If it's a historical event, start with "අද වගේ දවසක...". If it's a special day/holiday, start with an exciting hook celebrating the day. Add 4 relevant hashtags. No external links.
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
                print("✅ දත්ත ලබාගැනීම සාර්ථකයි!")
                break 
            except Exception as e:
                print(f"⚠️ AI ලිමිට්/දෝෂයක්. තත්පර 20කින් නැවත බලයි... ({e})")
                time.sleep(20) 

        if post_content:
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
                    base_filename = "base_image_temp.jpg"
                    with open(base_filename, "wb") as f: f.write(img_data)
                    
                    print("පින්තූරය මත අකුරු සටහන් කරමින් පවතී...")
                    final_image_filename = add_text_to_image(base_filename, short_title, display_date)
                    
                    if os.path.exists(base_filename): os.remove(base_filename)
                    break 
                except:
                    time.sleep(5)
            
            final_post_text = f"{post_content}\n\n🔗 වැඩිදුර කියවන්න (Wikipedia): {article_link}"

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
                save_to_history(english_text)
                print("\n🎉 පෝස්ට් එක සම්පූර්ණයි! Cloud Automation සඳහා කේතය නතර වේ.")
            else:
                print("\n⚠️ අසාර්ථක විය. Script එක නතර වේ (Loop වීම වැළැක්වීමට).")
        else:
            print("පෝස්ට් විස්තරය නොමැත.")