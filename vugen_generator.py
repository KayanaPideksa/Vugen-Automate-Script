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

    .section-card {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .api-card {
        background: #1a1a1a;
        border: 1px solid #2e2e2e;
        border-left: 3px solid #00e5a0;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    .api-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #00e5a0;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .code-output {
        font-family: 'JetBrains Mono', monospace;
        background: #0a0a0a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 1.5rem;
        font-size: 0.82rem;
        line-height: 1.7;
        color: #c8c8c8;
        white-space: pre;
        overflow-x: auto;
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

    .stAlert {
        background: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #e8e8e8 !important;
    }
</style>
""", unsafe_allow_html=True)


def json_to_c_string(json_input: str) -> str:
    """Convert JSON string to C-style escaped string."""
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
    step_transaction = func_name

    lines = []
    lines.append(f"{func_name}()")
    lines.append("{")
    lines.append(f'  lr_save_string("{step_transaction}", "stepTransaction");')
    lines.append(f'  lr_start_transaction(lr_eval_string("{{stepTransaction}}"));')
    lines.append("")

    for i, api in enumerate(apis, start=1):
        api_number = str(i).zfill(3)
        api_name = api["name"].strip()
        sub_transaction = f"{bp_str}_{sc_str}_{api_number}_{api_name}"
        method = api["method"]
        url = api["url"].strip()
        header_key = api["header_key"].strip()
        header_value = api["header_value"].strip()
        body_raw = api["body"].strip()
        body_str = json_to_c_string(body_raw) if body_raw else ""
        snapshot_num = i

        lines.append(f'  lr_save_string("{sub_transaction}", "subTransaction");')
        lines.append(f'  lr_start_sub_transaction(lr_eval_string("{{subTransaction}}"), lr_eval_string("{{stepTransaction}}"));')
        lines.append("")
        lines.append(f'  Message_Response();')
        lines.append("")
        lines.append(f'  web_add_header("{header_key}", "{header_value}");')
        lines.append("")
        lines.append(f'  web_custom_request(lr_eval_string("{{subTransaction}}"),')
        lines.append(f'    "URL={url}",')
        lines.append(f'    "Method={method}",')
        lines.append(f'    "TargetFrame=",')
        lines.append(f'    "Resource=0",')
        lines.append(f'    "Referer=",')
        lines.append(f'    "Mode=HTML",')
        lines.append(f'    "EncType=Application/json",')
        lines.append(f'    "Snapshot=t{snapshot_num}.inf",')
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


# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">VuGen Script Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">⚡ LoadRunner · Automated Script Builder</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── LEFT / RIGHT COLUMNS ─────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown("### 🗂 Business Process Info")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        bp_number = st.number_input("BP Number", min_value=1, max_value=99, value=1, step=1)
    with col2:
        screen_number = st.number_input("Screen Number", min_value=1, max_value=99, value=1, step=1)
    with col3:
        screen_name = st.text_input("Screen Name", placeholder="e.g. Login")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("### 🔌 APIs in this Screen")

    num_apis = st.number_input("How many APIs?", min_value=1, max_value=20, value=1, step=1)

    apis = []
    for i in range(int(num_apis)):
        st.markdown(f'<div class="api-number">▸ API {i+1}</div>', unsafe_allow_html=True)
        with st.container():
            a1, a2 = st.columns([2, 1])
            with a1:
                api_name = st.text_input(f"API Name", key=f"name_{i}", placeholder=f"e.g. api_login")
            with a2:
                method = st.selectbox(f"Method", ["POST", "GET", "PUT", "DELETE", "PATCH"], key=f"method_{i}")

            api_url = st.text_input(f"URL", key=f"url_{i}", placeholder="https://api.example.com/endpoint")

            h1, h2 = st.columns([1, 2])
            with h1:
                header_key = st.text_input(f"Header Key", key=f"hkey_{i}", placeholder="Authorization")
            with h2:
                header_value = st.text_input(f"Header Value", key=f"hval_{i}", placeholder="Bearer <token>")

            body = st.text_area(
                f"Request Body (JSON)",
                key=f"body_{i}",
                placeholder='{"username": "test", "password": "1234"}',
                height=100
            )

            apis.append({
                "name": api_name,
                "method": method,
                "url": api_url,
                "header_key": header_key,
                "header_value": header_value,
                "body": body
            })

        if i < int(num_apis) - 1:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

with right_col:
    st.markdown("### 📄 Generated Script")

    generate_btn = st.button("⚡ Generate Script", use_container_width=True)

    if generate_btn:
        if not screen_name.strip():
            st.error("Screen name cannot be empty.")
        elif any(not a["name"].strip() for a in apis):
            st.error("All API names must be filled in.")
        else:
            script = generate_vugen_script(
                bp_number=int(bp_number),
                screen_number=int(screen_number),
                screen_name=screen_name.strip(),
                apis=apis
            )
            st.session_state["generated_script"] = script

    if "generated_script" in st.session_state:
        script = st.session_state["generated_script"]
        st.markdown('<div class="preview-label">Output · C Script</div>', unsafe_allow_html=True)
        st.code(script, language="c")
        st.download_button(
            label="⬇ Download .c file",
            data=script,
            file_name=f"BP{str(int(bp_number)).zfill(2)}_{str(int(screen_number)).zfill(2)}_{screen_name}.c",
            mime="text/plain",
            use_container_width=True
        )
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
            Fill in the form on the left<br>then hit <span style="color:#00e5a0">⚡ Generate Script</span>
        </div>
        """, unsafe_allow_html=True)
