import json
import os
import re
import time
import urllib.request
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==============================================================================
st.set_page_config(
    page_title="LEGAL",
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
        "question": (
            "შპს 'ალფამ' გააფორმა ხელშეკრულება შპს 'ბეტასთან' დანადგარების"
            " მოწოდებაზე. 'ბეტამ' დაარღვია ვადა 2 თვით. 'ალფამ' ცალმხრივად"
            " მოშალა ხელშეკრულება და მოითხოვა მიუღებელი შემოსავლის"
            " ანაზღაურება. კანონიერია თუ არა 'ალფას' მოთხოვნა?"
        ),
        "options": [
            (
                "ა) კანონიერია, რადგან ვალდებულების დარღვევა იძლევა"
                " ხელშეკრულებიდან გასვლისა და ზიანის მოთხოვნის უფლებას (სსკ 394-ე"
                " და 405-ე მუხლები)."
            ),
            "ბ) არაკანონიერია, რადგან ჯერ დამატებითი ვადა უნდა დაენიშნა.",
            "გ) კანონიერია მხოლოდ ნაწილობრივ.",
            "დ) 'ბეტა' გათავისუფლებულია პასუხისმგებლობისგან.",
        ],
        "correct_index": 0,
        "explanation": (
            "საქართველოს სამოქალაქო კოდექსის 405-ე მუხლის თანახმად,"
            " ხელშეკრულების მონაწილე მხარეს შეუძლია უარი თქვას ხელშეკრულებაზე"
            " ვალდებულების დარღვევის გამო. 394-ე მუხლით კი დაზარალებულს აქვს"
            " მიუღებელი შემოსავლის მოთხოვნის უფლება."
        ),
    },
    {
        "id": "case_2",
        "title": "განზრახ მკვლელობა დამამძიმებელ გარემოებებში",
        "code": "სისხლის სამართალი",
        "article": "სსკ 109-ე მუხლი",
        "file_name": "სისხლის_სამართლის_ტესტები.docx",
        "question": (
            "პირმა შურისძიების მოტივით განზრახ ცეცხლი წაუკიდა საცხოვრებელ"
            " სახლს, სადაც იმყოფებოდა 3 ადამიანი. შედეგად გარდაიცვალა ერთი პირი."
            " როგორ უნდა დაკვალიფიცირდეს ქმედება?"
        ),
        "options": [
            "ა) სსკ-ის 108-ე მუხლით (განზრახ მკვლელობა).",
            (
                "ბ) სსკ-ის 109-ე მუხლით (განზრახ მკვლელობა დამამძიმებელ"
                " გარემოებაში - სიცოცხლისათვის საშიში საშუალებით)."
            ),
            "გ) სსკ-ის 187-ე მუხლით (ნივთის დაზიანება).",
            "დ) გაუფრთხილებლობით სიცოცხლის მოსპობა.",
        ],
        "correct_index": 1,
        "explanation": (
            "საქართველოს სისხლის სამართლის კოდექსის 109-ე მუხლის შესაბამისად,"
            " განზრახ მკვლელობა ჩადენილი ისეთი საშუალებით, რომელიც საფრთხეს"
            " უქმნის სხვათა სიცოცხლეს ან ჯანმრთელობას, კვალიფიცირდება"
            " დამამძიმებელ გარემოებად."
        ),
    },
    {
        "id": "case_3",
        "title": "ადმინისტრაციული აქტის გასაჩივრების ვადა",
        "code": "ადმინისტრაციული სამართალი",
        "article": "ზაკ 180-ე მუხლი",
        "file_name": "ადმინისტრაციული_საპროცესო.docx",
        "question": (
            "მოქალაქეს ჩაბარდა ინდივიდუალური ადმინისტრაციულ-სამართლებრივი აქტი."
            " რა ვადაში აქვს მას უფლება წარადგინოს ადმინისტრაციული საჩივარი?"
        ),
        "options": [
            "ა) 10 დღის ვადაში.",
            "ბ) 1 თვის ვადაში აქტის ჩაბარების დღიდან.",
            "გ) 3 თვის ვადაში.",
            "დ) 1 წლის განმავლობაში.",
        ],
        "correct_index": 1,
        "explanation": (
            "საქართველოს ზოგადი ადმინისტრაციული კოდექსის 180-ე მუხლის 1-ლი"
            " ნაწილის თანახმად, ადმინისტრაციული საჩივარი წარდგენილ უნდა იქნეს 1"
            " თვის ვადაში ადმინისტრაციულ-სამართლებრივი აქტის გამოქვეყნების ან"
            " ჩაბარების დღიდან."
        ),
    },
    {
        "id": "case_4",
        "title": "სასამართლო პრაქტიკა: საკუთრების უფლების შეზღუდვა",
        "code": "საქმეები / სასამართლო პრაქტიკა",
        "article": "კონსტიტუციის 19-ე მუხლი",
        "file_name": "საკონსტიტუციო_პრაქტიკა.docx",
        "question": (
            "საკონსტიტუციო სასამართლოს განმარტებით, რა შემთხვევაშია დასაშვები"
            " საკუთრების უფლების შეზღუდვა საჯარო ინტერესებისათვის?"
        ),
        "options": [
            "ა) ნებისმიერ დროს, სახელმწიფო ორგანოს გადაწყვეტილებით.",
            (
                "ბ) მხოლოდ კანონით დადგენილ შემთხვევებში, თანაბარი და"
                " სამართლიანი კომპენსაციით."
            ),
            "გ) საკუთრების შეზღუდვა არასოდეს არ არის დასაშვები.",
            "დ) მხოლოდ საგანგებო მდგომარეობის დროს.",
        ],
        "correct_index": 1,
        "explanation": (
            "საქართველოს კონსტიტუციის 19-ე მუხლის მიხედვით, საკუთრების უფლების"
            " შეზღუდვა დასაშვებია აუცილებელი საზოგადოებრივი საჭიროებისათვის"
            " კანონით დადგენილ შემთხვევებში და წესით, ჯეროვანი კომპენსაციით."
        ),
    },
    {
        "id": "case_5",
        "title": "ადვოკატთა პროფესიული ეთიკა",
        "code": "სხვადასხვა",
        "article": "ეთიკის კოდექსის მე-4 მუხლი",
        "file_name": "ეთიკის_კოდექსი.docx",
        "question": (
            "მართებულია თუ არა ადვოკატის მიერ კლიენტის კონფიდანციალური"
            " ინფორმაციის გამჟღავნება მესამე პირებისთვის კლიენტის თანხმობის"
            " გარეშე?"
        ),
        "options": [
            "ა) დიახ, თუ ეს ადვოკატის ინტერესებშია.",
            (
                "ბ) არა, პროფესიული საიდუმლოების დაცვა ადვოკატის უვადო"
                " მოვალეობაა."
            ),
            "გ) დიახ, თუ კლიენტმა ჰონორარი არ გადაიხადა.",
            "დ) მხოლოდ ჟურნალისტებთან საუბრისას.",
        ],
        "correct_index": 1,
        "explanation": (
            "ადვოკატთა პროფესიული ეთიკის კოდექსის თანახმად, პროფესიული"
            " საიდუმლოების დაცვა ადვოკატის ფუნდამენტური და უვადო მოვალეობაა."
        ),
    },
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


