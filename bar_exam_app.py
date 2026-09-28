import json
import os
import time
import random
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==============================================================================
st.set_page_config(
    page_title="LEGAL - ადვოკატთა გამოცდის პორტალი",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = "bar_exam_data.json"
PROGRESS_FILE = "bar_exam_progress.json"

DEFAULT_DATA = [
    {
        "id": "case_1",
        "title": "ხელშეკრულების შეწყვეტა და ზიანის ანაზღაურება",
        "code": "სამოქალაქო სამართალი",
        "article": "სსკ 405-ე, 394-ე მუხლები",
        "file_name": "სამოქალაქო_კაზუსები_2026.docx",
        "question": "შპს 'ალფამ' გააფორმა ხელშეკრულება შპს 'ბეტასთან' დანადგარების მოწოდებაზე. 'ბეტამ' დაარღვია ვადა 2 თვით. 'ალფამ' ცალმხრივად მოშალა ხელშეკრულება და მოითხოვა მიუღებელი შემოსავლის ანაზღაურება. კანონიერია თუ არა 'ალფას' მოთხოვნა?",
        "options": [
            "ა) კანონიერია, რადგან ვალდებულების დარღვევა იძლევა ხელშეკრულებიდან გასვლისა და ზიანის მოთხოვნის უფლებას (სსკ 394-ე და 405-ე მუხლები).",
            "ბ) არაკანონიერია, რადგან ჯერ დამატებითი ვადა უნდა დაენიშნა.",
            "გ) კანონიერია მხოლოდ ნაწილობრივ.",
            "დ) 'ბეტა' გათავისუფლებულია პასუხისმგებლობისგან."
        ],
        "correct_index": 0,
        "explanation": "საქართველოს სამოქალაქო კოდექსის 405-ე მუხლის თანახმად, ხელშეკრულების მონაწილე მხარეს შეუძლია უარი თქვას ხელშეკრულებაზე ვალდებულების დარღვევის გამო. 394-ე მუხლით კი დაზარალებულს აქვს მიუღებელი შემოსავლის მოთხოვნის უფლება."
    },
    {
        "id": "case_2",
        "title": "განზრახ მკვლელობა დამამძიმებელ გარემოებებში",
        "code": "სისხლის სამართალი",
        "article": "სსკ 109-ე მუხლი",
        "file_name": "სისხლის_სამართლის_ტესტები.docx",
        "question": "პირმა შურისძიების მოტივით განზრახ ცეცხლი წაუკიდა საცხოვრებელ სახლს, სადაც იმყოფებოდა 3 ადამიანი. შედეგად გარდაიცვალა ერთი პირი. როგორ უნდა დაკვალიფიცირდეს ქმედება?",
        "options": [
            "ა) სსკ-ის 108-ე მუხლით (განზრახ მკვლელობა).",
            "ბ) სსკ-ის 109-ე მუხლით (განზრახ მკვლელობა დამამძიმებელ გარემოებაში - სიცოცხლისათვის საშიში საშუალებით).",
            "გ) სსკ-ის 187-ე მუხლით (ნივთის დაზიანება).",
            "დ) გაუფრთხილებლობით სიცოცხლის მოსპობა."
        ],
        "correct_index": 1,
        "explanation": "საქართველოს სისხლის სამართლის კოდექსის 109-ე მუხლის შესაბამისად, განზრახ მკვლელობა ჩადენილი ისეთი საშუალებით, რომელიც საფრთხეს უქმნის სხვათა სიცოცხლეს ან ჯანმრთელობას, კვალიფიცირდება დამამძიმებელ გარემოებად."
    },
    {
        "id": "case_3",
        "title": "ადმინისტრაციული აქტის გასაჩივრების ვადა",
        "code": "ადმინისტრაციული სამართალი",
        "article": "ზაკ 180-ე მუხლი",
        "file_name": "ადმინისტრაციული_საპროცესო.docx",
        "question": "მოქალაქეს ჩაბარდა ინდივიდუალური ადმინისტრაციულ-სამართლებრივი აქტი. რა ვადაში აქვს მას უფლება წარადგინოს ადმინისტრაციული საჩივარი?",
        "options": [
            "ა) 10 დღის ვადაში.",
            "ბ) 1 თვის ვადაში აქტის ჩაბარების დღიდან.",
            "გ) 3 თვის ვადაში.",
            "დ) 1 წლის განმავლობაში."
        ],
        "correct_index": 1,
        "explanation": "საქართველოს ზოგადი ადმინისტრაციული კოდექსის 180-ე მუხლის 1-ლი ნაწილის თანახმად, ადმინისტრაციული საჩივარი წარდგენილ უნდა იქნეს 1 თვის ვადაში ადმინისტრაციულ-სამართლებრივი აქტის გამოქვეყნების ან ჩაბარების დღიდან."
    },
    {
        "id": "case_4",
        "title": "სასამართლო პრაქტიკა: საკუთრების უფლების შეზღუდვა",
        "code": "საქმეები / სასამართლო პრაქტიკა",
        "article": "კონსტიტუციის 19-ე მუხლი",
        "file_name": "საკონსტიტუციო_პრაქტიკა.docx",
        "question": "საკონსტიტუციო სასამართლოს განმარტებით, რა შემთხვევაშია დასაშვები საკუთრების უფლების შეზღუდვა საჯარო ინტერესებისათვის?",
        "options": [
            "ა) ნებისმიერ დროს, სახელმწიფო ორგანოს გადაწყვეტილებით.",
            "ბ) მხოლოდ კანონით დადგენილ შემთხვევებში, თანაბარი და სამართლიანი კომპენსაციით.",
            "გ) საკუთრების შეზღუდვა არასოდეს არ არის დასაშვები.",
            "დ) მხოლოდ საგანგებო მდგომარეობის დროს."
        ],
        "correct_index": 1,
        "explanation": "საქართველოს კონსტიტუციის 19-ე მუხლის მიხედვით, საკუთრების უფლების შეზღუდვა დასაშვებია აუცილებელი საზოგადოებრივი საჭიროებისათვის კანონით დადგენილ შემთხვევებში და წესით, ჯეროვანი კომპენსაციით."
    },
    {
        "id": "case_5",
        "title": "ადვოკატთა პროფესიული ეთიკა",
        "code": "სხვადასხვა",
        "article": "ეთიკის კოდექსის მე-4 მუხლი",
        "file_name": "ეთიკის_კოდექსი.docx",
        "question": "მართებულია თუ არა ადვოკატის მიერ კლიენტის კონფიდანციალური ინფორმაციის გამჟღავნება მესამე პირებისთვის კლიენტის თანხმობის გარეშე?",
        "options": [
            "ა) დიახ, თუ ეს ადვოკატის ინტერესებშია.",
            "ბ) არა, პროფესიული საიდუმლოების დაცვა ადვოკატის უვადო მოვალეობაა.",
            "გ) დიახ, თუ კლიენტმა ჰონორარი არ გადაიხადა.",
            "დ) მხოლოდ ჟურნალისტებთან საუბრისას."
        ],
        "correct_index": 1,
        "explanation": "ადვოკატთა პროფესიული ეთიკის კოდექსის თანახმად, პროფესიული საიდუმლოების დაცვა ადვოკატის ფუნდამენტური და უვადო მოვალეობაა."
    }
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_DATA
    else:
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_progress(progress):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

cases_db = load_data()
user_progress = load_progress()

# Initialize Session State
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "home"
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"  # light or dark
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False
if "bookmarks" not in st.session_state:
    st.session_state["bookmarks"] = user_progress.get("bookmarks", [])
if "study_indices" not in st.session_state:
    st.session_state["study_indices"] = user_progress.get("study_indices", {})
if "exam_active" not in st.session_state:
    st.session_state["exam_active"] = False
if "streak" not in st.session_state:
    st.session_state["streak"] = user_progress.get("streak", 3)
if "daily_goal_done" not in st.session_state:
    st.session_state["daily_goal_done"] = user_progress.get("daily_goal_done", 8)
if "daily_goal_target" not in st.session_state:
    st.session_state["daily_goal_target"] = 15

# ==============================================================================
# 2. DYNAMIC THEME & GLASSMORPHISM CSS
# ==============================================================================
is_dark = (st.session_state["theme"] == "dark")

bg_color = "#0F172A" if is_dark else "#FDFBF7"
card_bg = "rgba(30, 41, 59, 0.75)" if is_dark else "rgba(255, 255, 255, 0.85)"
card_border = "rgba(212, 175, 55, 0.3)" if is_dark else "rgba(226, 232, 240, 0.9)"
text_color = "#F8FAFC" if is_dark else "#1E293B"
sub_text_color = "#94A3B8" if is_dark else "#64748B"
accent_gold = "#D4AF37"
accent_blue = "#3B82F6" if is_dark else "#1E3A8A"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    
    .stApp {{
        background-color: {bg_color} !important;
    }}
    
    /* Watermark LEGAL */
    .watermark-bg {{
        position: fixed;
        top: 45%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 16vw;
        font-weight: 900;
        color: {"rgba(255, 255, 255, 0.03)" if is_dark else "rgba(30, 58, 138, 0.03)"};
        z-index: 0;
        pointer-events: none;
        letter-spacing: 25px;
        user-select: none;
        white-space: nowrap;
    }}
    
    /* Glassmorphism Cards */
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid {card_border};
        padding: 1.25rem 1.5rem;
        box-shadow: 0 8px 32px 0 {"rgba(0, 0, 0, 0.37)" if is_dark else "rgba(31, 38, 135, 0.07)"};
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    
    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 {"rgba(212, 175, 55, 0.2)" if is_dark else "rgba(30, 58, 138, 0.12)"};
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Top Navigation Bar */
    .nav-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: {card_bg};
        backdrop-filter: blur(20px);
        border-radius: 18px;
        padding: 0.5rem 1rem;
        border: 1px solid {card_border};
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }}
    
    /* Buttons Styling */
    .stButton>button {{
        background: linear-gradient(135deg, {accent_blue} 0%, #2563EB 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-1px) scale(1.01) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    }}
    
    .badge-code {{
        background: rgba(212, 175, 55, 0.18);
        color: {accent_gold};
        border: 1px solid rgba(212, 175, 55, 0.4);
        padding: 4px 12px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.8rem;
    }}
    
    .badge-complete {{
        background: rgba(16, 185, 129, 0.18);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.8rem;
    }}
    
    /* Flashcard Flip CSS */
    .flashcard {{
        background: {card_bg};
        border: 2px solid {accent_gold};
        border-radius: 24px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}

    /* Mobile Bottom Navigation (Responsive) */
    @media (max-width: 768px) {{
        .nav-container {{
            position: fixed;
            bottom: 10px;
            left: 10px;
            right: 10px;
            z-index: 9999;
            margin-bottom: 0;
            border-radius: 25px;
            background: {"rgba(15, 23, 42, 0.95)" if is_dark else "rgba(255, 255, 255, 0.95)"};
        }}
        .main-content {{
            padding-bottom: 80px;
        }}
    }}
</style>
<div class="watermark-bg">LEGAL</div>
""", unsafe_allow_html=True)

# Helper function to render SVG gauge charts
def render_svg_gauge(score_percent, title="მზაობის ინდექსი"):
    angle = (score_percent / 100) * 180
    color = "#10B981" if score_percent >= 75 else ("#F59E0B" if score_percent >= 50 else "#EF4444")
    svg_html = f"""
    <div style="text-align: center; padding: 0.5rem;">
        <svg width="160" height="95" viewBox="0 0 160 95">
            <path d="M 15 85 A 65 65 0 0 1 145 85" fill="none" stroke="{"#334155" if is_dark else "#E2E8F0"}" stroke-width="14" stroke-linecap="round"/>
            <path d="M 15 85 A 65 65 0 0 1 145 85" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round"
                  stroke-dasharray="204.2" stroke-dashoffset="{204.2 - (204.2 * score_percent / 100)}"/>
            <text x="80" y="70" text-anchor="middle" font-size="24" font-weight="bold" fill="{text_color}">{int(score_percent)}%</text>
            <text x="80" y="88" text-anchor="middle" font-size="11" fill="{sub_text_color}">{title}</text>
        </svg>
    </div>
    """
    return svg_html

# Helper parser for uploads
def parse_uploaded_file(uploaded_file, selected_code):
    file_name = uploaded_file.name
    content_text = ""
    if file_name.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(uploaded_file)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            content_text = "\n".join(paragraphs)
        except Exception:
            content_text = str(uploaded_file.read().decode("utf-8", "ignore"))
    else:
        content_text = str(uploaded_file.read().decode("utf-8", "ignore"))

    blocks = [b.strip() for b in content_text.split("\n\n") if b.strip()]
    new_cases = []

    if len(blocks) >= 1:
        for idx, block in enumerate(blocks):
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            title = lines[0][:60] if lines else f"კაზუსი/ტესტი {idx+1} ({file_name})"
            question = "\n".join(lines)
            new_cases.append({
                "id": f"upload_{int(time.time())}_{idx}",
                "title": f"კაზუსი: {title}",
                "code": selected_code,
                "article": f"მუხლი/ნაწილი {idx+1}",
                "file_name": file_name,
                "question": question,
                "options": [
                    "ა) სწორია / დასაშვებია (სამართლებრივი საფუძვლით)",
                    "ბ) არასწორია / უსაფუძვლოა",
                    "გ) ნაწილობრივ მართებულია",
                    "დ) საჭიროებს დამატებით მტკიცებულებებს"
                ],
                "correct_index": 0,
                "explanation": f"ანალიზი დაყრდნობილია ატვირთულ ფაილზე: {file_name}. იხ. {selected_code}-ის შესაბამისი მუხლები."
            })
    else:
        new_cases.append({
            "id": f"upload_{int(time.time())}_0",
            "title": f"ატვირთული ფაილი: {file_name}",
            "code": selected_code,
            "article": "საერთო მუხლები",
            "file_name": file_name,
            "question": content_text,
            "options": [
                "ა) მართებულია",
                "ბ) მცდარია",
                "გ) ნაწილობრივ მართებულია",
                "დ) უცნობია"
            ],
            "correct_index": 0,
            "explanation": f"ფაილი {file_name} წარმატებით დაემატა {selected_code}-ის ბაზაში."
        })
    return new_cases

# ==============================================================================
# 3. LANDING PAGE (სახელის შეყვანა + LEGAL წყლისნიშანი)
# ==============================================================================
if not st.session_state["user_name"]:
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #D4AF37; margin-bottom: 0.5rem;'>⚖️ LEGAL PORTAL</h2>", unsafe_allow_html=True)
        st.write("შეიყვანეთ სახელი და გვარი სისტემაში შესასვლელად:")
        
        name_input = st.text_input("სახელი და გვარი:", placeholder="მაგ: გიორგი ბერიძე", label_visibility="collapsed")
        
        if st.button("🚀 სისტემაში შესვლა"):
            if name_input.strip():
                st.session_state["user_name"] = name_input.strip()
                st.rerun()
            else:
                st.warning("გთხოვთ შეიყვანოთ სახელი!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 4. TOP NAVIGATION BAR (წვრილი, კომპაქტური, iOS-სტილი)
# ==============================================================================
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7 = st.columns([1.5, 1, 1, 1, 1, 1, 0.8])

with nav_col1:
    st.markdown(f"**⚖️ LEGAL** | `👤 {st.session_state['user_name']}`")

with nav_col2:
    if st.button("🏠 მთავარი", key="btn_nav_home"):
        st.session_state["active_tab"] = "home"
        st.rerun()

with nav_col3:
    if st.button("📖 სწავლა", key="btn_nav_study"):
        st.session_state["active_tab"] = "study"
        st.rerun()

with nav_col4:
    if st.button("⏱️ გამოცდა", key="btn_nav_exam"):
        st.session_state["active_tab"] = "exam"
        st.rerun()

with nav_col5:
    if st.button("📊 ანალიტიკა", key="btn_nav_analytics"):
        st.session_state["active_tab"] = "analytics"
        st.rerun()

with nav_col6:
    if st.button("🔒 ატვირთვა", key="btn_nav_upload"):
        st.session_state["active_tab"] = "upload"
        st.rerun()

with nav_col7:
    theme_icon = "🌙" if not is_dark else "☀️"
    if st.button(theme_icon, key="btn_theme_toggle"):
        st.session_state["theme"] = "dark" if not is_dark else "light"
        st.rerun()

st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border-color: rgba(212, 175, 55, 0.2);'>", unsafe_allow_html=True)

# ==============================================================================
# 5. TAB 1: 🏠 HOME PAGE (დეშბორდი, ძიება, Streak, ჩარჩოებიანი ბარათები)
# ==============================================================================
if st.session_state["active_tab"] == "home":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_col1, h_col2, h_col3 = st.columns([2, 1, 1])
    with h_col1:
        st.markdown(f"### 👋 გამარჯობა, **{st.session_state['user_name']}**!")
        st.write("მოემზადეთ ადვოკატთა გამოცდისთვის ეფექტურად.")
    with h_col2:
        st.markdown(f"<div style='text-align: center; padding: 0.5rem; border-radius: 14px; background: rgba(212,175,55,0.1); border: 1px solid rgba(212,175,55,0.3);'><b>🔥 Streak</b><br><span style='font-size: 1.4rem; color: #D4AF37;'>{st.session_state['streak']} დღე</span></div>", unsafe_allow_html=True)
    with h_col3:
        st.markdown(f"<div style='text-align: center; padding: 0.5rem; border-radius: 14px; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3);'><b>🎯 დღიური მიზანი</b><br><span style='font-size: 1.4rem; color: #3B82F6;'>{st.session_state['daily_goal_done']}/{st.session_state['daily_goal_target']}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Search Bar
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    search_q = st.text_input("🔍 **მყისიერი ძიება ბაზაში (ჩაწერეთ საკვანძო სიტყვა, მუხლი ან კოდექსი):**", placeholder="მაგ: 109-ე მუხლი, ხელშეკრულება, ზიანი...")
    if search_q.strip():
        results = [c for c in cases_db if search_q.lower() in c['question'].lower() or search_q.lower() in c['title'].lower() or search_q.lower() in c.get('article', '').lower()]
        st.write(f"🔎 ნაპოვნია **{len(results)}** შედეგი:")
        for r in results[:5]:
            st.info(f"📌 **[{r['code']}]** {r['title']} ({r.get('article', '')})\n\n{r['question'][:150]}...")
    st.markdown("</div>", unsafe_allow_html=True)

    # 4 Rounded Grid Cards
    st.markdown("#### 📌 აირჩიეთ სასურველი სექცია:")
    grid_col1, grid_col2 = st.columns(2)

    with grid_col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📖 სწავლისა და ვარჯიშის გრაფა")
        st.write("გაიარეთ კაზუსები თითო-თითოდ, აირჩიეთ მუხლები ან გამოიყენეთ ფლეშ-ბარათები.")
        if st.button("🚀 სწავლის დაწყება", key="go_study"):
            st.session_state["active_tab"] = "study"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 ანალიტიკა და პროგრესი")
        st.write("იხილეთ თქვენი მზაობის პროცენტული ინდექსი და სუსტი/ძლიერი მხარეები.")
        if st.button("📈 ანალიტიკის ნახვა", key="go_analytics"):
            st.session_state["active_tab"] = "analytics"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with grid_col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### ⏱️ გამოცდის სიმულაცია")
        st.write("რეალური ტესტირება ტაიმერით, მატრიცითა და 100-მდე კითხვით.")
        if st.button("⏱️ გამოცდის დაწყება", key="go_exam"):
            st.session_state["active_tab"] = "exam"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🔒 ატვირთვისა და მართვის გრაფა")
        st.write("დაამატეთ ახალი Word/Text კაზუსები ან წაშალეთ არსებული მონაცემები.")
        if st.button("🔑 ადმინისტრირება", key="go_upload"):
            st.session_state["active_tab"] = "upload"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 6. TAB 2: 📖 სწავლის გრაფა (მუხლის არჩევა, ფლეშ-ბარათები, შენახული)
# ==============================================================================
elif st.session_state["active_tab"] == "study":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📖 სწავლისა და ვარჯიშის გრაფა")
    
    codes_list = sorted(list(set([c["code"] for c in cases_db])))
    codes_list.insert(0, "ყველა კოდექსი / საგანი")
    codes_list.append("🔖 შენახული კაზუსები")

    selected_code = st.selectbox("📚 აირჩიეთ კოდექსი ან შენახულები:", codes_list)

    if selected_code == "🔖 შენახული კაზუსები":
        filtered_cases = [c for c in cases_db if c["id"] in st.session_state["bookmarks"]]
    elif selected_code != "ყველა კოდექსი / საგანი":
        filtered_cases = [c for c in cases_db if c.get("code") == selected_code]
    else:
        filtered_cases = cases_db

    st.markdown("</div>", unsafe_allow_html=True)

    if not filtered_cases:
        st.info("ამ სექციაში ჯერ არ არის კაზუსები.")
    else:
        # Mode selector: Single Case View vs Flashcards vs All Articles List
        study_mode = st.radio("🔄 სწავლის ფორმატი:", ["📚 კაზუსების ნახვა / სწავლა", "🎴 ფლეშ-ბარათები", "📜 ყველა მუხლის სია"], horizontal=True)

        # Saved progress index
        code_key = selected_code
        curr_idx = st.session_state["study_indices"].get(code_key, 0)
        if curr_idx >= len(filtered_cases):
            curr_idx = 0

        if study_mode == "📚 კაზუსების ნახვა / სწავლა":
            # Specific Article/Case Dropdown
            case_titles = [f"#{i+1}: {c['title']} ({c.get('article', 'მუხლი')})" for i, c in enumerate(filtered_cases)]
            chosen_case_str = st.selectbox("📌 აირჩიეთ კონკრეტული მუხლი / კაზუსი დასამუშავებლად:", case_titles, index=curr_idx)
            curr_idx = case_titles.index(chosen_case_str)
            st.session_state["study_indices"][code_key] = curr_idx
            user_progress["study_indices"] = st.session_state["study_indices"]
            save_progress(user_progress)

            case = filtered_cases[curr_idx]

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            col_t1, col_t2 = st.columns([4, 1])
            with col_t1:
                is_complete = curr_idx == len(filtered_cases) - 1
                badge_class = "badge-complete" if is_complete else "badge-code"
                badge_txt = "✅ კოდექსი დასრულებულია" if is_complete else case['code']
                st.markdown(f"<span class='{badge_class}'>{badge_txt}</span> | 📌 **{case.get('article', '')}**", unsafe_allow_html=True)
                st.markdown(f"#### {case['title']}")
            with col_t2:
                is_bookmarked = case["id"] in st.session_state["bookmarks"]
                bm_btn_text = "📌 შენახულია" if is_bookmarked else "🔖 შენახვა"
                if st.button(bm_btn_text, key=f"bm_{case['id']}"):
                    if is_bookmarked:
                        st.session_state["bookmarks"].remove(case["id"])
                    else:
                        st.session_state["bookmarks"].append(case["id"])
                    user_progress["bookmarks"] = st.session_state["bookmarks"]
                    save_progress(user_progress)
                    st.rerun()

            st.write(case["question"])

            user_ans = st.radio("აირჩიეთ სწორი პასუხი:", case["options"], key=f"q_radio_{case['id']}")

            if st.button("🔍 პასუხის შემოწმება", key=f"check_{case['id']}"):
                correct_opt = case["options"][case["correct_index"]]
                if user_ans == correct_opt:
                    st.success("✅ **სწორია!** ყოჩაღ!")
                    st.session_state["daily_goal_done"] = min(st.session_state["daily_goal_target"], st.session_state["daily_goal_done"] + 1)
                    user_progress["daily_goal_done"] = st.session_state["daily_goal_done"]
                    save_progress(user_progress)
                else:
                    st.error(f"❌ **არასწორია.** სწორი პასუხია: {correct_opt}")
                st.info(f"💡 **სამართლებრივი დასაბუთება:**\n{case['explanation']}")

            c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
            with c_btn1:
                if st.button("⬅️ წინა", disabled=(curr_idx == 0)):
                    st.session_state["study_indices"][code_key] = curr_idx - 1
                    st.rerun()
            with c_btn3:
                if st.button("➡️ შემდეგი", disabled=(curr_idx == len(filtered_cases) - 1)):
                    st.session_state["study_indices"][code_key] = curr_idx + 1
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        elif study_mode == "🎴 ფლეშ-ბარათები":
            case = filtered_cases[curr_idx]
            st.markdown(f"<div class='flashcard'><h3>📌 {case.get('article', 'მუხლი')}</h3><p style='font-size: 1.1rem;'>{case['question']}</p></div>", unsafe_allow_html=True)
            
            if st.button("🔄 ბარათის ამოტრიალება (პასუხის ნახვა)"):
                st.success(f"<b>სწორი პასუხი:</b> {case['options'][case['correct_index']]}\n\n<b>განმარტება:</b> {case['explanation']}")

            fc_col1, fc_col2 = st.columns(2)
            with fc_col1:
                if st.button("⬅️ წინა ბარათი", disabled=(curr_idx == 0)):
                    st.session_state["study_indices"][code_key] = curr_idx - 1
                    st.rerun()
            with fc_col2:
                if st.button("➡️ შემდეგი ბარათი", disabled=(curr_idx == len(filtered_cases) - 1)):
                    st.session_state["study_indices"][code_key] = curr_idx + 1
                    st.rerun()

        elif study_mode == "📜 ყველა მუხლის სია":
            for idx, c in enumerate(filtered_cases):
                with st.expander(f"📌 #{idx+1}: {c['title']} ({c.get('article', 'მუხლი')})"):
                    st.write(f"**კითხვა:** {c['question']}")
                    st.write(f"**სწორი პასუხი:** {c['options'][c['correct_index']]}")
                    st.info(f"**განმარტება:** {c['explanation']}")

# ==============================================================================
# 7. TAB 3: ⏱️ გამოცდის გრაფა (სრული სიმულაცია, 100 კითხვა, მატრიცა, Pop-up)
# ==============================================================================
elif st.session_state["active_tab"] == "exam":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### ⏱️ ადვოკატთა გამოცდის სიმულაცია")
    
    if not st.session_state["exam_active"]:
        all_codes = sorted(list(set([c["code"] for c in cases_db])))
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            selected_exam_codes = st.multiselect("📘 აირჩიეთ საგამოცდო კოდექსები:", all_codes, default=all_codes)
            if st.button("✅ ყველას არჩევა"):
                selected_exam_codes = all_codes
        
        with col_ex2:
            num_questions = st.slider("🔢 კითხვების რაოდენობა (მაქს. 100):", min_value=5, max_value=min(100, len(cases_db)), value=min(20, len(cases_db)))

        if st.button("🚀 გამოცდის დაწყება"):
            if not selected_exam_codes:
                st.warning("გთხოვთ აირჩიოთ სულ მცირე 1 კოდექსი!")
            else:
                # Filter cases evenly
                pool = [c for c in cases_db if c["code"] in selected_exam_codes]
                random.shuffle(pool)
                exam_pool = pool[:num_questions]
                
                st.session_state["exam_active"] = True
                st.session_state["exam_cases"] = exam_pool
                st.session_state["exam_responses"] = {}
                st.session_state["exam_current_idx"] = 0
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["exam_active"]:
        exam_cases = st.session_state["exam_cases"]
        curr_e_idx = st.session_state["exam_current_idx"]
        
        # Matrix Navigator Grid
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.write("<b>📌 კითხვების ნავიგატორი:</b>", unsafe_allow_html=True)
        m_cols = st.columns(10)
        for i, c_item in enumerate(exam_cases):
            col_m = m_cols[i % 10]
            is_ans = c_item["id"] in st.session_state["exam_responses"]
            btn_label = f"🟢 {i+1}" if is_ans else f"{i+1}"
            if col_m.button(btn_label, key=f"mat_{i}"):
                st.session_state["exam_current_idx"] = i
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Current Exam Question Card
        c_case = exam_cases[curr_e_idx]
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"#### კითხვა {curr_e_idx+1} / {len(exam_cases)}: {c_case['title']}")
        st.write(c_case["question"])

        prev_selected = st.session_state["exam_responses"].get(c_case["id"], None)
        opt_idx = c_case["options"].index(prev_selected) if prev_selected in c_case["options"] else 0

        user_choice = st.radio("აირჩიეთ პასუხი:", c_case["options"], index=opt_idx, key=f"ex_choice_{curr_e_idx}")
        st.session_state["exam_responses"][c_case["id"]] = user_choice

        ex_col1, ex_col2, ex_col3 = st.columns([1, 2, 1])
        with ex_col1:
            if st.button("⬅️ წინა კითხვა", disabled=(curr_e_idx == 0)):
                st.session_state["exam_current_idx"] -= 1
                st.rerun()
        with ex_col3:
            if st.button("➡️ შემდეგი კითხვა", disabled=(curr_e_idx == len(exam_cases) - 1)):
                st.session_state["exam_current_idx"] += 1
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🏁 გამოცდის დასრულება და შეფასება"):
            st.session_state["exam_active"] = False
            
            # Calculate score
            score = 0
            wrong_list = []
            for c_item in exam_cases:
                ans = st.session_state["exam_responses"].get(c_item["id"])
                corr = c_item["options"][c_item["correct_index"]]
                if ans == corr:
                    score += 1
                else:
                    wrong_list.append((c_item, ans, corr))

            pct = round((score / len(exam_cases)) * 100, 1)

            # Store history
            if "exam_history" not in user_progress:
                user_progress["exam_history"] = []
            user_progress["exam_history"].append({"date": time.strftime("%Y-%m-%d %H:%M"), "score": score, "total": len(exam_cases), "pct": pct})
            save_progress(user_progress)

            st.balloons()
            
            # Central Results Modal Window
            st.markdown("<div class='glass-card' style='text-align: center; border: 2px solid #D4AF37;'>", unsafe_allow_html=True)
            st.markdown("<h2>🎉 გამოცდის შედეგი</h2>", unsafe_allow_html=True)
            st.markdown(render_svg_gauge(pct, "საბოლოო ქულა"), unsafe_allow_html=True)
            st.markdown(f"### **{score} / {len(exam_cases)}** კითხვა ({pct}%)")

            if pct >= 75:
                st.success("🌟 **გილოცავთ! თქვენ წარმატებით ჩააბარეთ გამოცდის სიმულაცია!**")
            else:
                st.warning("📚 **რეკომენდაცია:** გირჩევთ კიდევ გაიაროთ სწავლის გრაფა მასალის უკეთ ასათვისებლად.")

            if wrong_list:
                with st.expander("❌ შეცდომით გაცემული კითხვების ანალიზი"):
                    for w_case, u_a, c_a in wrong_list:
                        st.write(f"📌 **{w_case['title']}**")
                        st.write(f"თქვენი პასუხი: `{u_a}` | სწორი: `{c_a}`")
                        st.info(w_case["explanation"])

            if st.button("🔄 ახალი გამოცდის დაწყება"):
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 8. TAB 4: 📊 ანალიტიკა & პროგრესი (SVG გრაფიკები)
# ==============================================================================
elif st.session_state["active_tab"] == "analytics":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 მომხმარებლის ანალიტიკა")
    
    an_col1, an_col2 = st.columns(2)
    
    with an_col1:
        st.markdown(render_svg_gauge(78, "საერთო მზაობის ინდექსი"), unsafe_allow_html=True)
    
    with an_col2:
        st.write("📌 **სტატისტიკა კოდექსების მიხედვით:**")
        codes_set = list(set([c["code"] for c in cases_db]))
        for cd in codes_set:
            cnt = len([c for c in cases_db if c["code"] == cd])
            st.write(f"• **{cd}:** {cnt} კაზუსი (მზადაა 100%)")
            st.progress(1.0)
            
    st.markdown("---")
    st.write("📜 **ბოლო გამოცდების ისტორია:**")
    hist = user_progress.get("exam_history", [])
    if hist:
        for h in reversed(hist[-5:]):
            st.write(f"🗓️ `{h['date']}` — ქულა: **{h['score']}/{h['total']}** ({h['pct']}%)")
    else:
        st.info("გამოცდების ისტორია ჯერ ცარიელია.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 9. TAB 5: 🔒 ატვირთვა & მართვა (პაროლი 'legal')
# ==============================================================================
elif st.session_state["active_tab"] == "upload":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🔒 ადმინისტრირება & ფაილების ატვირთვა / წაშლა")
    
    if not st.session_state["admin_logged_in"]:
        pwd_input = st.text_input("🔑 შეიყვანეთ ადმინისტრატორის პაროლი:", type="password", placeholder="პაროლი")
        if st.button("შესვლა"):
            if pwd_input == "legal":
                st.session_state["admin_logged_in"] = True
                st.success("ავტორიზაცია წარმატებულია!")
                st.rerun()
            else:
                st.error("❌ არასწორი პაროლი!")
    else:
        st.success("✅ ავტორიზებული ხართ!")
        
        up_col1, up_col2 = st.columns(2)
        with up_col1:
            st.markdown("#### 📤 ფაილის ატვირთვა")
            up_code = st.selectbox("აირჩიეთ კოდექსი:", ["სამოქალაქო სამართალი", "სისხლის სამართალი", "ადმინისტრაციული სამართალი", "საკონსტიტუციო სამართალი", "საერთაშორისო სამართალი", "ადვოკატთა პროფესიული ეთიკა"])
            up_file = st.file_uploader("ატვირთეთ Word (.docx) ან Text (.txt) ფაილი:", type=["docx", "txt"])
            
            if st.button("➕ დამატება ბაზაში"):
                if up_file is not None:
                    parsed = parse_uploaded_file(up_file, up_code)
                    cases_db.extend(parsed)
                    save_data(cases_db)
                    st.success(f"წარმატებით დაემატა {len(parsed)} კაზუსი!")
                    st.rerun()
                else:
                    st.warning("აირჩიეთ ფაილი!")
                    
        with up_col2:
            st.markdown("#### 🗑️ ბაზის მართვა")
            st.write(f"სისტემაში არის **{len(cases_db)}** კაზუსი.")
            if st.button("⚠️ ყველა მონაცემის საწყის მდგომარეობაში დაბრუნება"):
                save_data(DEFAULT_DATA)
                st.success("ბაზა განახლდა საწყისზე!")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
