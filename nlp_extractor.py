import re
from datetime import datetime, timedelta
import dateutil.parser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Interest categories matching the student domain
INTEREST_OPTIONS = [
    'Artificial Intelligence',
    'Coding and Programming',
    'Web Development',
    'Cybersecurity',
    'Robotics and IoT',
    'Data Science',
    'Hackathons and Ideathons',
    'Business and Entrepreneurship',
    'Finance and Stock Market',
    'Career and Placements',
    'Communication Skills',
    'Science',
    'Sports and Fitness',
    'Cultural Events',
    'Volunteering and Social Outreach',
    'Research',
    'Psychology and Well-being',
    'Literature and Writing',
    'Environmental Sustainability',
    'General Events'
]

INTEREST_TERMS = {
    'Artificial Intelligence': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'data science', 'llm', 'nlp', 'digital'],
    'Coding and Programming': ['coding', 'programming', 'python', 'java', 'c++', 'software', 'computer', 'it club', 'technovanza', 'code', 'developer'],
    'Web Development': ['web', 'website', 'frontend', 'backend', 'fullstack', 'react', 'javascript', 'html', 'css', 'ui', 'ux'],
    'Cybersecurity': ['cyber', 'security', 'cyber ethics', 'cyber safe', 'privacy', 'ethical hacking', 'infosec', 'firewall'],
    'Robotics and IoT': ['robot', 'robotic', 'iot', 'internet of things', 'electronics', 'arduino', 'raspberry pi', 'sensors'],
    'Data Science': ['data', 'analytics', 'power bi', 'tableau', 'visualization', 'statistics', 'dataset', 'bi'],
    'Hackathons and Ideathons': ['hackathon', 'ideathon', 'idea challenge', 'innovation', 'bootcamp', 'design thinking', 'pitch', 'hack'],
    'Business and Entrepreneurship': ['business', 'entrepreneur', 'entrepreneurship', 'startup', 'trade fair', 'management', 'biz quest', 'udyama', 'stall', 'commerce', 'marketing', 'sales'],
    'Finance and Stock Market': ['finance', 'financial', 'stock market', 'wealth', 'investment', 'tax', 'banking', 'equity', 'shares', 'accounting'],
    'Career and Placements': ['career', 'placement', 'employability', 'interview', 'resume', 'linkedin', 'aptitude', 'job', 'internship', 'hiring'],
    'Communication Skills': ['communication', 'writing', 'email etiquette', 'leadership', 'soft skills', 'public speaking', 'toastmasters'],
    'Science': ['science', 'physics', 'mathematics', 'scientia', 'chemistry', 'research', 'laboratory', 'lab'],
    'Sports and Fitness': ['sports', 'football', 'cricket', 'volleyball', 'basketball', 'karate', 'marathon', 'fitness', 'tournament', 'wellness', 'badminton'],
    'Cultural Events': ['cultural', 'dance', 'fest', 'festival', 'music', 'rangotsav', 'sangamotsav', 'celebration', 'drama', 'theatre', 'singing', 'food fest'],
    'Volunteering and Social Outreach': ['outreach', 'nss', 'ncc', 'volunteer', 'community', 'plantation', 'social', 'ngo', 'blood donation'],
    'Research': ['research', 'conference', 'seminar', 'literature review', 'publication', 'patent', 'fdp', 'faculty development'],
    'Psychology and Well-being': ['psychology', 'well-being', 'wellness', 'mental health', 'kindness', 'counselling', 'mindfulness'],
    'Literature and Writing': ['literature', 'writing', 'storytelling', 'hindi', 'kannada', 'english', 'books', 'journalism', 'poetry'],
    'Environmental Sustainability': ['sustainable', 'sustainability', 'environment', 'plantation', 'zero hunger', 'green', 'eco', 'millet'],
    'General Events': []
}