# Google Drive-იდან ფაილის ჩამოტვირთვის ფუნქცია
def download_gdrive_file(url):
  match = re.search(r"/d/([a-zA-Z0-9_-]+)", url) or re.search(
      r"id=([a-zA-Z0-9_-]+)", url
  )
  if not match:
    return None, "Google Drive-ის არასწორი ლინკი!"
  file_id = match.group(1)
  download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
  try:
    req = urllib.request.Request(
        download_url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
      data = response.read()
    return data, None
  except Exception as e:
    return None, f"ჩამოტვირთვის შეცდომა: {str(e)}"


# ჭკვიანი ფაილის დამუშავება (Word / Text) - მრავალფაზიანი დაყოფა
def parse_uploaded_file(uploaded_file, selected_code, file_name=None):
  if file_name is None:
    file_name = getattr(uploaded_file, "name", "gdrive_doc.docx")

  content_text = ""
  if file_name.endswith(".docx"):
    try:
      import docx

      doc = docx.Document(uploaded_file)
      paragraphs = [p.text.strip() for p in doc.paragraphs]
      content_text = "\n".join(paragraphs)
    except Exception:
      if hasattr(uploaded_file, "read"):
        content_text = str(uploaded_file.read().decode("utf-8", "ignore"))
      else:
        content_text = str(uploaded_file)
  else:
    if hasattr(uploaded_file, "read"):
      content_text = str(uploaded_file.read().decode("utf-8", "ignore"))
    else:
      content_text = str(uploaded_file)

  text = content_text.replace("\r\n", "\n").replace("\r", "\n")

  # 1. გამოყოფა '---', '===', '***' გამყოფებით
  if re.search(r"\n\s*[-=*]{3,}\s*\n", text) or re.search(
      r"^\s*[-=*]{3,}\s*\n", text
  ):
    raw_blocks = [
        b.strip()
        for b in re.split(r"\n?\s*[-=*]{3,}\s*\n?", text)
        if b.strip()
    ]
  # 2. გამოყოფა ცარიელი სტრიქონებით (\n\n+)
  elif len([b for b in re.split(r"\n\s*\n+", text) if b.strip()]) > 1:
    raw_blocks = [b.strip() for b in re.split(r"\n\s*\n+", text) if b.strip()]
  # 3. გამოყოფა საკვანძო სიტყვებით/ნუმერაციით სტრიქონის დასაწყისში
  else:
    pattern = r"(?:^|\n)\s*(?=(?:კაზუსი|ტესტი|კითხვა|საქმე|ქეისი|№|#|N|\d+[\.\)\-–—])\s*)"
    raw_blocks = [
        b.strip()
        for b in re.split(pattern, text, flags=re.IGNORECASE)
        if b.strip()
    ]

  if not raw_blocks:
    raw_blocks = [text.strip()]

  new_cases = []
  for idx, block in enumerate(raw_blocks):
    if not block:
      continue
    lines = [l.strip() for l in block.split("\n") if l.strip()]
    if not lines:
      continue

    title = lines[0][:70]

    # სავარაუდო პასუხების ამოღება (ა, ბ, გ, დ)
    options = []
    question_lines = []
    opt_pattern = r"^\s*([ა-დa-dA-D1-4])[\.\)]\s*(.*)"

    for line in lines:
      match = re.match(opt_pattern, line)
      if match:
        options.append(line)
      else:
        question_lines.append(line)

    question_text = "\n".join(question_lines)
    if not question_text:
      question_text = block

    if len(options) < 2:
      options = [
          "ა) სწორია / დასაშვებია (სამართლებრივი საფუძვლით)",
          "ბ) არასწორია / უსაფუძვლოა",
          "გ) ნაწილობრივ მართებულია",
          "დ) საჭიროებს დამატებით მტკიცებულებებს",
      ]

    new_cases.append({
        "id": f"upload_{int(time.time())}_{idx}",
        "title": f"კაზუსი #{idx+1}: {title}",
        "code": selected_code,
        "article": f"ფაილი: {file_name}",
        "file_name": file_name,
        "question": question_text,
        "options": options,
        "correct_index": 0,
        "explanation": (
            f"ანალიზი დაყრდნობილია ატვირთულ ფაილზე: {file_name}. იხ."
            f" {selected_code}-ის შესაბამისი მუხლები."
        ),
    })

  return new_cases


cases_db = load_data()
user_progress = load_progress()

# Initialize Session State
if "user_name" not in st.session_state:
  st.session_state["user_name"] = None
if "active_tab" not in st.session_state:
  st.session_state["active_tab"] = "home"
if "theme" not in st.session_state:
  st.session_state["theme"] = "light"
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
is_dark = st.session_state["theme"] == "dark"
bg_color = "#0F172A" if is_dark else "#FDFBF7"
card_bg = "rgba(30, 41, 59, 0.75)" if is_dark else "rgba(255, 255, 255, 0.85)"
card_border = "rgba(212, 175, 55, 0.3)" if is_dark else "rgba(226, 232, 240, 0.9)"
text_color = "#F8FAFC" if is_dark else "#1E293B"
sub_text_color = "#94A3B8" if is_dark else "#64748B"
accent_gold = "#D4AF37"
accent_blue = "#3B82F6" if is_dark else "#1E3A8A"

st.markdown(
    f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .main-header {{
        font-size: 2.2rem;
        color: {accent_blue};
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    .sub-header {{
        font-size: 1.1rem;
        color: {sub_text_color};
        text-align: center;
        margin-bottom: 1.8rem;
    }}
    .card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid {card_border};
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
    }}
    .stButton>button {{
        background-color: {accent_blue};
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }}
    .stButton>button:hover {{
        background-color: #2563EB;
        color: white;
        transform: translateY(-1px);
    }}
    .badge-code {{
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    .badge-article {{
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
</style>
""",
    unsafe_allow_html=True,
)


def render_svg_gauge(score_percent, title="მზაობის ინდექსი"):
  color = (
      "#10B981"
      if score_percent >= 75
      else ("#F59E0B" if score_percent >= 50 else "#EF4444")
  )

  svg_html = f"""
    <div style="text-align: center; padding: 10px;">
        <svg width="180" height="110" viewBox="0 0 200 120">
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#E2E8F0" stroke-width="18" stroke-linecap="round" />
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="{color}" stroke-width="18" stroke-linecap="round"
                stroke-dasharray="251.2" stroke-dashoffset="{251.2 - (251.2 * score_percent / 100)}" />
            <text x="100" y="85" text-anchor="middle" font-size="28" font-weight="bold" fill="{text_color}">{score_percent}%</text>
            <text x="100" y="110" text-anchor="middle" font-size="13" fill="{sub_text_color}">{title}</text>
        </svg>
    </div>
    """
  return svg_html


# ==============================================================================
# 3. LOGO INTEGRATION & LANDING PAGE
# ==============================================================================
LOGO_PATHS = [
    "Blue and White Modern Minimalist Law Business Logo.png",
    "logo.png",
    "logo.jpg",
]
found_logo = None
for lpath in LOGO_PATHS:
  if os.path.exists(lpath):
    found_logo = lpath
    break

if not st.session_state["user_name"]:
  st.markdown(
      "<div class='card' style='max-width: 500px; margin: 50px auto; text-align:"
      " center;'>",
      unsafe_allow_html=True,
  )
  if found_logo:
    st.image(found_logo, width=120)
  st.markdown(
      "<h2 class='main-header'>⚖️ LEGAL PORTAL</h2>", unsafe_allow_html=True
  )
  st.write("შეიყვანეთ სახელი და გვარი სისტემაში შესასვლელად:")

  name_input = st.text_input(
      "სახელი და გვარი:",
      placeholder="სახელი",
      label_visibility="collapsed",
  )
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
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7 = st.columns(
    [1.5, 1, 1, 1, 1, 1, 0.8]
)

with nav_col1:
  st.markdown(f"**⚖️ LEGAL** | `{st.session_state['user_name']}`")

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

st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0;' />", unsafe_allow_html=True)

# ==============================================================================
# 5. TAB 1: 🏠 HOME PAGE (დეშბორდი, ძიება, Streak, ჩარჩოებიანი ბარათები)
# ==============================================================================
if st.session_state["active_tab"] == "home":
  st.markdown("<div class='card'>", unsafe_allow_html=True)
  h_col1, h_col2, h_col3 = st.columns()

  with h_col1:
    st.markdown(f"### 👋 გამარჯობა, **{st.session_state['user_name']}**!")
    st.write(
        " გაიარეთ კაზუსები და"
        " შეამოწმეთ ცოდნა."
    )
    st.caption(
        f"🔥 **Streak:** {st.session_state['streak']} დღე ზედიზედ | 🎯 **დღიური"
        f" მიზანი:**"
        f" {st.session_state['daily_goal_done']}/{st.session_state['daily_goal_target']}"
        " კაზუსი"
    )
    progress_val = min(
        1.0,
        st.session_state["daily_goal_done"]
        / st.session_state["daily_goal_target"],
    )
    st.progress(progress_val)

  with h_col2:
    st.components.v1.html(render_svg_gauge(78, "საერთო მზაობა"), height=130)

  with h_col3:
    st.markdown("**🔖 შენახული კაზუსები:**")
    st.write(f"სულ შენახულია: **{len(st.session_state['bookmarks'])}**")
    if st.button("📖 შენახულების გადახედვა"):
      st.session_state["active_tab"] = "study"
      st.rerun()
  st.markdown("</div>", unsafe_allow_html=True)

  # სწრაფი ძიება
  st.markdown("<div class='card'>", unsafe_allow_html=True)
  st.subheader("🔍 სწრაფი ძიება ბაზაში")
  search_query = st.text_input(
      "შეიყვანეთ საკვანძო სიტყვა, მუხლი ან თემა:",
      placeholder="მაგ: 405-ე მუხლი, მკვლელობა, საჩივარი...",
  )

  if search_query.strip():
    search_results = [
        c
        for c in cases_db
        if search_query.lower() in c["question"].lower()
        or search_query.lower() in c["title"].lower()
        or search_query.lower() in c.get("article", "").lower()
    ]
    st.write(f"🔎 ნაპოვნია **{len(search_results)}** შედეგი:")
    for res in search_results:
      with st.expander(f"📌 {res['title']} [{res['code']}]"):
        st.write(f"**მუხლი:** {res.get('article', 'N/A')}")
        st.write(res["question"])
  st.markdown("</div>", unsafe_allow_html=True)

  # სექციების ბარათები
  cat_col1, cat_col2, cat_col3 = st.columns(3)
  with cat_col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📘 სამოქალაქო")
    c_count = len([c for c in cases_db if "სამოქალაქო" in c["code"]])
    st.write(f"ხელმისაწვდომია **{c_count}** კაზუსი.")
    if st.button("გადავლა ➔", key="btn_home_civ"):
      st.session_state["active_tab"] = "study"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

  with cat_col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📕 სისხლის")
    cr_count = len([c for c in cases_db if "სისხლის" in c["code"]])
    st.write(f"ხელმისაწვდომია **{cr_count}** კაზუსი.")
    if st.button("გადავლა ➔", key="btn_home_crim"):
      st.session_state["active_tab"] = "study"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

  with cat_col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📗 ადმინისტრაციული")
    a_count = len([c for c in cases_db if "ადმინისტრაციული" in c["code"]])
    st.write(f"ხელმისაწვდომია **{a_count}** კაზუსი.")
    if st.button("გადავლა ➔", key="btn_home_admin"):
      st.session_state["active_tab"] = "study"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 6. TAB 2: 📖 STUDY MODE
# ==============================================================================
elif st.session_state["active_tab"] == "study":
  st.title("📖 სწავლისა და ვარჯიშის გრაფა")

  all_codes = sorted(list(set([c["code"] for c in cases_db])))
  all_codes.insert(0, "ყველა კოდექსი / საგანი")

  selected_code = st.selectbox("📚 აირჩიეთ კოდექსი/საგანი:", all_codes)

  filtered_cases = cases_db
  if selected_code != "ყველა კოდექსი / საგანი":
    filtered_cases = [c for c in cases_db if c.get("code") == selected_code]

  st.write(f"📊 ნაპოვნია **{len(filtered_cases)}** კაზუსი/ტესტი.")

  if not filtered_cases:
    st.info("ამ სექციაში ჯერ არ არის ატვირთული კაზუსები.")
  else:
    for idx, case in enumerate(filtered_cases):
      with st.expander(
          f"📌 #{idx+1} {case['title']} ({case['code']})", expanded=(idx == 0)
      ):
        st.markdown(
            f"<span class='badge-code'>{case['code']}</span> "
            "<span"
            f" class='badge-article'>{case.get('article', 'სამართლებრივი საფუძველი')}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"### **ფაქტობრივი გარემოებები / კითხვა:**\n{case['question']}"
        )

        user_ans = st.radio(
            f"აირჩიეთ სწორი პასუხი #{idx+1}:",
            case["options"],
            key=f"study_radio_{case['id']}",
        )

        col_btn1, col_btn2 = st.columns()
        with col_btn1:
          if st.button("🔍 პასუხის შემოწმება", key=f"check_btn_{case['id']}"):
            correct_opt = case["options"][case["correct_index"]]
            if user_ans == correct_opt:
              st.success("✅ **სწორია!** ყოჩაღ!")
              st.session_state["daily_goal_done"] += 1
              user_progress["daily_goal_done"] = st.session_state[
                  "daily_goal_done"
              ]
              save_progress(user_progress)
            else:
              st.error(f"❌ **არასწორია.** სწორი პასუხია: {correct_opt}")

            st.info(
                f"💡 **სამართლებრივი დასაბუთება:**\n{case['explanation']}"
            )

        with col_btn2:
          is_bookmarked = case["id"] in st.session_state["bookmarks"]
          bm_label = "🔖 წაშლა" if is_bookmarked else "🔖 შენახვა"
          if st.button(bm_label, key=f"bm_btn_{case['id']}"):
            if is_bookmarked:
              st.session_state["bookmarks"].remove(case["id"])
            else:
              st.session_state["bookmarks"].append(case["id"])
            user_progress["bookmarks"] = st.session_state["bookmarks"]
            save_progress(user_progress)
            st.rerun()

# ==============================================================================
# 7. TAB 3: ⏱️ EXAM MODE
# ==============================================================================
elif st.session_state["active_tab"] == "exam":
  st.title("⏱️ ადვოკატთა გამოცდის სიმულაცია")

  col1, col2 = st.columns(2)
  with col1:
    all_codes = sorted(list(set([c["code"] for c in cases_db])))
    all_codes.insert(0, "ყველა კოდექსი (სრული გამოცდა)")
    exam_code = st.selectbox("📘 აირჩიეთ საგამოცდო სფერო:", all_codes)
  with col2:
    exam_time = st.selectbox(
        "⏳ საგამოცდო დრო:",
        ["30 წუთი", "1 საათი", "2 საათი", "3 საათი", "უვადო"],
    )

  exam_cases = cases_db
  if exam_code != "ყველა კოდექსი (სრული გამოცდა)":
    exam_cases = [c for c in cases_db if c.get("code") == exam_code]

  st.markdown("---")

  if not st.session_state["exam_active"]:
    st.write(f"🎯 ხელმისაწვდომია: **{len(exam_cases)}** კითხვა.")
    if st.button("🚀 გამოცდის დაწყება"):
      if not exam_cases:
        st.warning("კითხვები არ არის მოძიებული!")
      else:
        st.session_state["exam_active"] = True
        st.rerun()
  else:
    st.warning("⚠️ **გამოცდა მიმდინარეობს!**")
    with st.form("exam_form"):
      user_responses = {}
      for idx, case in enumerate(exam_cases):
        st.markdown(f"#### **კითხვა {idx+1}: {case['title']}** [{case['code']}]")
        st.write(case["question"])
        ans = st.radio(
            f"აირჩიეთ პასუხი #{idx+1}:",
            case["options"],
            key=f"exam_q_{idx}",
        )
        user_responses[case["id"]] = ans
        st.markdown("---")

      submit_exam = st.form_submit_button(
          "🏁 გამოცდის დასრულება და შეფასება"
      )

    if submit_exam:
      st.session_state["exam_active"] = False
      score = 0
      total = len(exam_cases)
      st.balloons()
      st.title("🎉 გამოცდის შედეგები")

      for idx, case in enumerate(exam_cases):
        user_selected = user_responses.get(case["id"])
        correct_ans = case["options"][case["correct_index"]]
        if user_selected == correct_ans:
          score += 1
          st.success(f"კითხვა {idx+1}: ✅ სწორია!")
        else:
          st.error(
              f"კითხვა {idx+1}: ❌ არასწორია. სწორია: '{correct_ans}'"
          )

      percentage = round((score / total) * 100, 1) if total > 0 else 0
      st.markdown(f"### 📊 საბოლოო ქულა: **{score} / {total}** ({percentage}%)")

# ==============================================================================
# 8. TAB 4: 📊 ANALYTICS MODE
# ==============================================================================
elif st.session_state["active_tab"] == "analytics":
  st.title("📊 პროგრესის ანალიტიკა")
  st.markdown("<div class='card'>", unsafe_allow_html=True)
  st.subheader("🎯 თქვენი სტატისტიკა")

  st.write(f"👤 **მომხმარებელი:** {st.session_state['user_name']}")
  st.write(f"🔥 **აქტიური Streak:** {st.session_state['streak']} დღე")
  st.write(
      f"✅ **დღეს ამოხსნილი კაზუსები:** {st.session_state['daily_goal_done']}"
  )
  st.write(
      "🔖 **შენახული კაზუსების რაოდენობა:**"
      f" {len(st.session_state['bookmarks'])}"
  )
  st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 9. TAB 5: 🔒 UPLOAD & GOOGLE DRIVE INTEGRATION
# ==============================================================================
elif st.session_state["active_tab"] == "upload":
  st.title("🔒 ადმინისტრირება & ფაილების ატვირთვა")

  if not st.session_state["admin_logged_in"]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    pwd_input = st.text_input(
        "პაროლი:", type="password", placeholder="შეიყვანეთ პაროლი"
    )
    if st.button("შესვლა"):
      if pwd_input == "legal":
        st.session_state["admin_logged_in"] = True
        st.success("ავტორიზაცია წარმატებულია!")
        st.rerun()
      else:
        st.error("❌ არასწორი პაროლი! (პაროლია: legal)")
    st.markdown("</div>", unsafe_allow_html=True)
  else:
    st.success("✅ ავტორიზებული ხართ როგორც ადმინისტრატორი!")

    col_left, col_right = st.columns()

    with col_left:
      st.markdown("<div class='card'>", unsafe_allow_html=True)
      st.subheader("📤 ახალი ფაილის დამატება")

      upload_code = st.selectbox(
          "აირჩიეთ კოდექსი/სფერო:",
          [
              "სამოქალაქო სამართალი",
              "სისხლის სამართალი",
              "ადმინისტრაციული სამართალი",
              "საკონსტიტუციო სამართალი",
              "საერთაშორისო სამართალი",
              "ადვოკატთა პროფესიული ეთიკა",
          ],
      )

      source_mode = st.radio(
          "აირჩიეთ დამატების გზა:",
          ["☁️ Google Drive-ის ლინკით", "📁 პირდაპირ ატვირთვა (<200MB)"],
      )

      if source_mode == "☁️ Google Drive-ის ლინკით":
        drive_url = st.text_input("ჩასვით Google Drive-ის გაზიარებული ლინკი:")
        if st.button("📥 Google Drive-იდან ჩამოტვირთვა და დამატება"):
          if drive_url:
            with st.spinner("ფაილი ჩამოიტვირთება Google Drive-იდან..."):
              data, err = download_gdrive_file(drive_url)
              if err:
                st.error(err)
              else:
                import io

                file_obj = io.BytesIO(data)
                parsed_cases = parse_uploaded_file(
                    file_obj, upload_code, file_name="gdrive_doc.docx"
                )
                cases_db.extend(parsed_cases)
                save_data(cases_db)
                st.success(
                    f"🎉 Google Drive-იდან წარმატებით დაემატა"
                    f" **{len(parsed_cases)}** კაზუსი!"
                )
                st.rerun()
          else:
            st.warning("გთხოვთ ჩასვათ Google Drive-ის ლინკი!")
      else:
        uploaded_file = st.file_uploader(
            "ატვირთეთ Word (.docx) ან Text (.txt) ფაილი:",
            type=["docx", "txt"],
        )
        if st.button("➕ ფაილის ატვირთვა და ბაზაში დამატება"):
          if uploaded_file is not None:
            parsed_cases = parse_uploaded_file(uploaded_file, upload_code)
            cases_db.extend(parsed_cases)
            save_data(cases_db)
            st.success(
                f"🎉 ფაილი წარმატებით დაემატა **{len(parsed_cases)}**"
                " კაზუსად/ტესტად!"
            )
            st.rerun()
          else:
            st.warning("გთხოვთ, ჯერ აირჩიოთ ფაილი!")
      st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
      st.markdown("<div class='card'>", unsafe_allow_html=True)
      st.subheader("🗑️ არსებული ფაილების/კაზუსების წაშლა")
      st.write(f"სისტემაში სულ არის **{len(cases_db)}** კაზუსი/ტესტი.")

      for idx, case in enumerate(cases_db):
        c_col1, c_col2 = st.columns()
        with c_col1:
          st.caption(
              f"📌 #{idx+1} {case['title']} ({case['code']}) | 📁"
              f" `{case.get('file_name', 'ნაგულისხმევი')}`"
          )
        with c_col2:
          if st.button("❌ წაშლა", key=f"del_case_{case['id']}"):
            cases_db.pop(idx)
            save_data(cases_db)
            st.success("წაშლილია!")
            st.rerun()
        st.markdown("---")

      if st.button("⚠️ ყველა მონაცემის საწყის მდგომარეობაში დაბრუნება"):
        save_data(DEFAULT_DATA)
        st.success("მონაცემები განახლდა!")
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)
