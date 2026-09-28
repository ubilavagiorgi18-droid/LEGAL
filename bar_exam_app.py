import json
import os
import re
import time
import urllib.request
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="ადვოკატთა გამოცდის პორტალი",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Styling (iOS Glassmorphism & Modern UI)
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
        transform: translateY(-1px);
    }
    .card {
        background-color: #F8FAFC;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
    }
    .badge-code {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. LOGO DETECTION & SIDEBAR INTEGRATION
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

if found_logo:
  st.sidebar.image(found_logo, use_container_width=True)

# ==============================================================================
# 3. DATA PERSISTENCE & GOOGLE DRIVE LOADER
# ==============================================================================
DATA_FILE = "bar_exam_data.json"

DEFAULT_DATA = [
    {
        "id": "case_1",
        "title": "ხელშეკრულების შეწყვეტა და ზიანის ანაზღაურება",
        "code": "სამოქალაქო სამართალი",
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


def download_gdrive_file(url):
  """Google Drive-იდან დიდი ფაილების ჩამოტვირთვა."""
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


def parse_uploaded_file(uploaded_file, selected_code, file_name=None):
  """Word / Text ფაილების დამუშავება კაზუსებად."""
  if file_name is None:
    file_name = getattr(uploaded_file, "name", "gdrive_file.docx")

  content_text = ""
  if file_name.endswith(".docx"):
    try:
      import docx

      doc = docx.Document(uploaded_file)
      paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
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

  blocks = [b.strip() for b in content_text.split("\n\n") if b.strip()]
  new_cases = []

  if len(blocks) >= 1:
    for idx, block in enumerate(blocks):
      lines = [l.strip() for l in block.split("\n") if l.strip()]
      title = (
          lines[0][:60] if lines else f"კაზუსი/ტესტი {idx+1} ({file_name})"
      )
      question = "\n".join(lines)
      new_cases.append({
          "id": f"upload_{int(time.time())}_{idx}",
          "title": f"კაზუსი: {title}",
          "code": selected_code,
          "file_name": file_name,
          "question": question,
          "options": [
              "ა) სწორია / დასაშვებია (სამართლებრივი საფუძვლით)",
              "ბ) არასწორია / უსაფუძვლოა",
              "გ) ნაწილობრივ მართებულია",
              "დ) საჭიროებს დამატებით მტკიცებულებებს",
          ],
          "correct_index": 0,
          "explanation": (
              f"ანალიზი დაყრდნობილია ატვირთულ ფაილზე: {file_name}. იხ."
              f" {selected_code}-ის შესაბამისი მუხლები."
          ),
      })
  return new_cases


# ==============================================================================
# 4. SESSION STATE & WELCOME SCREEN
# ==============================================================================
if "user_name" not in st.session_state:
  st.session_state["user_name"] = None
if "admin_logged_in" not in st.session_state:
  st.session_state["admin_logged_in"] = False
if "exam_active" not in st.session_state:
  st.session_state["exam_active"] = False

cases_db = load_data()

if not st.session_state["user_name"]:
  st.markdown(
      "<h1 class='main-header'>⚖️ ადვოკატთა გამოცდის მოსამზადებელი"
      " პორტალი</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p class='sub-header'>მოემზადეთ საქართველოს ადვოკატთა ასოციაციის"
      " საკვალიფიკაციო გამოცდისთვის</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👋 კეთილი იყოს თქვენი მობრძანება!")
    st.write(
        "გთხოვთ, შეიყვანოთ თქვენი სახელი და გვარი სისტემაში შესასვლელად:"
    )

    name_input = st.text_input(
        "თქვენი სახელი და გვარი:", placeholder="მაგ: გიორგი ბერიძე"
    )
    if st.button("🚀 მთავარ მენიუში შესვლა"):
      if name_input.strip():
        st.session_state["user_name"] = name_input.strip()
        st.rerun()
      else:
        st.warning("გთხოვთ შეიყვანოთ სახელი!")
    st.markdown("</div>", unsafe_allow_html=True)

  st.stop()

# ==============================================================================
# 5. NAVIGATION & SIDEBAR
# ==============================================================================
st.sidebar.title(f"👤 {st.session_state['user_name']}")
st.sidebar.caption("ადვოკატობის კანდიდატი")

if st.sidebar.button("🚪 გამოსვლა (სახელის შეცვლა)"):
  st.session_state["user_name"] = None
  st.session_state["admin_logged_in"] = False
  st.session_state["exam_active"] = False
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📌 ნავიგაცია")
menu_choice = st.sidebar.radio(
    "აირჩიეთ სექცია:",
    ["📖 სწავლის გრაფა", "⏱️ გამოცდის გრაფა", "🔒 ატვირთვის/მართვის გრაფა"],
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **შენიშვნა:** ატვირთვის გრაფის პაროლია: `legal`")

# ==============================================================================
# 6. 📖 STUDY MODE
# ==============================================================================
if menu_choice == "📖 სწავლის გრაფა":
  st.title("📖 სწავლისა და ვარჯიშის გრაფა")
  st.write(
      "აქ შეგიძლიათ დეტალურად გაიაროთ კაზუსები და ტესტები, გადაამოწმოთ"
      " პასუხები და გაეცნოთ განმარტებებს."
  )

  all_codes = sorted(list(set([c["code"] for c in cases_db])))
  all_codes.insert(0, "ყველა კოდექსი / საგანი")

  selected_code = st.selectbox("📚 აირჩიეთ კოდექსი/საგანი:", all_codes)

  filtered_cases = cases_db
  if selected_code != "ყველა კოდექსი / საგანი":
    filtered_cases = [c for c in cases_db if c.get("code") == selected_code]

  st.write(f"📊 ნაპოვნია **{len(filtered_cases)}** კაზუსი/ტესტი.")

  if not filtered_cases:
    st.info(
        "ამ სექციაში ჯერ არ არის ატვირთული კაზუსები. გადადით 'ატვირთვის"
        " გრაფაში' Word/Google Drive ფაილის დასამატებლად."
    )
  else:
    for idx, case in enumerate(filtered_cases):
      with st.expander(
          f"📌 კაზუსი #{idx+1}: {case['title']} ({case['code']})",
          expanded=(idx == 0),
      ):
        st.markdown(
            f"<span class='badge-code'>{case['code']}</span> | 📁 ფაილი:"
            f" `{case.get('file_name', 'სისტემური')}`",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"### **კითხვა / ფაქტობრივი გარემოებები:**\n{case['question']}"
        )

        user_ans = st.radio(
            f"აირჩიეთ სწორი პასუხი კაზუსისთვის #{idx+1}:",
            case["options"],
            key=f"study_radio_{case['id']}",
        )

        if st.button("🔍 პასუხის შემოწმება", key=f"check_btn_{case['id']}"):
          correct_opt = case["options"][case["correct_index"]]
          if user_ans == correct_opt:
            st.success("✅ **სწორია!** ყოჩაღ!")
          else:
            st.error(f"❌ **არასწორია.** სწორი პასუხია: {correct_opt}")

          st.info(
              f"💡 **სამართლებრივი დასაბუთება:**\n{case['explanation']}"
          )

# ==============================================================================
# 7. ⏱️ EXAM MODE
# ==============================================================================
elif menu_choice == "⏱️ გამოცდის გრაფა":
  st.title("⏱️ ადვოკატთა გამოცდის სიმულაცია")
  st.write(
      "გაიარეთ გამოცდა რეალურ დროში, აირჩიეთ სასურველი ხანგრძლივობა და"
      " კოდექსი."
  )

  col1, col2 = st.columns(2)
  with col1:
    all_codes = sorted(list(set([c["code"] for c in cases_db])))
    all_codes.insert(0, "ყველა კოდექსი (სრული გამოცდა)")
    exam_code = st.selectbox("📘 აირჩიეთ საგამოცდო კოდექსი/სფერო:", all_codes)

  with col2:
    exam_time = st.selectbox(
        "⏳ აირჩიეთ საგამოცდო დრო:",
        [
            "30 წუთი",
            "1 საათი",
            "2 საათი",
            "3 საათი (სრული საგამოცდო დრო)",
            "უვადო (ვარჯიშის რეჟიმი)",
        ],
    )

  exam_cases = cases_db
  if exam_code != "ყველა კოდექსი (სრული გამოცდა)":
    exam_cases = [c for c in cases_db if c.get("code") == exam_code]

  st.markdown("---")

  if not st.session_state["exam_active"]:
    st.write(
        f"🎯 საგამოცდო ბაზაში ხელმისაწვდომია: **{len(exam_cases)}** კითხვა."
    )
    if st.button("🚀 გამოცდის დაწყება"):
      if not exam_cases:
        st.warning("არჩეულ კოდექსში კითხვები არ არის მოძიებული!")
      else:
        st.session_state["exam_active"] = True
        st.session_state["exam_answers"] = {}
        st.session_state["exam_start_time"] = time.time()
        st.rerun()

  else:
    st.warning(f"⚠️ **გამოცდა მიმდინარეობს!** დრო: {exam_time}")

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
          st.success(f"კითხვა {idx+1}: ✅ სწორია! ({case['title']})")
        else:
          st.error(
              f"კითხვა {idx+1}: ❌ არასწორია. თქვენი: '{user_selected}' |"
              f" სწორია: '{correct_ans}'"
          )

      percentage = round((score / total) * 100, 1) if total > 0 else 0
      st.markdown(f"### 📊 საბოლოო ქულა: **{score} / {total}** ({percentage}%)")

      if percentage >= 75:
        st.success("🌟 **გილოცავთ! თქვენ წარმატებით ჩააბარეთ გამოცდა!**")
      else:
        st.warning(
            "📚 **რეკომენდაცია:** გირჩევთ კიდევ გაიაროთ სწავლის გრაფა მასალის"
            " უკეთ ასათვისებლად."
        )

      if st.button("🔄 ახალი გამოცდის დაწყება"):
        st.rerun()

# ==============================================================================
# 8. 🔒 ADMIN UPLOAD & GOOGLE DRIVE INTEGRATION
# ==============================================================================
elif menu_choice == "🔒 ატვირთვის/მართვის გრაფა":
  st.title("🔒 ადმინისტრირება & ფაილების ატვირთვა / წაშლა")
  st.write(
      "ამ სექციაში შეგიძლიათ ატვირთოთ Word/ტექსტური კაზუსები ან ჩამოტვირთოთ"
      " Google Drive-ის ლინკით."
  )

  if not st.session_state["admin_logged_in"]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔑 შეიყვანეთ ადმინისტრატორის პაროლი")
    pwd_input = st.text_input(
        "პაროლი:", type="password", placeholder="შეიყვანეთ პაროლი"
    )
    if st.button("შესვლა"):
      if pwd_input == "legal":
        st.session_state["admin_logged_in"] = True
        st.success("ავტორიზაცია წარმატებულია!")
        st.rerun()
      else:
        st.error("❌ არასწორი პაროლი! პაროლია: legal")
    st.markdown("</div>", unsafe_allow_html=True)
  else:
    st.success("✅ ავტორიზებული ხართ როგორც ადმინისტრატორი!")

    col_left, col_right = st.columns([1, 1])

    with col_left:
      st.markdown("<div class='card'>", unsafe_allow_html=True)
      st.subheader("📤 ახალი ფაილის დამატება")

      upload_code = st.selectbox(
          "აირჩიეთ კოდექსი/სფერო ატვირთული ფაილისთვის:",
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
                f"🎉 ფაილი `{uploaded_file.name}` წარმატებით აიტვირთა და"
                f" დაემატა **{len(parsed_cases)}** კაზუსი/ტესტი!"
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
        c_col1, c_col2 = st.columns([3, 1])
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