COMMON_VENUES = [
    r'Basketball Court',
    r'Main Auditorium',
    r'Open Air Auditorium',
    r'Auditorium',
    r'Mamma Maria Chapel',
    r'Chapel',
    r'Seminar Hall\s*(?:[-–]\s*\d+|\d+)?',
    r'Conference Hall',
    r'Central Library',
    r'Library Reading Hall',
    r'Quadrangle',
    r'Amphitheatre',
    r'Cafeteria',
    r'Canteen',
    r'College Ground',
    r'Sports Complex',
    r'Computer Lab\s*\d*',
    r'Lab\s*\d+',
    r'Room\s*(?:No\.?\s*)?\d+[A-Za-z]?',
    r'Block\s+[A-Za-z]',
    r'Stall\s*(?:No\.?\s*)?\d+',
    r'Google Meet',
    r'Zoom(?:\s+Meeting)?',
    r'MS Teams',
    r'Online'
]

# Patterns that indicate purely non-event administrative/spam messages
EXCLUDE_SUBJECT_PATTERNS = [
    r'security alert',
    r'new sign-in',
    r'verification code',
    r'password reset',
    r'two-step verification',
    r'viewed your profile',
    r'notifications? for',
    r'invitation to connect',
    r'talent acquisition',
    r'job alert',
    r'recruiter'
]

def clean_subject(subject):
    """Strips reply prefixes, emojis and cleans subject line."""
    cleaned = re.sub(r'^(?:Re|Fwd|Fw)\s*:\s*', '', subject, flags=re.I)
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def extract_dates_from_text(text, reference_date=None):
    """
    Extracts dates mentioned in text.
    Handles relative dates like 'Tomorrow', 'Today', and explicit date strings.
    """
    if reference_date is None:
        reference_date = datetime.now()

    found_dates = []

    if re.search(r'\btomorrow\b', text, re.I):
        t_date = (reference_date + timedelta(days=1)).date()
        found_dates.append({
            'raw': 'Tomorrow',
            'parsed_iso': t_date.isoformat(),
            'formatted': t_date.strftime('%d %b %Y')
        })
    if re.search(r'\btoday\b', text, re.I):
        t_date = reference_date.date()
        found_dates.append({
            'raw': 'Today',
            'parsed_iso': t_date.isoformat(),
            'formatted': t_date.strftime('%d %b %Y')
        })

    date_patterns = [
        r'(?:Date\s*[:\-]\s*)?((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?,?\s*\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:\s+\d{2,4})?)',
        r'(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s*,?\s*\d{4})?)'
    ]

    for pat in date_patterns:
        for match in re.finditer(pat, text, re.I):
            raw_str = match.group(1).strip()
            cleaned_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', raw_str)
            try:
                dt = dateutil.parser.parse(cleaned_str, default=reference_date, fuzzy=True)
                iso = dt.date().isoformat()
                if not any(d['parsed_iso'] == iso for d in found_dates):
                    found_dates.append({
                        'raw': raw_str,
                        'parsed_iso': iso,
                        'formatted': dt.strftime('%d %b %Y')
                    })
            except Exception:
                pass

    return found_dates

def extract_times_from_text(text):
    """Extracts event times from text."""
    time_matches = []
    explicit_pat = r'(?:Time|Timings?|Schedule)\s*[:\-]\s*([0-9]{1,2}(?::[0-9]{2})?\s*(?:AM|PM|am|pm)?(?:\s*(?:to|-|–)\s*[0-9]{1,2}(?::[0-9]{2})?\s*(?:AM|PM|am|pm))?)'
    for m in re.finditer(explicit_pat, text, re.I):
        time_matches.append(m.group(1).strip())

    range_pat = r'\b([0-9]{1,2}(?::[0-9]{2})?\s*(?:AM|PM|am|pm)\s*(?:to|-|–)\s*[0-9]{1,2}(?::[0-9]{2})?\s*(?:AM|PM|am|pm))\b'
    for m in re.finditer(range_pat, text, re.I):
        t = m.group(1).strip()
        if t not in time_matches:
            time_matches.append(t)

    single_pat = r'(?:at|from)\s+([0-9]{1,2}(?::[0-9]{2})?\s*(?:AM|PM|am|pm))\b'
    for m in re.finditer(single_pat, text, re.I):
        t = m.group(1).strip()
        if t not in time_matches:
            time_matches.append(t)

    return time_matches

