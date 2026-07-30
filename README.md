# 🕰️ Days Special Auto-Bot | The IT Forge

An autonomous, AI-powered Facebook bot built with Python that fetches historical events, generates localized content, creates cinematic images, and automatically publishes them hourly.

## 🚀 Overview
This project is designed to fully automate the content creation pipeline for Facebook pages. It runs completely in the cloud using GitHub Actions, requiring no local server. The bot retrieves "On This Day" historical data, uses AI to translate and expand the content into engaging Sinhala posts, generates text-overlaid cinematic background images, and posts directly to Facebook.

## ✨ Key Features
* **100% Autonomous Automation:** Runs hourly via GitHub Actions Cron Jobs.
* **AI Content Generation:** Integrates **Google Gemini AI** to generate highly detailed, engaging Facebook post descriptions in Sinhala with relevant hashtags.
* **Cinematic Image Generation:** Utilizes **FLUX AI** (via Pollinations) to create photorealistic, text-free historical background images.
* **Dynamic Typography:** Uses Python's `Pillow` library to dynamically center-align and overlay bold event titles and historical dates onto the AI-generated images.
* **Smart History Tracking:** Implements a file-based memory system (`posted_history.txt`) to ensure no event is ever posted twice.
* **Hybrid Cloud/Local Execution:** Gracefully handles font loading and API keys whether running locally in VS Code or in the GitHub Linux cloud environment.

## 🛠️ Technologies Used
* **Language:** Python 3.10
* **AI Models:** Google Gemini Flash, FLUX AI
* **APIs:** Wikipedia REST API, Facebook Graph API v19.0
* **Libraries:** `requests`, `google-genai`, `Pillow`, `textwrap`, `re`
* **CI/CD & Automation:** GitHub Actions, Ubuntu Runners

## 🔒 Security
All sensitive credentials (API Keys and Access Tokens) are strictly managed via **GitHub Secrets** and are injected into the environment dynamically. No keys are hardcoded in the repository.

* `GEMINI_API_KEY` - Google AI Studio
* `FB_PAGE_ID` - Facebook Page Identifier
* `FB_ACCESS_TOKEN` - Meta Graph API Token

## ⚙️ How It Works (The Pipeline)
1. **Trigger:** GitHub Actions wakes up every hour.
2. **Fetch:** Pulls today's historical events and global holidays from Wikipedia.
3. **Filter:** Checks against the local history ledger to find a fresh, unposted event.
4. **Prompt:** Sends a Master Prompt to Gemini AI to extract a short title, image prompt, and Sinhala description.
5. **Render:** FLUX AI generates the base image; `Pillow` writes the text.
6. **Publish:** Sends the final image and text payload to Facebook via Graph API.
7. **Commit:** Saves the event to history and auto-commits the ledger back to the repository.

---
*Developed and maintained for **The IT Forge***
