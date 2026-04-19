import streamlit as st
import json

st.set_page_config(
    page_title="VuGen Script Generator",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background-color: #0d0d0d;
        color: #e8e8e8;
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
    }

    .main-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #f0f0f0;
        letter-spacing: -1px;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }

    .main-subtitle {
        color: #00e5a0;
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .screen-header {
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #00e5a0;
        margin-bottom: 1rem;
    }

    .api-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #888;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        margin-top: 0.8rem;
    }

    .preview-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #555;
        margin-bottom: 0.5rem;
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: #1e1e1e !important;
        border: 1px solid #333 !important;
        color: #e8e8e8 !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00e5a0 !important;
        box-shadow: 0 0 0 1px #00e5a0 !important;
    }

    .stButton > button {
        background: #00e5a0 !important;
        color: #0d0d0d !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background: #00ffb3 !important;
        transform: translateY(-1px) !important;
    }

    label, .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label {
        color: #888 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-family: 'Syne', sans-serif !important;
    }

    .divider {
        border: none;
        border-top: 1px solid #222;
        margin: 1.5rem 0;
    }

    .screen-block {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)


def json_to_c_string(json_input: str) -> str:
    try:
        parsed = json.loads(json_input)
        compact = json.dumps(parsed, separators=(',', ':'))
    except json.JSONDecodeError:
        compact = json_input.strip()
    return compact.replace('\\', '\\\\').replace('"', '\\"')


def generate_vugen_script(bp_number: int, screen_number: int, screen_name: str, apis: list) -> str:
    bp_str = str(bp_number).zfill(2)
    sc_str = str(screen_number).zfill(2)
    func_name = f"BP{bp_str}_{sc_str}_{screen_name}"

    lines = []
    lines.append(f"{func_name}()")
    lines.append("{")
    lines.append(f'  lr_save_string("{func_name}", "stepTransaction");')
    lines.append(f'  lr_start_transaction(lr_eval_string("{{stepTransaction}}"));')
    lines.append("")

    for i, api in enumerate(apis, start=1):
        api_number = str(i).zfill(3)
        api_name = api["name"].strip()
        sub_transaction = f"{bp_str}_{sc_str}_{api_number}_{api_name}"

        lines.append(f'  lr_save_string("{sub_transaction}", "subTransaction");')
        lines.append(f'  lr_start_sub_transaction(lr_eval_string("{{subTransaction}}"), lr_eval_string("{{stepTransaction}}"));')
        lines.append("")
        lines.append(f'  Message_Response();')
        lines.append("")
        lines.append(f'  web_add_header("{api["header_key"].strip()}", "{api["header_value"].strip()}");')
        lines.append("")
        lines.append(f'  web_custom_request(lr_eval_string("{{subTransaction}}"),')
        lines.append(f'    "URL={api["url"].strip()}",')
        lines.append(f'    "Method={api["method"]}",')
        lines.append(f'    "TargetFrame=",')
        lines.append(f'    "Resource=0",')
        lines.append(f'    "Referer=",')
        lines.append(f'    "Mode=HTML",')
        lines.append(f'    "EncType=Application/json",')
        lines.append(f'    "Snapshot=t{i}.inf",')
        body_str = json_to_c_string(api["body"].strip()) if api["body"].strip() else ""
        lines.append(f'    "Body={body_str}",')
        lines.append(f'    LAST);')
        lines.append("")
        lines.append(f'  Validation_Response();')
        lines.append(f'  lr_end_sub_transaction(lr_eval_string("{{subTransaction}}"));')
        lines.append("")

    lines.append(f'  lr_end_transaction(lr_eval_string("{{stepTransaction}}"));')
    lines.append("")
    lines.append("  return 0;")
    lines.append("}")
    return "\n".join(lines)


# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
if "num_screens" not in st.session_state:
    st.session_state.num_screens = 1