def extract_venues_from_text(text):
    """Extracts event venues or locations."""
    venues = []
    explicit_pat = r'(?:Venue|Location|Place)\s*[:\-]\s*([^\n\r•,\.;]+)'
    for m in re.finditer(explicit_pat, text, re.I):
        val = m.group(1).strip()
        if 2 < len(val) < 60:
            venues.append(val)

    for pat in COMMON_VENUES:
        m = re.search(r'\b(' + pat + r')\b', text, re.I)
        if m:
            v = m.group(1).strip()
            if not any(v.lower() in existing.lower() for existing in venues):
                venues.append(v)

    return venues

def extract_rich_metadata_from_text(text):
    """
    Extracts deep metadata from email content:
    - Categorized links (Registration forms, WhatsApp groups, virtual meetings)
    - Deadlines / Last date to register
    - Contact persons & phone numbers
    - Target audience / Eligibility
    - Fee info
    - Key highlights & menu/stalls
    """
    metadata = {
        'registration_link': None,
        'whatsapp_link': None,
        'meeting_link': None,
        'all_links': [],
        'deadline': None,
        'contact_numbers': [],
        'coordinators': [],
        'eligibility': None,
        'fee': None,
        'highlights': [],
        'stall_info': None
    }

    # 1. Links Extraction & Categorization
    urls = re.findall(r'https?://[^\s<>"\')]+', text)
    cleaned_urls = []
    for u in urls:
        # Strip trailing punctuation
        u_clean = u.rstrip('.,;:')
        if u_clean not in cleaned_urls:
            cleaned_urls.append(u_clean)

    metadata['all_links'] = cleaned_urls

    for url in cleaned_urls:
        url_lower = url.lower()
        if any(d in url_lower for d in ['forms.gle', 'google.com/forms', 'docs.google.com/forms', 'typeform', 'surveymonkey', 'register']):
            if not metadata['registration_link']:
                metadata['registration_link'] = url
        elif 'chat.whatsapp.com' in url_lower:
            if not metadata['whatsapp_link']:
                metadata['whatsapp_link'] = url
        elif any(d in url_lower for d in ['meet.google.com', 'zoom.us', 'teams.microsoft.com', 'webex']):
            if not metadata['meeting_link']:
                metadata['meeting_link'] = url

    # 2. Registration Deadline
    deadline_patterns = [
        r'(?:Last\s+date\s+to\s+register|Registration\s+closes|Register\s+before|Deadline|Last\s+date)\s*[:\-]?\s*([^\n\r•\.,]{4,45})',
        r'(?:submissions?\s+close\s+on?)\s*([^\n\r•\.,]{4,35})'
    ]
    for d_pat in deadline_patterns:
        m = re.search(d_pat, text, re.I)
        if m:
            metadata['deadline'] = m.group(1).strip()
            break

    # 3. Contact Numbers & Coordinators
    phones = re.findall(r'\b(?:\+?91[\s\-]?)?[6-9]\d{4}\s*\d{5}\b|\b(?:\+?91[\s\-]?)?[6-9]\d{9}\b', text)
    metadata['contact_numbers'] = list(dict.fromkeys(phones))

    coordinator_patterns = [
        r'(?:Faculty\s+Coordinator|Student\s+Coordinator|Contact\s+Person|Coordinators?|For\s+queries\s+contact)\s*[:\-]?\s*([^\n\r•]+)'
    ]
    for c_pat in coordinator_patterns:
        m = re.search(c_pat, text, re.I)
        if m:
            c_text = m.group(1).strip()
            if 3 < len(c_text) < 70:
                metadata['coordinators'].append(c_text)

    # 4. Eligibility / Target Audience
    eligibility_patterns = [
        r'(?:Eligibility|Open\s+to|Target\s+Audience|For)\s*[:\-]?\s*([^\n\r•]{4,60})'
    ]
    for e_pat in eligibility_patterns:
        m = re.search(e_pat, text, re.I)
        if m:
            metadata['eligibility'] = m.group(1).strip()
            break

    if not metadata['eligibility']:
        # Check course mentions
        courses_found = []
        for course in ['BCA', 'BBA', 'B.Com', 'B.Sc', 'BA', 'MBA', 'MCA', 'All Students', 'Faculty']:
            if re.search(r'\b' + re.escape(course) + r'\b', text, re.I):
                courses_found.append(course)
        if courses_found:
            metadata['eligibility'] = f"Students of {', '.join(courses_found)}"

    # 5. Fee Info
    if re.search(r'\b(?:free\s+(?:entry|registration|of\s+cost)|no\s+(?:registration\s+)?fee|registration\s+free)\b', text, re.I):
        metadata['fee'] = "Free Entry"
    else:
        fee_m = re.search(r'(?:Registration\s+Fee|Entry\s+Fee|Fee)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*(\d+)', text, re.I)
        if fee_m:
            metadata['fee'] = f"₹{fee_m.group(1)}"
        elif re.search(r'\b(?:free)\b', text, re.I) and any(w in text.lower() for w in ['entry', 'workshop', 'webinar', 'seminar', 'attend']):
            metadata['fee'] = "Free Entry"

    # 6. Certificate Provided Info
    cert_pat = r'(?:e-?\s*certificates?|certificates?)\s*(?:of\s+participation)?\s*(?:will\s+be\s+provided|provided|issued|awarded|given|for\s+all\s+participants?|to\s+all)'
    if re.search(cert_pat, text, re.I) or re.search(r'\b(?:participation\s+certificate|e-certificate\s+will\s+be\s+given)\b', text, re.I):
        metadata['certificate'] = "Certificate Provided"
    elif re.search(r'\b(?:e-?certificates?|certificates?)\b', text, re.I) and any(w in text.lower() for w in ['all participants', 'registered participants', 'attendees']):
        metadata['certificate'] = "Certificate Provided"
    elif re.search(r'\b(?:merit\s+certificates?|winner\s+certificates?)\b', text, re.I):
        metadata['certificate'] = "Merit Certificate"
    else:
        metadata['certificate'] = None

    # 7. Attendance / Duty Leave Credited
    if re.search(r'\b(?:attendance|duty\s*leave)\s*(?:will\s+be\s+provided|provided|marked|credited|given)\b', text, re.I):
        metadata['attendance'] = "Attendance Provided"
    else:
        metadata['attendance'] = None

    # 8. Prizes / Cash Rewards / Trophies / Cups
    if re.search(r'\b(?:sangam\s*cup|the\s*battle\s*for\s*the\s*cup|cup\b|championship\s*trophy)\b', text, re.I):
        metadata['prizes'] = "Sangam Cup & Trophies"
    elif re.search(r'\b(?:prizes?\s*and\s*recognition|cash\s*prizes?|top\s*\d+\s*winners?|prizes?\s*worth|awards?|trophies|medals|goodies|what\s+you\s+can\s+win)\b', text, re.I):
        prize_m = re.search(r'(?:cash\s*prizes?|prizes?\s*worth|awards?)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+)', text, re.I)
        if prize_m:
            metadata['prizes'] = f"Cash Prizes: ₹{prize_m.group(1)}"
        else:
            metadata['prizes'] = "Prizes & Recognition"
    else:
        metadata['prizes'] = None

    # 9. Mode (Offline / Online)
    if any(m in text.lower() for m in ['google meet', 'zoom.us', 'meet.google.com', 'online webinar', 'virtual session', 'teams meeting']):
        metadata['mode'] = "Online / Virtual"
    else:
        metadata['mode'] = "On-Campus (Offline)"

    # 10. Stalls & Highlights (e.g. Udyama stall numbers, special features)
    stall_m = re.search(r'(?:Stall\s*(?:No\.?\s*)?\d+[^\n\r•]*)', text, re.I)
    if stall_m:
        metadata['stall_info'] = stall_m.group(0).strip()

    # Look for bullet points with food or agenda highlights
    highlights = []
    for line in text.splitlines():
        line_s = line.strip()
        if (line_s.startswith(('•', '-', '*', '✓', '👉')) or 'biryani' in line_s.lower() or 'stall' in line_s.lower()) and 5 < len(line_s) < 80:
            clean_item = re.sub(r'^[•\-\*✓👉\s]+', '', line_s).strip()
            if clean_item and clean_item not in highlights:
                highlights.append(clean_item)
    metadata['highlights'] = highlights[:4]

    return metadata

