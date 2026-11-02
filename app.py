import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from calendar_parser import extract_calendar_events
from email_fetcher import fetch_recent_emails, get_user_profile
from nlp_extractor import (
    INTEREST_OPTIONS,
    analyze_email_for_event,
    match_and_augment_events,
    calculate_recommendations
)

app = FastAPI(title="AI Event Assistant for CAIAS", version="1.1.0")

# Mount static and template directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

AUTO_SYNC_INTERVAL_SECONDS = 1800  # 30 minutes
NEXT_SYNC_TIME = None

# Global Application State
STATE = {
    "calendar_events": [],
    "emails_raw": [],
    "analyzed_emails": [],
    "augmented_events": [],
    "standalone_events": [],
    "all_merged_events": [],
    "active_events": [],
    "expired_events": [],
    "user_profile": {"email": "student@caias.in", "connected": False},
    "last_synced": None,
    "departments": []
}

EMAIL_CACHE_FILE = "emails_cache.json"

def refresh_state(fetch_new_emails=False, max_email_count=35):
    """Refreshes calendar and email data, executes NLP analysis, matching, and active/expired segregation."""
    global NEXT_SYNC_TIME
    # 1. Load Calendar
    cal_events = extract_calendar_events(force_refresh=False)
    STATE["calendar_events"] = cal_events

    # Collect unique departments
    depts = sorted(list({e.get('department') for e in cal_events if e.get('department') and e.get('department') != 'Holiday'}))
    STATE["departments"] = depts

    # 2. Get User Profile
    profile = get_user_profile()
    STATE["user_profile"] = profile

    # 3. Load or Fetch Emails
    if fetch_new_emails:
        emails = fetch_recent_emails(max_results=max_email_count)
        if emails:
            STATE["emails_raw"] = emails
            analyzed = [analyze_email_for_event(em) for em in emails]
            STATE["analyzed_emails"] = analyzed
            try:
                with open(EMAIL_CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(analyzed, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Warning saving email cache: {e}")
    elif os.path.exists(EMAIL_CACHE_FILE):
        try:
            with open(EMAIL_CACHE_FILE, 'r', encoding='utf-8') as f:
                STATE["analyzed_emails"] = json.load(f)
        except Exception as e:
            print(f"Warning reading email cache: {e}")

    # 4. Augment and match events (includes standalone email announcements)
    if STATE["analyzed_emails"]:
        aug_cal, standalone = match_and_augment_events(STATE["calendar_events"], STATE["analyzed_emails"])
        STATE["augmented_events"] = aug_cal
        STATE["standalone_events"] = standalone
        STATE["all_merged_events"] = standalone + aug_cal
    else:
        STATE["augmented_events"] = STATE["calendar_events"]
        STATE["standalone_events"] = []
        STATE["all_merged_events"] = STATE["calendar_events"]

    # 5. Clean Segregation: Active/Upcoming vs Expired/Done Events
    STATE["active_events"] = [e for e in STATE["all_merged_events"] if not e.get("is_expired", False)]
    STATE["expired_events"] = [e for e in STATE["all_merged_events"] if e.get("is_expired", False)]

    STATE["last_synced"] = datetime.now().strftime("%I:%M %p, %d %b %Y")
    NEXT_SYNC_TIME = datetime.now() + timedelta(seconds=AUTO_SYNC_INTERVAL_SECONDS)

    print(f"State ready: {len(STATE['active_events'])} active events, "
          f"{len(STATE['expired_events'])} expired events, "
          f"{len(STATE['standalone_events'])} standalone email notices.")

async def background_sync_worker():
    """Background task that automatically syncs Gmail every 30 minutes to keep tokens refreshed."""
    global NEXT_SYNC_TIME
    while True:
        try:
            await asyncio.sleep(AUTO_SYNC_INTERVAL_SECONDS)
            print("⏰ [Auto-Sync] 30m scheduled sync triggered. Refreshing Gmail tokens and events...")
            refresh_state(fetch_new_emails=True, max_email_count=35)
            print(f"✅ [Auto-Sync] Completed successfully at {STATE['last_synced']}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"⚠️ [Auto-Sync Error]: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def on_startup():
    try:
        has_cache = os.path.exists(EMAIL_CACHE_FILE)
        refresh_state(fetch_new_emails=not has_cache, max_email_count=25)
    except Exception as e:
        print(f"Startup initialization note: {e}")
        cal_events = extract_calendar_events()
        STATE["calendar_events"] = cal_events
        STATE["all_merged_events"] = cal_events
        STATE["active_events"] = [e for e in cal_events if not e.get("is_expired")]
        STATE["expired_events"] = [e for e in cal_events if e.get("is_expired")]

    # Launch background auto-sync worker
    asyncio.create_task(background_sync_worker())

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "interest_options": INTEREST_OPTIONS,
            "departments": STATE["departments"],
            "user_profile": STATE["user_profile"],
            "last_synced": STATE["last_synced"] or "Not yet synced",
            "active_count": len(STATE["active_events"]),
            "expired_count": len(STATE["expired_events"])
        }
    )

@app.get("/api/status")
def get_status():
    enriched_count = sum(1 for e in STATE["active_events"] if e.get("has_email_update"))
    remaining_seconds = 0
    if NEXT_SYNC_TIME:
        diff = (NEXT_SYNC_TIME - datetime.now()).total_seconds()
        remaining_seconds = max(0, int(diff))

    return {
        "connected": STATE["user_profile"].get("connected", False),
        "user_email": STATE["user_profile"].get("email") or "Not connected",
        "calendar_count": len(STATE["calendar_events"]),
        "emails_analyzed_count": len(STATE["analyzed_emails"]),
        "email_events_count": sum(1 for a in STATE["analyzed_emails"] if a.get("is_event")),
        "enriched_calendar_count": enriched_count,
        "standalone_events_count": len(STATE["standalone_events"]),
        "active_events_count": len(STATE["active_events"]),
        "expired_events_count": len(STATE["expired_events"]),
        "auto_sync_enabled": True,
        "auto_sync_interval_seconds": AUTO_SYNC_INTERVAL_SECONDS,
        "next_sync_seconds": remaining_seconds,
        "last_synced": STATE["last_synced"],
        "departments": STATE["departments"]
    }

@app.get("/api/events")
def get_events(
    interests: Optional[str] = Query(None, description="Comma-separated interests"),
    department: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    status_filter: str = Query("active", description="active, expired, or all"),
    time_filter: str = Query("all"),
    quick_filter: Optional[str] = Query(None, description="today, this_week, registration, standalone"),
    only_email_updates: bool = Query(False),
    limit: int = Query(60)
):
    """
    Returns filtered, scored, and categorized events.
    By default, excludes expired events and only returns active/upcoming events.
    """
    interest_list = [i.strip() for i in interests.split(",")] if interests else [
        "Coding and Programming", "Artificial Intelligence", "Business and Entrepreneurship"
    ]

    # Select base list based on status_filter
    if status_filter == "expired":
        base_list = STATE["expired_events"]
    elif status_filter == "all":
        base_list = STATE["all_merged_events"]
    else:
        # Default: ONLY active and upcoming events (expired events pushed out)
        base_list = STATE["active_events"]

    today_dt = datetime.now().date()
    today_str = today_dt.isoformat()
    week_later_str = (today_dt + timedelta(days=7)).isoformat()

    # Time filter
    if time_filter == "upcoming":
        filtered = [e for e in base_list if (e.get("end_date") or e.get("start_date", "")) >= today_str]
    elif time_filter == "today_week":
        filtered = [
            e for e in base_list
            if (e.get("start_date") or "") <= week_later_str and (e.get("end_date") or "") >= today_str
        ]
    elif time_filter == "past":
        filtered = [e for e in base_list if (e.get("end_date") or "") < today_str]
    else:
        filtered = list(base_list)

    # Quick filters
    if quick_filter == "today":
        filtered = [e for e in filtered if e.get("start_date") == today_str or (e.get("start_date", "") <= today_str <= e.get("end_date", ""))]
    elif quick_filter == "this_week":
        filtered = [e for e in filtered if (e.get("start_date") or "") <= week_later_str and (e.get("end_date") or "") >= today_str]
    elif quick_filter == "registration":
        filtered = [e for e in filtered if e.get("registration_link") or (e.get("email_data") and e["email_data"].get("registration_link"))]
    elif quick_filter == "standalone":
        filtered = [e for e in filtered if e.get("is_standalone_email")]
    elif quick_filter == "certificate":
        filtered = [e for e in filtered if e.get("certificate") or (e.get("email_data") and e["email_data"].get("certificate"))]
    elif quick_filter == "free":
        filtered = [e for e in filtered if (e.get("fee") and "free" in str(e.get("fee")).lower()) or (e.get("email_data") and e["email_data"].get("fee") and "free" in str(e["email_data"].get("fee")).lower())]

    # Email updates only filter
    if only_email_updates:
        filtered = [e for e in filtered if e.get("has_email_update")]

    # Department filter
    if department and department != "All":
        filtered = [e for e in filtered if e.get("department") == department]

    # Keyword search query
    if query:
        q_lower = query.lower()
        filtered = [
            e for e in filtered
            if q_lower in e.get("title", "").lower()
            or q_lower in e.get("department", "").lower()
            or q_lower in e.get("venue", "").lower()
            or (e.get("stall_info") and q_lower in e["stall_info"].lower())
            or (e.get("email_data") and q_lower in e["email_data"].get("snippet", "").lower())
        ]

    # Compute personalized scores
    scored = calculate_recommendations(
        filtered,
        user_interests=interest_list,
        top_n=limit,
        include_past=(status_filter in ["expired", "all"])
    )

    return {
        "count": len(scored),
        "total_available": len(filtered),
        "status_filter": status_filter,
        "active_total": len(STATE["active_events"]),
        "expired_total": len(STATE["expired_events"]),
        "events": scored
    }

@app.get("/api/email_notices")
def get_email_notices():
    """Returns analyzed emails with full NLP entity breakdown."""
    return {
        "count": len(STATE["analyzed_emails"]),
        "emails": STATE["analyzed_emails"]
    }

@app.get("/api/cron_sync")
def cron_sync():
    """Endpoint triggered by Vercel Cron jobs or external cron services to auto-sync every 30 minutes."""
    try:
        refresh_state(fetch_new_emails=True, max_email_count=35)
        return {
            "status": "success",
            "message": "Cron auto-sync completed successfully",
            "last_synced": STATE["last_synced"],
            "active_events": len(STATE["active_events"])
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/sync_emails")
def sync_emails(max_count: int = Query(35)):
    """Triggers live synchronization with Gmail API and refreshes token."""
    try:
        refresh_state(fetch_new_emails=True, max_email_count=max_count)
        return {
            "success": True,
            "message": "Gmail synchronized and OAuth token verified.",
            "emails_fetched": len(STATE["analyzed_emails"]),
            "active_events": len(STATE["active_events"]),
            "last_synced": STATE["last_synced"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync Gmail: {str(e)}")

@app.post("/api/reload_calendar")
def reload_calendar():
    """Re-extracts calendar from PDF."""
    try:
        extract_calendar_events(force_refresh=True)
        refresh_state(fetch_new_emails=False)
        return {"success": True, "message": "Calendar PDF re-parsed and cached."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export_ics/{event_id}")
def export_ics(event_id: str):
    """Generates an .ics calendar file for standard import into Google Calendar or Apple/Outlook."""
    event = next((e for e in STATE["all_merged_events"] if e.get("id") == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    title = event.get("title", "CAIAS Event")
    venue = event.get("venue", "CAIAS Campus")
    start_date_str = event.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    end_date_str = event.get("end_date", start_date_str)
    dept = event.get("department", "CAIAS")

    desc = f"Department: {dept}\\nVenue: {venue}\\nTime: {event.get('time', 'Refer to notice')}"
    if event.get("registration_link"):
        desc += f"\\nRegistration Link: {event['registration_link']}"
    if event.get("email_data"):
        desc += f"\\n\\nEmail Notice: {event['email_data'].get('subject')}\\nSnippet: {event['email_data'].get('snippet')}"

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CAIAS//AI Event Assistant//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
SUMMARY:{title}
LOCATION:{venue}
DESCRIPTION:{desc}
DTSTART;VALUE=DATE:{start_date_str.replace('-', '')}
DTEND;VALUE=DATE:{end_date_str.replace('-', '')}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="caias_event_{event_id}.ics"'}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
