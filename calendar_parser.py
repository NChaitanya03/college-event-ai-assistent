import os
import json
import re
from datetime import datetime
import pdfplumber
import pandas as pd

CACHE_FILE = "calendar_cache.json"
PDF_FILE = "CAIAS COE 2026 - 27.pdf"

DATE_FORMATS = ['%d-%b-%y', '%d-%b-%Y', '%d-%B-%y', '%d-%B-%Y', '%Y-%m-%d']

def parse_date(value):
    value = str(value or '').strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    return None

def extract_calendar_events(pdf_path=PDF_FILE, force_refresh=False):
    """
    Extracts events from the CAIAS Academic Calendar PDF.
    Caches the results to a JSON file for high-speed subsequent loads.
    """
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                events = json.load(f)
                if events:
                    return events
        except Exception as e:
            print(f"Error reading cache: {e}. Re-parsing PDF...")

    if not os.path.exists(pdf_path):
        print(f"PDF file not found at {pdf_path}")
        return []

    print(f"Parsing calendar events from {pdf_path}...")
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            for table in tables:
                for row in table:
                    if not row or len(row) < 5:
                        continue
                    vals = [re.sub(r'\s+', ' ', str(x or '')).strip() for x in row[:5]]
                    department, start_raw, end_raw, day_name, title = vals
                    
                    start_date = parse_date(start_raw)
                    if start_date is None:
                        continue  # Skip header rows
                    
                    end_date = parse_date(end_raw) or start_date
                    title = title.strip() or 'Unspecified Event'
                    if title.lower() in {'event title', 'title'}:
                        continue

                    # Filter out purely empty holidays or keep as holiday tag
                    is_holiday = department.lower() == 'holiday' or 'holiday' in title.lower()

                    event_id = f"cal_{page_num}_{len(records)+1}"
                    records.append({
                        'id': event_id,
                        'source': 'calendar',
                        'department': department or 'General',
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'day': day_name,
                        'title': title,
                        'source_page': page_num,
                        'is_holiday': is_holiday,
                        'venue': 'CAIAS Campus' if not is_holiday else 'N/A',
                        'time': '',
                        'has_email_update': False,
                        'email_data': None
                    })

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for r in records:
        key = (r['department'], r['start_date'], r['end_date'], r['title'].lower())
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    # Save to cache
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(deduped, f, indent=2, ensure_ascii=False)
        print(f"Cached {len(deduped)} events to {CACHE_FILE}")
    except Exception as e:
        print(f"Warning: could not write {CACHE_FILE}: {e}")

    return deduped

if __name__ == "__main__":
    events = extract_calendar_events(force_refresh=True)
    print(f"Total extracted: {len(events)}")
    for e in events[:5]:
        print(e)