def calculate_event_expiration(start_date_str, end_date_str=None, reference_today=None):
    """
    Calculates whether an event is expired or active, and computes a human-readable countdown.
    """
    today = (reference_today or datetime.now()).date()
    today_iso = today.isoformat()

    s_date = None
    e_date = None

    try:
        if start_date_str:
            s_date = datetime.fromisoformat(start_date_str).date()
    except Exception:
        pass

    try:
        if end_date_str:
            e_date = datetime.fromisoformat(end_date_str).date()
    except Exception:
        pass

    effective_end = e_date or s_date or today
    effective_start = s_date or today

    is_expired = effective_end < today

    if is_expired:
        days_ago = (today - effective_end).days
        status = "Completed"
        if days_ago == 1:
            countdown_text = "Completed yesterday"
        else:
            countdown_text = f"Completed {days_ago} days ago"
    elif effective_start <= today <= effective_end:
        status = "Happening Today!"
        countdown_text = "🔥 Happening Today!"
    else:
        days_ahead = (effective_start - today).days
        if days_ahead == 1:
            status = "Tomorrow"
            countdown_text = "⚡ Tomorrow"
        elif days_ahead <= 7:
            status = "This Week"
            countdown_text = f"In {days_ahead} days"
        elif days_ahead <= 14:
            status = "Next Week"
            countdown_text = "Next week"
        else:
            status = "Upcoming"
            countdown_text = f"In {days_ahead} days"

    return {
        'is_expired': is_expired,
        'status': status,
        'countdown_text': countdown_text
    }