if "generated_scripts" not in st.session_state:
    st.session_state.generated_scripts = []
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">VuGen Script Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">⚡ LoadRunner · Automated Script Builder</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown("### 🗂 Screens & APIs")

    rc = st.session_state.reset_counter
    all_screens_data = []

    for s in range(st.session_state.num_screens):
        st.markdown(f'<div class="screen-block">', unsafe_allow_html=True)
        st.markdown(f'<div class="screen-header">▸ Screen {s + 1}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            bp_num = st.number_input("BP Number", min_value=1, max_value=99, value=1, step=1, key=f"bp_{s}_{rc}")
        with col2:
            sc_num = st.number_input("Screen Number", min_value=1, max_value=99, value=s + 1, step=1, key=f"sc_{s}_{rc}")
        with col3:
            sc_name = st.text_input("Screen Name", placeholder="e.g. Login", key=f"sname_{s}_{rc}")

        num_apis = st.number_input("How many APIs?", min_value=1, max_value=99, value=1, step=1, key=f"napi_{s}_{rc}")

        apis = []
        for i in range(int(num_apis)):
            st.markdown(f'<div class="api-number">API {i + 1}</div>', unsafe_allow_html=True)
            a1, a2 = st.columns([2, 1])
            with a1:
                api_name = st.text_input("API Name", key=f"aname_{s}_{i}_{rc}", placeholder="e.g. api_login")
            with a2:
                method = st.selectbox("Method", ["POST", "GET", "PUT", "DELETE", "PATCH"], key=f"method_{s}_{i}_{rc}")
            api_url = st.text_input("URL", key=f"url_{s}_{i}_{rc}", placeholder="https://api.example.com/endpoint")
            h1, h2 = st.columns([1, 2])
            with h1:
                header_key = st.text_input("Header Key", key=f"hkey_{s}_{i}_{rc}", placeholder="Authorization")
            with h2:
                header_value = st.text_input("Header Value", key=f"hval_{s}_{i}_{rc}", placeholder="Bearer <token>")
            body = st.text_area("Request Body (JSON)", key=f"body_{s}_{i}_{rc}",
                                placeholder='{"username": "test"}', height=80)
            apis.append({
                "name": api_name,
                "method": method,
                "url": api_url,
                "header_key": header_key,
                "header_value": header_value,
                "body": body
            })

        all_screens_data.append({
            "bp_number": int(bp_num),
            "screen_number": int(sc_num),
            "screen_name": sc_name.strip(),
            "apis": apis
        })

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    btn1, btn2 = st.columns([1, 1])
    with btn1:
        if st.button("＋ Add Screen", use_container_width=True):
            st.session_state.num_screens += 1
            st.rerun()
    with btn2:
        if st.button("－ Remove Last Screen", use_container_width=True):
            if st.session_state.num_screens > 1:
                st.session_state.num_screens -= 1
                st.rerun()

with right_col:
    st.markdown("### 📄 Generated Scripts")

    gen_col, reset_col = st.columns([2, 1])
    with gen_col:
        generate_btn = st.button("⚡ Generate All Scripts", use_container_width=True)
    with reset_col:
        if st.button("🔄 Reset All", use_container_width=True):
            st.session_state.num_screens = 1
            st.session_state.generated_scripts = []
            st.session_state.reset_counter += 1
            st.rerun()

    if generate_btn:
        errors = []
        for idx, screen in enumerate(all_screens_data):
            if not screen["screen_name"]:
                errors.append(f"Screen {idx + 1}: Screen name kosong.")
            for j, api in enumerate(screen["apis"]):
                if not api["name"].strip():
                    errors.append(f"Screen {idx + 1}, API {j + 1}: API name kosong.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            scripts = []
            for screen in all_screens_data:
                script = generate_vugen_script(
                    bp_number=screen["bp_number"],
                    screen_number=screen["screen_number"],
                    screen_name=screen["screen_name"],
                    apis=screen["apis"]
                )
                scripts.append((screen["screen_name"], script))
            st.session_state.generated_scripts = scripts

    if st.session_state.generated_scripts:
        all_combined = "\n\n".join(
            [f"/* ===== {name} ===== */\n{script}" for name, script in st.session_state.generated_scripts]
        )

        st.download_button(
            label="⬇ Download All Scripts (.c)",
            data=all_combined,
            file_name="vugen_scripts.c",
            mime="text/plain",
            use_container_width=True
        )

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        for name, script in st.session_state.generated_scripts:
            st.markdown(f'<div class="preview-label">▸ {name}</div>', unsafe_allow_html=True)
            st.code(script, language="c")
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            border: 1px dashed #2a2a2a;
            border-radius: 10px;
            padding: 3rem 2rem;
            text-align: center;
            color: #444;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            margin-top: 1rem;
        ">
            Fill in the screens on the left<br>then hit <span style="color:#00e5a0">⚡ Generate All Scripts</span>
        </div>
        """, unsafe_allow_html=True)
