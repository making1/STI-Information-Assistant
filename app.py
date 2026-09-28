import re
import streamlit as st

st.set_page_config(page_title="STI Information Assistant", page_icon="🩺")

CONTENT = {
    "gonorrhoea": {
        "summary": "Gonorrhoea is an STI caused by Neisseria gonorrhoeae. It can affect the genitals, rectum and throat.",
        "symptoms": "Some people have no noticeable symptoms. Possible symptoms include pain or burning when urinating, genital discharge, pelvic pain or testicular pain.",
        "testing": "Symptoms alone cannot confirm gonorrhoea. Appropriate testing should be discussed with a qualified health professional.",
        "prevention": "Correct and consistent condom use, testing when indicated, treatment, and appropriate partner management can reduce transmission.",
        "treatment": "Gonorrhoea is treatable with appropriate antibiotics. Treatment should follow current clinical guidance and professional prescription."
    },
    "general": {
        "summary": "STIs are infections transmitted through sexual contact. Different infections have different symptoms, tests, treatments and prevention options.",
        "symptoms": "STIs can cause discharge, painful urination, sores, rash or pelvic pain, but some infections cause no noticeable symptoms.",
        "testing": "Testing depends on the infection, symptoms and exposure. A health professional can recommend appropriate tests.",
        "prevention": "Condom use, vaccination where applicable, testing, treatment and communication with partners are important prevention measures.",
        "treatment": "Treatment depends on the specific infection. Do not self-prescribe antibiotics based only on symptoms."
    }
}

INTENTS = {
    "symptom_inquiry": ["symptom","sign","discharge","burn","pain","itch","sore","rash","urinate"],
    "testing": ["test","testing","screen","screening","laboratory","check"],
    "treatment": ["treat","treatment","cure","medicine","medication","antibiotic"],
    "prevention": ["prevent","prevention","avoid","protect","condom","safe sex"],
    "transmission": ["transmit","transmission","spread","catch","oral sex","partner"],
    "general_information": ["what is","explain","information","about"]
}

SYMPTOMS = {
    "dysuria": ["burning when urinating","pain when urinating","painful urination","burn when i pee"],
    "genital_discharge": ["discharge","genital discharge","penile discharge","vaginal discharge"],
    "genital_pain": ["genital pain"],
    "pelvic_pain": ["pelvic pain","lower abdominal pain"],
    "testicular_pain": ["testicular pain","testicle pain"],
    "genital_sores": ["genital sore","genital sores","genital ulcer"],
    "itching": ["itch","itching"],
    "rash": ["rash"],
    "fever": ["fever","high temperature"]
}

DISEASES = {
    "gonorrhoea": ["gonorrhoea","gonorrhea"],
    "chlamydia": ["chlamydia"],
    "syphilis": ["syphilis"],
    "hiv": ["hiv"],
    "herpes": ["herpes"],
    "hpv": ["hpv"],
    "trichomoniasis": ["trichomoniasis"]
}

URGENT = ["severe pain","fainting","unconscious","difficulty breathing","heavy bleeding","severe bleeding","emergency"]

def intent(text):
    t = text.lower()
    scores = {k: sum(term in t for term in v) for k,v in INTENTS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "general_information"

def diseases(text):
    t = text.lower()
    return [d for d, terms in DISEASES.items() if any(x in t for x in terms)]

def symptoms(text):
    t = text.lower()
    return [s for s, terms in SYMPTOMS.items() if any(x in t for x in terms)]

def duration(text):
    m = re.search(r"\b\d+\s*(day|days|week|weeks|month|months)\b", text.lower())
    return m.group(0) if m else None

def exposures(text):
    t = text.lower()
    out=[]
    if "unprotected sex" in t or "without a condom" in t: out.append("unprotected sexual exposure")
    if "oral sex" in t: out.append("oral sex")
    if "new partner" in t: out.append("new sexual partner")
    return out

def response(i, ds, ss, dur, ex):
    topic = "gonorrhoea" if "gonorrhoea" in ds else "general"
    c = CONTENT[topic]
    parts = [f"### {topic.title()}", c["summary"]]
    if ss:
        parts.append("**Symptoms identified:** " + ", ".join(x.replace("_"," ") for x in ss) + ". These symptoms do not by themselves confirm an STI.")
    if dur: parts.append("**Reported duration:** " + dur)
    if ex: parts.append("**Reported exposure:** " + "; ".join(ex))
    if i == "testing": parts.append("**Testing:** " + c["testing"])
    elif i == "treatment": parts.append("**Treatment:** " + c["treatment"])
    elif i == "prevention": parts.append("**Prevention:** " + c["prevention"])
    elif i == "transmission": parts.append("Transmission depends on the infection and type of exposure. Appropriate testing and professional advice can help.")
    else:
        parts += ["**Symptoms:** " + c["symptoms"], "**Testing:** " + c["testing"], "**Prevention:** " + c["prevention"]]
    parts.append("**Safety:** This prototype provides education and information extraction; it does not diagnose infection or prescribe treatment.")
    return "\n\n".join(parts)

st.title("🩺 STI Information Assistant")
st.caption("Prototype: NLP-style extraction of meaningful information from STI inquiries")

st.warning("Do not enter names, phone numbers, national ID numbers, exact addresses, or other directly identifying information.")

examples = ["Select an example","What is gonorrhoea?","I have burning when urinating and discharge. Could this be gonorrhoea?","How can I prevent gonorrhoea?","Where can I get tested for an STI?","Can gonorrhoea be treated?","Can an STI spread through oral sex?"]
choice = st.selectbox("Select your Inquary", examples)
q = st.text_area("Enter your STI question", "" if choice=="Select an example" else choice, height=120)

if st.button("Analyze inquiry", type="primary"):
    if not q.strip():
        st.warning("Enter an inquiry first.")
    else:
        i, ds, ss, dur, ex = intent(q), diseases(q), symptoms(q), duration(q), exposures(q)
        urgent = any(x in q.lower() for x in URGENT)
        st.subheader("Extracted information")
        st.write("**Intent:**", i.replace("_"," ").title())
        st.write("**Possible STI/topic:**", ", ".join(ds) if ds else "Not specified")
        st.write("**Symptoms:**", ", ".join(x.replace("_"," ") for x in ss) if ss else "None identified")
        st.write("**Duration:**", dur or "Not specified")
        st.write("**Exposure:**", ", ".join(ex) if ex else "Not specified")
        if urgent: st.error("Potentially urgent wording detected. Seek prompt professional medical care.")
        elif ss: st.warning("Symptoms were identified. The system cannot determine the diagnosis; clinical evaluation/testing may be appropriate.")
        st.subheader("Educational information")
        st.markdown(response(i,ds,ss,dur,ex))
        st.subheader("Feedback")
        st.radio("Was this useful?", ["Yes","Partly","No"], horizontal=True)
        st.caption("For a production system, replace the prototype rules with validated, expert-reviewed NLP models and current clinical guidance.")