def analyze_email_for_event(email_item):
    """
    Performs rich NLP analysis on an email item to determine if it is an event,
    and extracts structured event entities (date, time, venue, organizer, links, metadata).
    """
    subject = email_item.get('subject', '')
    body = email_item.get('body', '')
    sender = email_item.get('sender', '')
    full_text = f"{subject}\n{body}"
    text_lower = full_text.lower()

    # Filter out obvious administrative/account security spam
    for pat in EXCLUDE_SUBJECT_PATTERNS:
        if re.search(pat, subject, re.I):
            return {
                'is_event': False,
                'confidence_score': 0,
                'title': clean_subject(subject),
                'email_subject': subject,
                'email_sender': sender,
                'email_date': email_item.get('date_header', ''),
                'snippet': email_item.get('snippet', '')
            }

    # Reference date from email
    ref_dt = datetime.now()
    if 'timestamp' in email_item:
        try:
            ref_dt = datetime.fromisoformat(email_item['timestamp'])
        except Exception:
            pass

    # Extract entities
    dates = extract_dates_from_text(full_text, reference_date=ref_dt)
    times = extract_times_from_text(full_text)
    venues = extract_venues_from_text(full_text)
    meta = extract_rich_metadata_from_text(full_text)

    # Event indicator keywords
    event_keywords = [
        'event', 'fest', 'fair', 'competition', 'workshop', 'seminar', 'webinar',
        'lecture', 'meeting', 'celebration', 'tournament', 'session', 'registration',
        'venue', 'auditorium', 'hall', 'audi', 'stall', 'udyama', 'sangamotsav',
        'rangotsav', 'technovanza', 'quiz', 'hackathon', 'symposium', 'conference',
        'chief guest', 'inauguration', 'valedictory', 'exhibition', 'flea market',
        'holy mass', 'mass tomorrow', 'discord community', 'hackfront'
    ]

    event_score = 0
    for kw in event_keywords:
        if kw in text_lower:
            event_score += 1

    if dates:
        event_score += 2
    if times:
        event_score += 2
    if venues:
        event_score += 2
    if meta['registration_link'] or meta['whatsapp_link']:
        event_score += 2
    if meta['stall_info']:
        event_score += 2

    # Sender credibility boost (from college accounts/clubs)
    if any(cl in sender.lower() for cl in ['caias.in', 'club', 'department', 'library', 'iqac', 'nss', 'council']):
        event_score += 2

    is_event = event_score >= 3 or ('venue' in text_lower and dates) or ('udyama' in text_lower)

    title = clean_subject(subject)
    quote_match = re.search(r'["“]([^"”]+)["”]', subject)
    if quote_match and len(quote_match.group(1)) > 4:
        sub_title = quote_match.group(1)
    else:
        star_match = re.search(r'\*([A-Za-z0-9\s–\-]{4,35})\*', body)
        sub_title = star_match.group(1) if star_match else title

    primary_date = dates[0]['parsed_iso'] if dates else ref_dt.date().isoformat()
    primary_date_fmt = dates[0]['formatted'] if dates else ref_dt.strftime('%d %b %Y')
    primary_venue = venues[0] if venues else 'Campus / To Be Announced'
    primary_time = times[0] if times else 'Refer to announcement'

    exp_info = calculate_event_expiration(primary_date, primary_date)

    return {
        'is_event': is_event,
        'confidence_score': min(event_score * 10, 100),
        'title': title,
        'highlight_title': sub_title,
        'primary_date': primary_date,
        'formatted_date': primary_date_fmt,
        'is_expired': exp_info['is_expired'],
        'status': exp_info['status'],
        'countdown_text': exp_info['countdown_text'],
        'venue': primary_venue,
        'time': primary_time,
        'all_dates': dates,
        'all_times': times,
        'all_venues': venues,
        'registration_link': meta['registration_link'],
        'whatsapp_link': meta['whatsapp_link'],
        'meeting_link': meta['meeting_link'],
        'all_links': meta['all_links'],
        'deadline': meta['deadline'],
        'contact_numbers': meta['contact_numbers'],
        'coordinators': meta['coordinators'],
        'eligibility': meta['eligibility'],
        'fee': meta['fee'],
        'certificate': meta['certificate'],
        'attendance': meta['attendance'],
        'prizes': meta['prizes'],
        'mode': meta['mode'],
        'highlights': meta['highlights'],
        'stall_info': meta['stall_info'],
        'organizer': sender,
        'raw_email_id': email_item.get('id'),
        'email_subject': subject,
        'email_sender': sender,
        'email_date': email_item.get('date_header', ''),
        'snippet': email_item.get('snippet', '')
    }

