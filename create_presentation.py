import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    C_BG_DARK = RGBColor(11, 19, 43)       # #0B132B Dark Navy
    C_PRIMARY = RGBColor(30, 58, 138)      # #1E3A8A Deep Blue
    C_ROYAL = RGBColor(37, 99, 235)        # #2563EB Royal Blue
    C_ACCENT = RGBColor(217, 119, 6)       # #D97706 Amber/Gold
    C_EMERALD = RGBColor(5, 150, 105)      # #059669 Green
    C_CARD_BG = RGBColor(255, 255, 255)    # White
    C_CARD_LIGHT = RGBColor(241, 245, 249) # #F1F5F9 Slate Light
    C_CARD_BLUE = RGBColor(239, 246, 255)  # #EFF6FF Ice Blue
    C_TEXT_DARK = RGBColor(15, 23, 42)     # #0F172A
    C_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    C_WHITE = RGBColor(255, 255, 255)
    C_BORDER = RGBColor(203, 213, 225)     # #CBD5E1

    def add_header(slide, title_text, category_text="CAIAS AI EVENT ASSISTANT • AI & ML PROJECT"):
        # Header background banner
        header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = C_PRIMARY
        header_box.line.color.rgb = C_PRIMARY

        # Category / Tagline small text
        tf = header_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        tf.margin_left = Inches(0.8)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.1)

        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Segoe UI"
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = RGBColor(254, 243, 199) # Gold

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Segoe UI Semibold"
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = C_WHITE

        # Accent horizontal strip
        accent_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        accent_strip.fill.solid()
        accent_strip.fill.fore_color.rgb = C_ACCENT
        accent_strip.line.fill.background()

    def add_footer(slide, current_slide, total_slides=9):
        # Footer text
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
        tf = footer_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = f"Christ Academy Institute for Advanced Studies (CAIAS) • Department of Computer Applications (BCA) • Slide {current_slide} of {total_slides}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE (Hero Dark Background)
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_BG_DARK
    bg1.line.fill.background()

    # Top Pill Badge
    pill = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(4.6), Inches(0.42))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(30, 41, 59)
    pill.line.color.rgb = C_ROYAL
    pill.line.width = Pt(1.5)
    tf_pill = pill.text_frame
    tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_pill = tf_pill.paragraphs[0]
    p_pill.text = "⚡ CAPSTONE PROJECT • SUBJECT: AI & ML"
    p_pill.font.name = "Segoe UI"
    p_pill.font.size = Pt(10)
    p_pill.font.bold = True
    p_pill.font.color.rgb = RGBColor(147, 197, 253)

    # Title Text Box
    title_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(2.2))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p1 = tf_title.paragraphs[0]
    p1.text = "CAIAS AI EVENT ASSISTANT"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf_title.add_paragraph()
    p2.text = "“Intelligent Campus Event Discovery, Academic Calendar NLP Extraction & Automated Real-time Gmail Synchronization System”"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(254, 243, 199) # Gold tint
    p2.space_before = Pt(8)

    # Presenter Card 1 (N Chaitanya)
    card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.9), Inches(5.6), Inches(1.8))
    card1.fill.solid()
    card1.fill.fore_color.rgb = RGBColor(15, 23, 42)
    card1.line.color.rgb = C_ROYAL
    card1.line.width = Pt(1.5)
    tf1 = card1.text_frame
    tf1.margin_left = Inches(0.3)
    tf1.margin_top = Inches(0.2)
    p_c1_t = tf1.paragraphs[0]
    p_c1_t.text = "N Chaitanya"
    p_c1_t.font.name = "Segoe UI"
    p_c1_t.font.size = Pt(18)
    p_c1_t.font.bold = True
    p_c1_t.font.color.rgb = C_WHITE

    p_c1_d = tf1.add_paragraph()
    p_c1_d.text = "Register No: 25bca090\nBachelor of Computer Applications (BCA)\nSpecialization: Artificial Intelligence & Machine Learning"
    p_c1_d.font.name = "Segoe UI"
    p_c1_d.font.size = Pt(11)
    p_c1_d.font.color.rgb = RGBColor(203, 213, 225)
    p_c1_d.space_before = Pt(4)

    # Presenter Card 2 (Delin Rajesh)
    card2 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.9), Inches(5.6), Inches(1.8))
    card2.fill.solid()
    card2.fill.fore_color.rgb = RGBColor(15, 23, 42)
    card2.line.color.rgb = C_ROYAL
    card2.line.width = Pt(1.5)
    tf2 = card2.text_frame
    tf2.margin_left = Inches(0.3)
    tf2.margin_top = Inches(0.2)
    p_c2_t = tf2.paragraphs[0]
    p_c2_t.text = "Delin Rajesh"
    p_c2_t.font.name = "Segoe UI"
    p_c2_t.font.size = Pt(18)
    p_c2_t.font.bold = True
    p_c2_t.font.color.rgb = C_WHITE

    p_c2_d = tf2.add_paragraph()
    p_c2_d.text = "Register No: 25bca072\nBachelor of Computer Applications (BCA)\nSpecialization: Artificial Intelligence & Machine Learning"
    p_c2_d.font.name = "Segoe UI"
    p_c2_d.font.size = Pt(11)
    p_c2_d.font.color.rgb = RGBColor(203, 213, 225)
    p_c2_d.space_before = Pt(4)

    # Institution Bar at Bottom
    inst_box = slide1.shapes.add_textbox(Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.8))
    tf_inst = inst_box.text_frame
    p_inst = tf_inst.paragraphs[0]
    p_inst.text = "Christ Academy Institute for Advanced Studies (CAIAS) • Bengaluru, Karnataka\nDepartment of Computer Applications • Academic Year 2026–2027"
    p_inst.font.name = "Segoe UI"
    p_inst.font.size = Pt(11)
    p_inst.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 2: THE PROBLEM STATEMENT (Why We Built This)
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "The Problem Statement: Campus Information Fragmentation")
    add_footer(slide2, 2)

    # Left Card: Static Calendar Limitation
    p_box1 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(3.8))
    p_box1.fill.solid()
    p_box1.fill.fore_color.rgb = C_CARD_LIGHT
    p_box1.line.color.rgb = C_BORDER
    p_box1.line.width = Pt(1)
    tf_b1 = p_box1.text_frame
    tf_b1.margin_left = Inches(0.35)
    tf_b1.margin_right = Inches(0.35)
    tf_b1.margin_top = Inches(0.3)

    p = tf_b1.paragraphs[0]
    p.text = "📄 The Static 38-Page Calendar (COE)"
    p.font.name = "Segoe UI Semibold"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    bullets1 = [
        "480+ scheduled milestones buried in a monolithic PDF document.",
        "Zero real-time awareness: Does not reflect date changes, cancellations, or room reassignments.",
        "No interactive links: Registration forms, WhatsApp groups, and speaker profiles cannot be embedded in a PDF.",
        "Departmental silos: Students rarely scroll past their own course pages to discover inter-disciplinary events."
    ]
    for b in bullets1:
        pb = tf_b1.add_paragraph()
        pb.text = "• " + b
        pb.font.name = "Segoe UI"
        pb.font.size = Pt(10.5)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_before = Pt(8)

    # Right Card: The Flooded Email Inbox
    p_box2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.6), Inches(3.8))
    p_box2.fill.solid()
    p_box2.fill.fore_color.rgb = C_CARD_LIGHT
    p_box2.line.color.rgb = C_BORDER
    p_box2.line.width = Pt(1)
    tf_b2 = p_box2.text_frame
    tf_b2.margin_left = Inches(0.35)
    tf_b2.margin_right = Inches(0.35)
    tf_b2.margin_top = Inches(0.3)

    p = tf_b2.paragraphs[0]
    p.text = "📧 The Daily Flooded Gmail Inbox"
    p.font.name = "Segoe UI Semibold"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT

    bullets2 = [
        "Students receive 15–35 emails daily from administrative cells, clubs, and circulars.",
        "Buried registration deadlines: Critical workshop dates and Google Form links get lost in endless threads.",
        "Unstructured raw text: Dates, times, and entry fees are formatted haphazardly without standardization.",
        "No personalization: Every student receives all mass emails regardless of whether they code, paint, or debate."
    ]
    for b in bullets2:
        pb = tf_b2.add_paragraph()
        pb.text = "• " + b
        pb.font.name = "Segoe UI"
        pb.font.size = Pt(10.5)
        pb.font.color.rgb = C_TEXT_DARK
        pb.space_before = Pt(8)

    # Bottom Summary Callout
    callout2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.5), Inches(11.6), Inches(1.3))
    callout2.fill.solid()
    callout2.fill.fore_color.rgb = C_CARD_BLUE
    callout2.line.color.rgb = C_ROYAL
    callout2.line.width = Pt(1.5)
    tf_c2 = callout2.text_frame
    tf_c2.margin_left = Inches(0.3)
    tf_c2.margin_top = Inches(0.18)
    p_c2_t = tf_c2.paragraphs[0]
    p_c2_t.text = "🎯 The Solution & Engineering Mission"
    p_c2_t.font.name = "Segoe UI Semibold"
    p_c2_t.font.size = Pt(13)
    p_c2_t.font.bold = True
    p_c2_t.font.color.rgb = C_ROYAL

    p_c2_b = tf_c2.add_paragraph()
    p_c2_b.text = "Build an autonomous AI-driven assistant that extracts the baseline calendar, continuously ingests real-time Gmail notices, uses NLP to extract all logistical metadata (venues, times, forms, perks), and delivers a personalized, lightning-fast dashboard to students."
    p_c2_b.font.name = "Segoe UI"
    p_c2_b.font.size = Pt(10.5)
    p_c2_b.font.color.rgb = C_TEXT_DARK
    p_c2_b.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 3: PROJECT OBJECTIVES & DELIVERABLES
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Core Objectives & Measurable Engineering Goals")
    add_footer(slide3, 3)

    pillars = [
        ("1. PDF Digitization", "Automate extraction of 480 events from the 38-page CAIAS COE PDF with zero manual data entry, categorized by department and date.", C_PRIMARY),
        ("2. Real-Time Gmail Sync", "Authenticate via Google OAuth 2.0 with offline refresh token rotation to ingest official circulars and notices dynamically every 30 minutes.", C_ROYAL),
        ("3. NLP Entity Extractor", "Extract unstructured entities: Venues, Timings, Google Form registration URLs, WhatsApp groups, Deadlines, Entry Fees, and Duty Leave credits.", C_ACCENT),
        ("4. Strict 1-to-1 Matcher", "Correlate email updates to calendar rows using token deduplication and date proximity, guaranteeing zero false data leakage between events.", C_EMERALD),
        ("5. ML Recommender", "Personalize event discovery using Scikit-Learn TF-IDF Vectorization and Cosine Similarity to compute a 0–99% Match Score per student profile.", C_PRIMARY),
        ("6. Sub-10ms UI Performance", "Implement Two-Tier LocalStorage Caching to bypass serverless cold starts on Vercel, enabling instant page rendering within 10 milliseconds.", C_ROYAL)
    ]

    card_w = Inches(3.65)
    card_h = Inches(2.55)
    xs = [Inches(0.8), Inches(4.8), Inches(8.8)]
    ys = [Inches(1.5), Inches(4.3)]

    for idx, (title, desc, accent_color) in enumerate(pillars):
        r = idx // 3
        c = idx % 3
        box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[c], ys[r], card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD_LIGHT
        box.line.color.rgb = C_BORDER
        box.line.width = Pt(1)

        # Top accent bar on each card
        bar = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, xs[c], ys[r], card_w, Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_color
        bar.line.fill.background()

        tf = box.text_frame
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Segoe UI Semibold"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = "Segoe UI"
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = C_TEXT_DARK
        p_desc.space_before = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 4: END-TO-END SYSTEM WORKFLOW (The Pipeline Diagram)
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "End-to-End System Workflow & Architecture")
    add_footer(slide4, 4)

    stages = [
        ("STAGE 1", "Dual-Source Ingestion", [
            "CAIAS COE PDF (480 events parsed via PyMuPDF)",
            "Institutional Gmail API v1 (Live circulars fetched)",
            "OAuth 2.0 offline token refresh rotation"
        ], C_PRIMARY),
        ("STAGE 2", "Applied NLP Extraction", [
            "RegEx Named Entity Recognition (NER)",
            "Venues, Times & Registration Form links",
            "Fee detector, Certification & Attendance flags",
            "Period sanitizer (SG. Canisius -> St. Peter Canisius)"
        ], C_ROYAL),
        ("STAGE 3", "Strict 1-to-1 Matcher", [
            "Token Set Intersections (Strips generic words)",
            "Date proximity evaluation (+/- 7 days bonus)",
            "1-to-1 Locking: Matched emails never repeat",
            "Standalone generation for new live notices"
        ], C_ACCENT),
        ("STAGE 4", "Delivery & Caching", [
            "TF-IDF Personalized Match Scoring (0-99%)",
            "FastAPI async REST endpoints (/api/events)",
            "Sub-10ms LocalStorage SWR cache restoration",
            "One-click Google Calendar & .ics export"
        ], C_EMERALD)
    ]

    pipe_w = Inches(2.7)
    pipe_h = Inches(4.8)
    pipe_xs = [Inches(0.8), Inches(3.75), Inches(6.7), Inches(9.65)]

    for idx, (stage_num, stage_title, bullets, color) in enumerate(stages):
        box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pipe_xs[idx], Inches(1.6), pipe_w, pipe_h)
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD_LIGHT
        box.line.color.rgb = color
        box.line.width = Pt(1.5)

        # Header block on card
        top_h = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, pipe_xs[idx], Inches(1.6), pipe_w, Inches(0.85))
        top_h.fill.solid()
        top_h.fill.fore_color.rgb = color
        top_h.line.fill.background()

        tf_th = top_h.text_frame
        tf_th.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_sn = tf_th.paragraphs[0]
        p_sn.text = stage_num
        p_sn.alignment = PP_ALIGN.CENTER
        p_sn.font.name = "Segoe UI"
        p_sn.font.size = Pt(9.5)
        p_sn.font.bold = True
        p_sn.font.color.rgb = RGBColor(254, 243, 199)

        p_st = tf_th.add_paragraph()
        p_st.text = stage_title
        p_st.alignment = PP_ALIGN.CENTER
        p_st.font.name = "Segoe UI Semibold"
        p_st.font.size = Pt(11.5)
        p_st.font.bold = True
        p_st.font.color.rgb = C_WHITE

        # Content
        tf = box.text_frame
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(1.05)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = "• " + b
            pb.font.name = "Segoe UI"
            pb.font.size = Pt(9.5)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_before = Pt(8)

        # Arrow connector between stages
        if idx < 3:
            arrow = slide4.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, pipe_xs[idx] + pipe_w + Inches(0.06), Inches(3.8), Inches(0.18), Inches(0.35))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = C_ROYAL
            arrow.line.fill.background()

    # Bottom workflow text
    bot_info = slide4.shapes.add_textbox(Inches(0.8), Inches(6.55), Inches(11.6), Inches(0.4))
    tf_bi = bot_info.text_frame
    p_bi = tf_bi.paragraphs[0]
    p_bi.alignment = PP_ALIGN.CENTER
    p_bi.text = "🔄 Fully automated continuous background cycle: syncs every 30 minutes via GitHub Actions & Vercel serverless crons"
    p_bi.font.name = "Segoe UI"
    p_bi.font.size = Pt(10)
    p_bi.font.bold = True
    p_bi.font.color.rgb = C_PRIMARY

    # -------------------------------------------------------------
    # SLIDE 5: APPLIED MACHINE LEARNING & NLP ENGINE
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Machine Learning Recommender & Applied NLP Pipeline")
    add_footer(slide5, 5)

    # Box 1: TF-IDF & Cosine Similarity
    b_ml = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    b_ml.fill.solid()
    b_ml.fill.fore_color.rgb = C_CARD_LIGHT
    b_ml.line.color.rgb = C_ROYAL
    b_ml.line.width = Pt(1.5)

    tf_ml = b_ml.text_frame
    tf_ml.margin_left = Inches(0.35)
    tf_ml.margin_right = Inches(0.35)
    tf_ml.margin_top = Inches(0.25)

    p = tf_ml.paragraphs[0]
    p.text = "🤖 TF-IDF & Cosine Similarity Engine"
    p.font.name = "Segoe UI Semibold"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    ml_points = [
        ("Mathematical Text Vectorization", "Converts student interest preferences and event text into sparse TF-IDF vectors using Scikit-Learn's TfidfVectorizer (N-grams 1-2)."),
        ("Personalized Match Scoring", "Calculates the cosine angle between user vectors and event vectors to assign an intuitive match percentage (5% to 99%)."),
        ("Dynamic Why-Recommended Badges", "Explains exactly why an event was recommended (e.g., 'Matches: Artificial Intelligence, Coding, Hackathons')."),
        ("Why Not an LLM API?", "Executes in < 5 milliseconds with zero API costs, zero token limits, and deterministic output. An external LLM would add 1-2s latency per user query.")
    ]
    for title, desc in ml_points:
        p_t = tf_ml.add_paragraph()
        p_t.text = "▶ " + title
        p_t.font.name = "Segoe UI Semibold"
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_ROYAL
        p_t.space_before = Pt(8)

        p_d = tf_ml.add_paragraph()
        p_d.text = desc
        p_d.font.name = "Segoe UI"
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_DARK

    # Box 2: Applied NLP & Entity Recognition
    b_nlp = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.2))
    b_nlp.fill.solid()
    b_nlp.fill.fore_color.rgb = C_CARD_LIGHT
    b_nlp.line.color.rgb = C_ACCENT
    b_nlp.line.width = Pt(1.5)

    tf_nlp = b_nlp.text_frame
    tf_nlp.margin_left = Inches(0.35)
    tf_nlp.margin_right = Inches(0.35)
    tf_nlp.margin_top = Inches(0.25)

    p = tf_nlp.paragraphs[0]
    p.text = "🔍 RegEx Named Entity Recognition (NER)"
    p.font.name = "Segoe UI Semibold"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT

    nlp_points = [
        ("Venues & Room Locations", "Extracts explicit location strings and common campus landmarks (Canisius Hall, Main Audi, Amphitheatre, Lab 3)."),
        ("Classified Link Harvester", "Separates registration Google Forms (forms.gle) from WhatsApp community groups (chat.whatsapp.com) and virtual meets."),
        ("Event Perks & Logistics", "Extracts Entry Fees (Free vs. Paid ₹), Participation Certificates, Attendance Credits, and Sangam Cup / Cash Prizes."),
        ("Deadlines & Timings", "Captures registration cut-off dates and session timings (e.g., '9:00 AM - 10:00 AM', '11:59 PM').")
    ]
    for title, desc in nlp_points:
        p_t = tf_nlp.add_paragraph()
        p_t.text = "▶ " + title
        p_t.font.name = "Segoe UI Semibold"
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_ACCENT
        p_t.space_before = Pt(8)

        p_d = tf_nlp.add_paragraph()
        p_d.text = desc
        p_d.font.name = "Segoe UI"
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_DARK

    # -------------------------------------------------------------
    # SLIDE 6: TECHNICAL BREAKTHROUGHS & PROBLEM SOLVING
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Key Technical Breakthroughs & Engineering Fixes")
    add_footer(slide6, 6)

    breakthroughs = [
        ("1. Zero Data Leakage via Strict 1-to-1 Match Locking",
         "The Challenge: In early tests, generic words like 'workshop' or repeated tokens like 'India' caused one email notice (Smart Robotics) to match dozens of unrelated calendar events.\n\n"
         "The Engineering Solution:\n"
         "• Stop-Word Filtering: Stripped generic tokens ('workshop', 'program', 'management', 'science').\n"
         "• Token Set Intersections: Titles converted to unique sets, eliminating score inflation from repeated words.\n"
         "• 1-to-1 Match Constraint: Once matched, an email ID is permanently locked in matched_email_ids.\n"
         "• Standalone Notices: Unmatched emails become dedicated standalone event cards.",
         C_PRIMARY),
        ("2. Robust Venue Extraction & Period Normalization",
         "The Challenge: Email circulars frequently contained markdown asterisks and abbreviation periods (e.g., '*Venue:* SG. Canisius Hall'). Standard RegEx broke on the period, cutting the venue to '* SG'.\n\n"
         "The Engineering Solution:\n"
         "• Markdown Stripping: Pre-cleans all asterisks (*), underscores (_), and tildes (~).\n"
         "• Period Lookahead: Prevents breaking on abbreviations like 'St.' or 'SG.'.\n"
         "• Canonical Resolution: Automatically resolves colloquial campus names to formal locations ('St. Peter Canisius Hall (SG Hall)').",
         C_ROYAL),
        ("3. Sub-10ms Instant Load via LocalStorage Caching",
         "The Challenge: Serverless functions on Vercel suffer from cold-start latency (1-2.5 seconds), causing blank screens or loading spinners.\n\n"
         "The Engineering Solution:\n"
         "• Stale-While-Revalidate (SWR): On DOM load, restoreFromLocalStorage() reads caias_events_cache and renders cards in < 10ms.\n"
         "• Background Revalidation: Silently fetches fresh updates from /api/events and updates the cache.\n"
         "• Offline Persistence: Viewing details saves the event offline under caias_event_<id>.",
         C_EMERALD)
    ]

    col_w = Inches(3.65)
    col_h = Inches(5.2)
    col_xs = [Inches(0.8), Inches(4.8), Inches(8.8)]

    for idx, (title, content, color) in enumerate(breakthroughs):
        box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_xs[idx], Inches(1.5), col_w, col_h)
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD_LIGHT
        box.line.color.rgb = color
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Segoe UI Semibold"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = color

        p_c = tf.add_paragraph()
        p_c.text = content
        p_c.font.name = "Segoe UI"
        p_c.font.size = Pt(9.5)
        p_c.font.color.rgb = C_TEXT_DARK
        p_c.space_before = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 7: USER INTERFACE & FEATURE SHOWCASE
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "UI Dashboard Features & User Experience")
    add_footer(slide7, 7)

    features = [
        ("Smart Glassmorphism Event Cards", [
            "Dynamic Countdown Badges: '🔥 Today', '⚡ Tomorrow', 'In 4 days', or 'Completed'.",
            "Departmental Color Coding: General, Science, Management, IQAC, Commerce.",
            "Verified Badges: '⚡ Email Update' vs. '📢 New Notice' (Standalone).",
            "Personalized Match Score: Color-coded recommendation pill (e.g., '84% Match')."
        ]),
        ("Interactive Deep Metadata Modal", [
            "Full event schedule, exact room / venue, and primary organizer.",
            "Visual perk tags: Entry Fee (Free Entry), Certification, and Duty Leave Attendance.",
            "Direct 1-click Google Form Registration button and WhatsApp Group join link.",
            "Quoted email snippet preview showing the exact Gmail announcement text."
        ]),
        ("Personal Saved Events & Offline Bookmarks", [
            "Star (⭐) Bookmark System: Save events with one click directly from card headers.",
            "Dedicated 'Saved Events' Tab: Direct top-level navigation tab with live badge counter.",
            "Offline Persistence: Saved events and modal metadata stored in browser localStorage.",
            "Works across sessions: Bookmarks remain saved permanently without requiring account login."
        ]),
        ("Calendar Export, Sharing & Real-Time Sync", [
            "One-Click Google Calendar Web URL generation with pre-filled title, dates, and venue.",
            "Native iCalendar (.ics) export for Apple Calendar, Outlook, and mobile devices.",
            "Live 30-minute auto-sync countdown timer and one-click 'Sync Now' button.",
            "NLP Inspector Tab: Live entity inspection (0-100% confidence scores) on all circulars."
        ])
    ]

    card_w7 = Inches(5.6)
    card_h7 = Inches(2.45)
    xs7 = [Inches(0.8), Inches(6.8)]
    ys7 = [Inches(1.5), Inches(4.2)]

    for idx, (title, items) in enumerate(features):
        r = idx // 2
        c = idx % 2
        box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs7[c], ys7[r], card_w7, card_h7)
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD_LIGHT
        box.line.color.rgb = C_BORDER
        box.line.width = Pt(1)

        tf = box.text_frame
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.2)

        p = tf.paragraphs[0]
        p.text = "✦ " + title
        p.font.name = "Segoe UI Semibold"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_PRIMARY

        for it in items:
            pb = tf.add_paragraph()
            pb.text = "• " + it
            pb.font.name = "Segoe UI"
            pb.font.size = Pt(9.5)
            pb.font.color.rgb = C_TEXT_DARK
            pb.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 8: FUTURE UPDATES & PROJECT ROADMAP
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Future Updates & Project Roadmap")
    add_footer(slide8, 8)

    roadmap = [
        ("Phase 1: Q1 2027", "WhatsApp Bot & SMS Push Alerts",
         "Integration with Twilio / WhatsApp Business API to dispatch automated event reminders, room changes, and registration deadlines directly to registered student phone numbers 24 hours in advance.",
         C_PRIMARY),
        ("Phase 2: Q2 2027", "LLM Conversational Q&A Agent",
         "Embedding a lightweight conversational model (Gemini Flash / Llama 3) allowing students to query in natural language (e.g., 'Are there any coding events happening this Friday with free entry?').",
         C_ROYAL),
        ("Phase 3: Q3 2027", "Digital RSVP & QR Attendance Passes",
         "Allowing club coordinators to track attendance directly through the assistant by issuing digital QR-code event passes to students upon clicking 'Register'.",
         C_ACCENT),
        ("Phase 4: 2027–28", "Cross-Platform Mobile App (React Native)",
         "Developing a dedicated companion mobile application featuring native home-screen calendar widgets and push notification channels.",
         C_EMERALD)
    ]

    r_w = Inches(11.6)
    r_h = Inches(1.15)
    r_ys = [Inches(1.5), Inches(2.8), Inches(4.1), Inches(5.4)]

    for idx, (phase, title, desc, col) in enumerate(roadmap):
        box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), r_ys[idx], r_w, r_h)
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD_LIGHT
        box.line.color.rgb = col
        box.line.width = Pt(1.2)

        # Left Accent Block
        lbl = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), r_ys[idx], Inches(2.2), r_h)
        lbl.fill.solid()
        lbl.fill.fore_color.rgb = col
        lbl.line.fill.background()
        tf_lbl = lbl.text_frame
        tf_lbl.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_lbl = tf_lbl.paragraphs[0]
        p_lbl.alignment = PP_ALIGN.CENTER
        p_lbl.text = phase
        p_lbl.font.name = "Segoe UI"
        p_lbl.font.size = Pt(11)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = C_WHITE

        # Description text
        tf_d = box.text_frame
        tf_d.margin_left = Inches(2.4)
        tf_d.margin_right = Inches(0.3)
        tf_d.margin_top = Inches(0.12)
        p_t = tf_d.paragraphs[0]
        p_t.text = title
        p_t.font.name = "Segoe UI Semibold"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = col

        p_desc = tf_d.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = "Segoe UI"
        p_desc.font.size = Pt(9.5)
        p_desc.font.color.rgb = C_TEXT_DARK
        p_desc.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 9: KEY ACHIEVEMENTS & CONCLUSION
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Summary of Achievements & Conclusion")
    add_footer(slide9, 9)

    stats = [
        ("480", "CALENDAR EVENTS PARSED", "100% extraction accuracy across all 38 pages of the CAIAS COE PDF.", C_PRIMARY),
        ("100%", "DATA LEAKAGE ELIMINATION", "Strict 1-to-1 matching and stop-word filtering prevents duplicate false notices.", C_ROYAL),
        ("< 10ms", "INSTANT UI LOAD TIME", "Client-side LocalStorage SWR caching completely eliminates Vercel cold starts.", C_ACCENT),
        ("30 MIN", "CONTINUOUS AUTO-SYNC", "Automated background sync refreshes OAuth tokens & pulls fresh Gmail notices.", C_EMERALD)
    ]

    stat_w = Inches(2.7)
    stat_h = Inches(2.6)
    stat_xs = [Inches(0.8), Inches(3.75), Inches(6.7), Inches(9.65)]

    for idx, (num, label, desc, col) in enumerate(stats):
        box = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, stat_xs[idx], Inches(1.5), stat_w, stat_h)
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD_BLUE
        box.line.color.rgb = col
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.3)

        p_num = tf.paragraphs[0]
        p_num.alignment = PP_ALIGN.CENTER
        p_num.text = num
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(36)
        p_num.font.bold = True
        p_num.font.color.rgb = col

        p_lbl = tf.add_paragraph()
        p_lbl.alignment = PP_ALIGN.CENTER
        p_lbl.text = label
        p_lbl.font.name = "Segoe UI"
        p_lbl.font.size = Pt(9.5)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = C_PRIMARY
        p_lbl.space_before = Pt(4)

        p_d = tf.add_paragraph()
        p_d.alignment = PP_ALIGN.CENTER
        p_d.text = desc
        p_d.font.name = "Segoe UI"
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_TEXT_DARK
        p_d.space_before = Pt(8)

    # Bottom Conclusion Banner
    conc_box = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.4), Inches(11.6), Inches(2.3))
    conc_box.fill.solid()
    conc_box.fill.fore_color.rgb = C_PRIMARY
    conc_box.line.color.rgb = C_ACCENT
    conc_box.line.width = Pt(1.5)

    tf_c = conc_box.text_frame
    tf_c.margin_left = Inches(0.4)
    tf_c.margin_right = Inches(0.4)
    tf_c.margin_top = Inches(0.25)

    p_ct = tf_c.paragraphs[0]
    p_ct.text = "🎓 Final Conclusion & Thank You"
    p_ct.font.name = "Segoe UI Semibold"
    p_ct.font.size = Pt(16)
    p_ct.font.bold = True
    p_ct.font.color.rgb = RGBColor(254, 243, 199)

    p_cb = tf_c.add_paragraph()
    p_cb.text = "The CAIAS AI Event Assistant demonstrates how applied Natural Language Processing, TF-IDF machine learning recommendation models, and asynchronous full-stack web engineering can modernize campus communication. By systematically transforming neglected calendar PDFs and cluttered inboxes into a personalized, self-updating hub, the system eliminates administrative friction and boosts student engagement."
    p_cb.font.name = "Segoe UI"
    p_cb.font.size = Pt(10.5)
    p_cb.font.color.rgb = C_WHITE
    p_cb.space_before = Pt(6)

    p_team = tf_c.add_paragraph()
    p_team.text = "Project By: N Chaitanya (25bca090) & Delin Rajesh (25bca072) • Department of Computer Applications, CAIAS • Questions & Answers"
    p_team.font.name = "Segoe UI"
    p_team.font.size = Pt(10)
    p_team.font.bold = True
    p_team.font.color.rgb = RGBColor(147, 197, 253)
    p_team.space_before = Pt(10)

    # Save presentation
    output_filename = "CAIAS_AI_Event_Assistant_Presentation.pptx"
    prs.save(output_filename)
    print(f"Presentation generated successfully: {output_filename}")

if __name__ == "__main__":
    build_presentation()

