import streamlit as st
import re
import pdfplumber

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="wide")

ROLE_SKILLS = {
    "AI / ML Intern": ["python","machine learning","data analysis","numpy","pandas","scikit-learn","tensorflow","pytorch","git","github","sql"],
    "Data Analyst Intern": ["python","sql","excel","pandas","numpy","data analysis","data visualization","power bi","tableau","statistics"],
    "Python Developer Intern": ["python","git","github","sql","api","streamlit","flask","django","object oriented programming"],
    "Generative AI Intern": ["python","generative ai","prompt engineering","llm","nlp","api","git","github","machine learning"],
    "Software Developer Intern": ["python","java","sql","git","github","data structures","algorithms","oops","api"]
}

LABELS = {x:x.title() for skills in ROLE_SKILLS.values() for x in skills}
LABELS.update({"python":"Python","github":"GitHub","git":"Git","sql":"SQL","numpy":"NumPy","pandas":"Pandas","scikit-learn":"Scikit-learn","power bi":"Power BI","api":"APIs","llm":"LLMs","nlp":"NLP","oops":"OOP"})

def extract_pdf_text(file):
    try:
        file.seek(0)
        with pdfplumber.open(file) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages).strip()
    except Exception as e:
        st.error(f"Could not read the PDF: {e}")
        return ""

def normalize(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+#.\-/ ]+", " ", text.lower()))

def find_skills(text, skills):
    t = normalize(text)
    return [s for s in skills if re.search(r"(?<![a-z0-9])"+re.escape(s)+r"(?![a-z0-9])", t)]

def make_score(found, total, text):
    base = round(found / total * 100) if total else 0
    sections = ["education","skills","project","experience"]
    bonus = min(sum(x in normalize(text) for x in sections) * 2, 8)
    return min(base + bonus, 100)

def tips(text, missing):
    t = normalize(text)
    out = []
    if "project" not in t and "projects" not in t: out.append("Add a Projects section with 1–3 relevant projects.")
    if "github" not in t: out.append("Add your GitHub profile and project links.")
    if "education" not in t: out.append("Add a clear Education section with degree and graduation year.")
    if "summary" not in t and "objective" not in t: out.append("Add a short summary tailored to the target internship.")
    if missing: out.append("Learn missing skills before adding them to your resume.")
    return out or ["Your resume has the basic structure. Keep tailoring keywords to each internship."]

st.title("🤖 AI Resume Analyzer")
st.caption("Analyze a resume PDF against an internship role and get actionable feedback.")

with st.sidebar:
    st.header("🎯 Target Role")
    role = st.selectbox("Choose a role", list(ROLE_SKILLS))
    st.write("Upload → Extract → Match → Score → Improve")

uploaded = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])

if uploaded:
    text = extract_pdf_text(uploaded)
    if not text:
        st.warning("No readable text was found. Try a text-based PDF.")
        st.stop()

    required = ROLE_SKILLS[role]
    found = find_skills(text, required)
    missing = [s for s in required if s not in found]
    score = make_score(len(found), len(required), text)

    st.success("Resume analyzed successfully!")

    a,b,c = st.columns(3)
    a.metric("Resume Match", f"{score}%")
    b.metric("Skills Found", len(found))
    c.metric("Skills to Consider", len(missing))

    st.divider()
    left,right = st.columns(2)

    with left:
        st.subheader("✅ Skills Detected")
        if found:
            for s in found: st.write("• " + LABELS.get(s, s.title()))
        else: st.info("No target skills detected.")

    with right:
        st.subheader("📚 Skills to Consider")
        if missing:
            for s in missing: st.write("• " + LABELS.get(s, s.title()))
        else: st.success("All target skills were detected.")

    st.divider()
    st.subheader("💡 Resume Improvement Suggestions")
    for tip in tips(text, missing): st.write("• " + tip)

    st.write(f"Approximate word count: **{len(text.split())}**")

    with st.expander("🔍 View extracted resume text"):
        st.text(text)
else:
    st.info("Upload a PDF resume above to start.")
    st.markdown("### What this project demonstrates\n- PDF text extraction\n- NLP/text-processing basics\n- Skill matching\n- Rule-based scoring\n- Streamlit UI")