def match_and_augment_events(calendar_events, analyzed_emails):
    """
    Correlates analyzed email events with the Academic Calendar events.
    Enriches calendar events with live email venue/time, and adds standalone email events.
    Applies expiration calculation to all events.
    """
    augmented_calendar = []
    matched_email_ids = set()

    for cal_ev in calendar_events:
        item = dict(cal_ev)
        cal_title = item.get('title', '').lower()
        cal_dept = item.get('department', '').lower()
        cal_date = item.get('start_date', '')

        # Calculate expiration for calendar event
        exp_info = calculate_event_expiration(item.get('start_date'), item.get('end_date'))
        item['is_expired'] = exp_info['is_expired']
        item['status'] = exp_info['status']
        item['countdown_text'] = exp_info['countdown_text']

        # Search for matching emails
        best_match = None
        best_score = 0

        for em in analyzed_emails:
            if not em.get('is_event'):
                continue

            em_text = f"{em.get('email_subject', '')} {em.get('highlight_title', '')} {em.get('snippet', '')}".lower()
            keyword_score = 0
            cal_words = [w for w in re.findall(r'[a-z]{4,}', cal_title) if w not in {'general', 'staff', 'meeting', 'club', 'activity'}]
            
            if cal_words:
                matched_words = [w for w in cal_words if w in em_text]
                if matched_words:
                    keyword_score += len(matched_words) * 3

            if cal_dept in em_text or (cal_dept == 'commerce' and 'commerce' in em_text) or (cal_dept == 'management' and 'management' in em_text):
                keyword_score += 2

            if em.get('primary_date') == cal_date:
                keyword_score += 5

            if keyword_score > best_score and keyword_score >= 4:
                best_score = keyword_score
                best_match = em

        if best_match:
            item['has_email_update'] = True
            item['venue'] = best_match['venue'] if best_match['venue'] != 'Campus / To Be Announced' else item.get('venue', 'Campus')
            item['time'] = best_match['time'] if best_match['time'] != 'Refer to announcement' else item.get('time', 'TBD')
            item['registration_link'] = best_match.get('registration_link')
            item['whatsapp_link'] = best_match.get('whatsapp_link')
            item['deadline'] = best_match.get('deadline')
            item['eligibility'] = best_match.get('eligibility')
            item['contact_numbers'] = best_match.get('contact_numbers')
            item['highlights'] = best_match.get('highlights')
            item['stall_info'] = best_match.get('stall_info')
            item['certificate'] = best_match.get('certificate')
            item['fee'] = best_match.get('fee')
            item['attendance'] = best_match.get('attendance')
            item['prizes'] = best_match.get('prizes')
            item['mode'] = best_match.get('mode')
            item['live_update_notes'] = f"Updated via recent email: {best_match['email_subject']}"
            item['email_data'] = {
                'subject': best_match['email_subject'],
                'sender': best_match['email_sender'],
                'date': best_match['email_date'],
                'snippet': best_match['snippet'],
                'extracted_venue': best_match['venue'],
                'extracted_time': best_match['time'],
                'registration_link': best_match.get('registration_link'),
                'whatsapp_link': best_match.get('whatsapp_link'),
                'deadline': best_match.get('deadline'),
                'eligibility': best_match.get('eligibility'),
                'contact_numbers': best_match.get('contact_numbers'),
                'highlights': best_match.get('highlights', []),
                'stall_info': best_match.get('stall_info'),
                'certificate': best_match.get('certificate'),
                'fee': best_match.get('fee'),
                'attendance': best_match.get('attendance'),
                'prizes': best_match.get('prizes'),
                'mode': best_match.get('mode'),
                'links': best_match.get('all_links', best_match.get('links', []))
            }
            matched_email_ids.add(best_match['raw_email_id'])

        augmented_calendar.append(item)

    # Standalone email events not found on calendar
    standalone_events = []
    for em in analyzed_emails:
        if em.get('is_event') and em.get('raw_email_id') not in matched_email_ids:
            exp_info = calculate_event_expiration(em.get('primary_date'), em.get('primary_date'))
            standalone_events.append({
                'id': f"email_announcement_{em.get('raw_email_id')}",
                'source': 'email_live',
                'is_standalone_email': True,
                'department': em.get('organizer', 'Campus Announcement'),
                'start_date': em.get('primary_date'),
                'end_date': em.get('primary_date'),
                'day': datetime.fromisoformat(em.get('primary_date')).strftime('%A') if em.get('primary_date') else 'Upcoming',
                'title': em.get('title'),
                'source_page': 'Live Gmail Notice',
                'is_holiday': False,
                'is_expired': exp_info['is_expired'],
                'status': exp_info['status'],
                'countdown_text': exp_info['countdown_text'],
                'venue': em.get('venue'),
                'time': em.get('time'),
                'registration_link': em.get('registration_link'),
                'whatsapp_link': em.get('whatsapp_link'),
                'meeting_link': em.get('meeting_link'),
                'deadline': em.get('deadline'),
                'eligibility': em.get('eligibility'),
                'contact_numbers': em.get('contact_numbers'),
                'highlights': em.get('highlights'),
                'stall_info': em.get('stall_info'),
                'fee': em.get('fee'),
                'certificate': em.get('certificate'),
                'attendance': em.get('attendance'),
                'prizes': em.get('prizes'),
                'mode': em.get('mode'),
                'has_email_update': True,
                'email_data': {
                    'subject': em.get('email_subject'),
                    'sender': em.get('email_sender'),
                    'date': em.get('email_date'),
                    'snippet': em.get('snippet'),
                    'extracted_venue': em.get('venue'),
                    'extracted_time': em.get('time'),
                    'registration_link': em.get('registration_link'),
                    'whatsapp_link': em.get('whatsapp_link'),
                    'deadline': em.get('deadline'),
                    'eligibility': em.get('eligibility'),
                    'contact_numbers': em.get('contact_numbers'),
                    'highlights': em.get('highlights'),
                    'stall_info': em.get('stall_info'),
                    'fee': em.get('fee'),
                    'certificate': em.get('certificate'),
                    'attendance': em.get('attendance'),
                    'prizes': em.get('prizes'),
                    'mode': em.get('mode'),
                    'links': em.get('all_links', [])
                }
            })

    return augmented_calendar, standalone_events

