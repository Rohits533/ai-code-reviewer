import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import io

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="⭐",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { 
        background: linear-gradient(135deg, #0f1117 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    h1 { 
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5em !important;
        font-weight: 700 !important;
    }
    p { color: #888; text-align: center; }
    .review-box {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border-radius: 16px;
        padding: 25px;
        border-left: 4px solid #00d4ff;
        margin: 10px 0;
        animation: slideIn 0.5s ease;
    }
    .score-box {
        background: linear-gradient(135deg, #2e1e2e, #3e2a3e);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid #7b2ff7;
        text-align: center;
        margin: 10px 0;
    }
    .good-box {
        background: linear-gradient(135deg, #1e2e1e, #2a3e2a);
        border-radius: 16px;
        padding: 20px;
        border-left: 4px solid #a6e3a1;
        margin: 8px 0;
    }
    .bad-box {
        background: linear-gradient(135deg, #2e1e1e, #3e2a2a);
        border-radius: 16px;
        padding: 20px;
        border-left: 4px solid #f38ba8;
        margin: 8px 0;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton button {
        border-radius: 12px !important;
        font-weight: 500 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⭐ AI Code Reviewer</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px'>Paste any code — get a professional senior developer review</p>", unsafe_allow_html=True)
st.divider()

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

def generate_pdf(review, code, language):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                fontSize=18, textColor=colors.HexColor('#00d4ff'),
                                spaceAfter=10)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                               fontSize=10, spaceAfter=6, leading=14)
    code_style = ParagraphStyle('Code', parent=styles['Normal'],
                               fontSize=9, spaceAfter=8,
                               backColor=colors.HexColor('#f0f0f0'),
                               leftIndent=10, rightIndent=10)
    story = []
    story.append(Paragraph(f"Code Review Report — {language}", title_style))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Code Reviewed:", title_style))
    for line in code.split('\n')[:30]:
        story.append(Paragraph(line or " ", code_style))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Review Findings:", title_style))
    for line in review.split('\n'):
        if line.strip():
            story.append(Paragraph(line.strip(), body_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

col1, col2 = st.columns([3, 1])
with col1:
    language = st.selectbox("Programming Language:", [
        "Python", "JavaScript", "Java", "C++", "C",
        "TypeScript", "SQL", "HTML/CSS", "Other"
    ])
with col2:
    review_type = st.selectbox("Review Focus:", [
        "Full Review",
        "Bug Detection",
        "Security",
        "Performance",
        "Best Practices"
    ])

code_input = st.text_area(
    "Paste your code here:",
    height=300,
    placeholder="def calculate_average(numbers):\n    total = 0\n    for n in numbers:\n        total = total + n\n    return total / len(numbers)"
)

if st.button("🔍 Review My Code", use_container_width=True):
    if code_input:
        with st.spinner("Analyzing your code like a senior developer..."):
            prompt = f"""You are a senior software engineer doing a {review_type} for {language} code.

Review this code and provide feedback in exactly this format:

SCORE: X/10

SUMMARY:
2-3 sentence overall assessment

GOOD THINGS:
- Point 1
- Point 2
- Point 3

ISSUES FOUND:
- Issue 1
- Issue 2
- Issue 3

SECURITY CONCERNS:
- Any security issues or "None found"

PERFORMANCE:
- Any performance improvements or "Looks good"

IMPROVED CODE:
Write the improved version of the code here

Code to review:
{code_input}"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are an expert {language} developer doing thorough code reviews. Be specific and helpful."},
                    {"role": "user", "content": prompt}
                ]
            )
            review = response.choices[0].message.content

        score = 7
        for line in review.split('\n'):
            if line.startswith('SCORE:'):
                try:
                    score = int(line.replace('SCORE:', '').replace('/10', '').strip())
                except:
                    score = 7

        st.markdown(f"""
        <div class="score-box">
            <p style="color:#7b2ff7; font-size:13px; font-weight:600; margin:0">CODE QUALITY SCORE</p>
            <p style="color:#ffffff; font-size:52px; font-weight:700; margin:8px 0">{score}/10</p>
            <p style="color:#888; font-size:13px; margin:0">
                {"🔥 Excellent code!" if score >= 8 else "👍 Good code!" if score >= 6 else "📚 Needs improvement"}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📋 Full Review")
        st.markdown(f"""
        <div class="review-box">
            <p style="color:#cdd6f4; font-size:14px; line-height:1.8; white-space:pre-wrap">{review}</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        pdf = generate_pdf(review, code_input, language)
        st.download_button(
            label="📥 Download Review as PDF",
            data=pdf,
            file_name=f"code_review_{language}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Please paste some code first!")

st.markdown("<p style='margin-top:20px'>Built by Rohit • Powered by Groq + Llama 3</p>", unsafe_allow_html=True)
