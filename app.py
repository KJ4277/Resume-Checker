import os
import tempfile
import streamlit as st
from extract import extract_text
from scoring import review_cv
import history

st.set_page_config(page_title="CV Reviewer", page_icon="📝", layout="centered")

st.markdown("""
<style>
.block-container {max-width: 760px; padding-top: 2rem;}
#MainMenu, footer {visibility: hidden;}
.scorebox {display:flex; gap:28px; align-items:center; border:1px solid #D9E0EA;
           border-radius:14px; padding:22px 26px; margin:16px 0 8px;}
.ring {position:relative; width:150px; height:150px; flex:none;}
.ring svg {transform: rotate(-90deg);}
.ring .num {position:absolute; inset:0; display:flex; flex-direction:column;
            align-items:center; justify-content:center; font-size:2.4rem; font-weight:700;}
.ring .num small {font-size:0.8rem; font-weight:400; opacity:0.7;}
.ring circle.arc {stroke-dasharray: var(--c) var(--c); stroke-dashoffset: var(--c);
                  animation: fill 1.1s ease-out forwards;}
@keyframes fill {to {stroke-dashoffset: var(--off);}}
.verdict h3 {margin:0 0 4px;}
.verdict p {margin:0; opacity:0.75;}
.delta {display:inline-block; margin-top:10px; padding:3px 12px; border-radius:99px;
        font-weight:600; font-size:0.9rem;}
.up {background:#E3F4EC; color:#1F8A5B;}
.down {background:#FBE7E4; color:#C0392B;}
.same {background:#E9EDF3; color:#5C6B80;}
.bar .row {display:flex; justify-content:space-between; margin:10px 0 4px; font-weight:500;}
.bar .track {height:8px; background:#D9E0EA; border-radius:99px; overflow:hidden;}
.bar .fill {height:100%; border-radius:99px;}
.tip {padding:12px 16px; border:1px solid #D9E0EA; border-left:4px solid #2F5BEA;
      border-radius:8px; margin:8px 0;}
.tip.top {border-left-color:#C0392B;}
</style>
""", unsafe_allow_html=True)


def colour(pct):
    return "#1F8A5B" if pct >= 75 else "#C77700" if pct >= 50 else "#C0392B"


def verdict(p):
    if p >= 85:
        return "Interview-ready", "Strong across the board. Polish the small things below."
    if p >= 70:
        return "Good, with clear wins available", "A few targeted edits will lift this noticeably."
    if p >= 50:
        return "Needs work", "The basics are there. Impact and detail are holding it back."
    return "Early draft", "Start with the first few tips. They will move the score most."


def ring(p):
    r = 62
    c = 2 * 3.14159 * r
    off = c * (1 - p / 100)
    return (
        '<div class="ring">'
        '<svg width="150" height="150" viewBox="0 0 150 150">'
        f'<circle cx="75" cy="75" r="{r}" fill="none" stroke="#D9E0EA" stroke-width="12"/>'
        f'<circle class="arc" cx="75" cy="75" r="{r}" fill="none" stroke="{colour(p)}" '
        f'stroke-width="12" stroke-linecap="round" style="--c:{c:.1f};--off:{off:.1f}"/>'
        '</svg>'
        f'<div class="num">{p}%<small>CV score</small></div></div>'
    )


st.title("CV Reviewer")
st.caption("Upload your CV for a score out of 100 and a prioritised list of fixes. "
           "Edit it, upload again, and watch the score climb.")

file = st.file_uploader("Your CV (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"])
version = st.text_input("Version name (optional)", placeholder="e.g. v2, added numbers")

if st.button("Review my CV", type="primary", disabled=file is None):
    suffix = os.path.splitext(file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(file.read())
        path = f.name
    try:
        with st.spinner("Reading your CV..."):
            text = extract_text(path)
            if len(text.split()) < 30:
                st.error("Almost no text was found. If your CV is a scan or an image, "
                         "export it as a text-based PDF and try again.")
                st.stop()
            previous = history.load()
            result = review_cv(text)
        if result["percentage"] > 0:
            history.save(version or file.name, result["percentage"])
        st.session_state["result"] = result
        st.session_state["previous"] = previous[-1]["percentage"] if previous else None
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()
    finally:
        os.remove(path)

result = st.session_state.get("result")
if result:
    if not result["breakdown"]:
        st.warning(result.get("message", "Could not review this file."))
    else:
        p = result["percentage"]
        title, blurb = verdict(p)
        prev = st.session_state.get("previous")
        delta_html = ""
        if prev is not None:
            d = p - prev
            if d > 0:
                delta_html = f'<span class="delta up">+{d} since last version</span>'
            elif d < 0:
                delta_html = f'<span class="delta down">{d} since last version</span>'
            else:
                delta_html = '<span class="delta same">No change since last version</span>'

        st.markdown(
            f'<div class="scorebox">{ring(p)}<div class="verdict"><h3>{title}</h3>'
            f'<p>{blurb}</p>{delta_html}</div></div>',
            unsafe_allow_html=True,
        )
        st.caption(
            f"Detected: {result['field']} ({result['seniority']}). "
            f"Found {result['statements_found']} achievement or duty statements, "
            f"{result['statements_quantified']} with numbers, "
            f"{result['statements_with_results']} showing results."
        )

        st.subheader("Where the points come from")
        for name, value in result["breakdown"].items():
            earned, maximum = (float(x) for x in value.split(" / "))
            pct = earned / maximum * 100
            st.markdown(
                f'<div class="bar"><div class="row"><span>{name}</span>'
                f'<span>{value}</span></div><div class="track">'
                f'<div class="fill" style="width:{pct:.0f}%;background:{colour(pct)}"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        st.subheader("What to fix, most important first")
        for i, tip in enumerate(result["tips"]):
            cls = "tip top" if i < 2 else "tip"
            st.markdown(
                f'<div class="{cls}"><b>{tip["problem"]}</b><br>{tip["fix"]}</div>',
                unsafe_allow_html=True,
            )

h = history.load()
if len(h) > 1:
    st.subheader("Your progress")
    st.line_chart([x["percentage"] for x in h], height=220)
    c1, c2 = st.columns(2)
    c1.metric("First version", f'{h[0]["percentage"]}%')
    c2.metric("Latest", f'{h[-1]["percentage"]}%',
              delta=h[-1]["percentage"] - h[0]["percentage"])
if h:
    if st.button("Clear history"):
        history.clear()
        st.session_state.pop("result", None)
        st.rerun()