def calculate_recommendations(events_list, user_interests, top_n=None, include_past=False, reference_today=None):
    """
    Computes personalized TF-IDF similarity match scores between user's chosen interests
    and events.
    """
    if not user_interests:
        user_interests = ['General Events']

    today_str = (reference_today or datetime.now()).date().isoformat()

    filtered_events = []
    for ev in events_list:
        if not include_past and ev.get('is_expired', False):
            continue
        filtered_events.append(dict(ev))

    if not filtered_events:
        return []

    # Build corpus
    event_texts = []
    for ev in filtered_events:
        txt = f"{ev.get('department', '')} {ev.get('title', '')} {ev.get('venue', '')}"
        if ev.get('stall_info'):
            txt += f" {ev['stall_info']}"
        if ev.get('highlights'):
            txt += f" {' '.join(ev['highlights'])}"
        if ev.get('has_email_update') and ev.get('email_data'):
            txt += f" {ev['email_data'].get('snippet', '')} {ev['email_data'].get('subject', '')}"
        event_texts.append(txt)

    profile_text = ' '.join(user_interests) + ' ' + ' '.join(t for interest in user_interests for t in INTEREST_TERMS.get(interest, []))
    corpus = event_texts + [profile_text]

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(matrix[:-1], matrix[-1]).ravel()

    lower_texts = [t.lower() for t in event_texts]
    for i, txt in enumerate(lower_texts):
        hits = sum(1 for interest in user_interests for term in INTEREST_TERMS.get(interest, []) if term in txt)
        scores[i] += min(hits * 0.05, 0.25)

    for i, ev in enumerate(filtered_events):
        score_val = float(scores[i])
        ev['match_score_raw'] = score_val
        ev['match_score'] = min(max(int(score_val * 100), 5), 99)

        matched_interests = []
        for interest in user_interests:
            terms = INTEREST_TERMS.get(interest, [])
            if any(term in lower_texts[i] for term in terms) or interest.lower() in lower_texts[i]:
                matched_interests.append(interest)

        if matched_interests:
            ev['why_recommended'] = f"Matches: {', '.join(matched_interests[:3])}"
        else:
            ev['why_recommended'] = "Relevant to selected student interests"

    # Sort by match score and then by start date
    filtered_events.sort(key=lambda x: (-x['match_score_raw'], x.get('start_date', '9999-99-99')))

    if top_n:
        return filtered_events[:top_n]
    return filtered_events
