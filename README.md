# AI Event Assistant for CAIAS
**Christ Academy Institute for Advanced Studies (CAIAS)**

A full-stack, AI-powered web application that assists students with upcoming campus events by integrating official **Academic Calendar (COE 2026–2027)** schedules with **live Gmail notifications** using NLP entity extraction, real-time background synchronization, and personalized recommendation algorithms.

---

## 🌟 Key Features

### 1. 🔄 30-Minute Background Auto-Sync & Token Keep-Alive
- Runs an asynchronous background worker every **30 minutes** (`1800s`).
- Checks Google OAuth tokens and automatically refreshes them with `refresh_token`, keeping authentication active.
- Fetches new student emails, runs NLP entity extraction, updates event caches, and updates the UI without requiring manual re-login.
- Includes a live countdown in the top bar (`Auto-Sync: 29:45`) and an instant **"Sync Now"** manual button.

### 2. ⚡ Clean Event Segregation (Active vs. Expired/Past Events)
- **Active & Upcoming Events (260+ events)**: The primary view strictly displays upcoming and ongoing events.
- **Completed / Past Events Archive (210+ events)**: Events that have already concluded are cleanly pushed into a dedicated **"Completed / Past Events"** tab, tagged with completion dates (e.g., *"Completed 4 days ago"*).
- Dynamic countdown pills on cards:
  - 🔥 **Happening Today!** (pulsing badge)
  - ⚡ **Tomorrow**
  - 📅 **In X Days / Weeks**
  - ✓ **Completed on [Date]**

### 3. 🔍 Deep NLP Metadata Extraction
Extracts enriched event details from email bodies:
- 📝 **Registration Form Links**: Detects Google Forms (`forms.gle`), Typeform, and college portals; surfaces direct **"Register"** buttons.
- 💬 **WhatsApp Group Links**: Extracts `chat.whatsapp.com` links for 1-click group joining.
- ⏰ **Registration Deadlines**: Parses last dates to register (e.g., *"Deadline: 31 October"*).
- 📍 **Live Venues**: Extracts locations (*Basketball Court*, *Seminar Hall*, *Main Auditorium*, *Mamma Maria Chapel*).
- 🏪 **Stalls & Food Menus**: Detects trade fair stalls (*UDYAMA Stall No. 13*, *Kuchiku Cafe menu*).
- 👥 **Eligibility / Target Students**: Identifies applicable courses (*BCA*, *BBA*, *B.Com*, etc.).
- 📞 **Coordinators & Contact Numbers**: Extracts student/faculty coordinator names and phone numbers.

### 4. 📢 Standalone Email Announcements
- College announcements or club notices received via Gmail that are **not present** on the COE academic calendar are automatically created as **Live Campus Notices** and added to the active event stream with a prominent badge.

### 5. ⭐ Bookmarks & 📤 1-Click Sharing
- **Save / Bookmark Events**: Star your favorite events to view them under the **"⭐ Saved Bookmarks"** quick filter (stored in browser `localStorage`).
- **Share via WhatsApp / Copy Details**: 1-click button formats the event title, date, time, venue, and registration link for easy sharing with classmates.
- **Add to Google Calendar & .ics Export**: Add any event directly to Google Calendar, Outlook, or Apple Calendar.

---

## 🚀 How to Run

1. Open your terminal in this directory:
```powershell
.\.venv\Scripts\python run.py
```

2. Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📁 Project Architecture

```
AI EVent Assitant/
├── app.py                     # FastAPI app with 30m background sync worker & REST APIs
├── run.py                     # Launcher script
├── calendar_parser.py         # 37-page COE calendar PDF extractor
├── email_fetcher.py           # Gmail API client with auto-refresh token handling
├── nlp_extractor.py           # NLP extraction (Venues, Times, Links, Deadlines, TF-IDF engine)
├── calendar_cache.json        # Cached 480 calendar events
├── emails_cache.json          # Cached analyzed emails with NLP metadata
├── templates/
│   └── index.html             # High-end Tailwind CSS dashboard
├── static/
│   ├── css/styles.css         # Styling, glassmorphism & animations
│   └── js/app.js              # Client reactivity, 30m timer, search, bookmarks & modals
├── credentials.json           # Google Cloud OAuth credentials
├── token.json                 # User authorization token (auto-refreshed)
├── CAIAS COE 2026 - 27.pdf    # University Academic Calendar
└── README.md
```
