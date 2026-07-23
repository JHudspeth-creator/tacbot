import os
import streamlit as st
from pyunifi.controller import Controller
import meraki
from groq import Groq

# =====================================================================
# 🔑 ENTERPRISE AI ENGINE KEY DEFINITION
# =====================================================================
# Securely reads the key from system memory instead of raw text
groq_api_key = os.environ.get("GROQ_API_KEY")

# Safety fallback: If it's missing, tell the user how to provide it
if not groq_api_key:
    st.error("Missing Groq API Key! Please configure your environment variables.")

# --- UNIVERSAL MULTI-PLATFORM CO-PILOT IDENTITIES ---
BOT_LOGO_AVATAR = "🤖"
USER_LOGO_AVATAR = "🧑‍💻"

# --- CORE PAGE CONFIGURATION ---
st.set_page_config(page_title="MyTacBot | NetOps Co-Pilot HUD", page_icon="⚡", layout="wide")

# --- HIGH-UTILITY ENGINEER TERMINAL CSS THEME ---
st.markdown("""
    <style>
    /* Global Background Adjustments */
    .stApp { background-color: #0b0f19; color: #cbd5e1; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    
    /* Engineer HUD Operational Telemetry Cards */
    .hud-card { 
        background-color: #111827; 
        border-radius: 8px; 
        padding: 18px; 
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 12px;
    }
    .hud-card.critical { border-left-color: #ef4444; background-color: #1c1416; }
    .hud-card.warning { border-left-color: #f59e0b; background-color: #1a1711; }
    
    .hud-val { font-size: 2.2rem; font-weight: 700; color: #ffffff; line-height: 1.1; margin-bottom: 2px; font-family: monospace; }
    .hud-lbl { font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    
    /* Playbook Command Buttons */
    div.stButton > button {
        background-color: #1f2937 !important;
        color: #e5e7eb !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 12px rgba(59,130,246,0.4);
    }
    
    /* Formatting AI Output and General Text */
    h1, h2, h3 { color: #f3f4f6 !important; font-weight: 700 !important; }
    code { background-color: #1f2937 !important; color: #f43f5e !important; padding: 2px 6px !important; border-radius: 4px !important; }

    /* Custom Rounded Background Container for Emojis */
    div[data-testid="stChatMessageAvatar"] {
        background-color: #161b22 !important; 
        border-radius: 6px !important;
        border: 1px solid #30363d !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# Memory State Orchestration Layer
if "current_vendor" not in st.session_state: st.session_state["current_vendor"] = "Home"
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "cached_telemetry" not in st.session_state: st.session_state["cached_telemetry"] = None
if "active_prompt" not in st.session_state: st.session_state["active_prompt"] = None

# --- SIDEBAR PERSISTENT CONSOLE ROUTER ---
if st.session_state["current_vendor"] != "Home":
    st.sidebar.markdown("### 🖥️ **TacBot Controls**")
    if st.sidebar.button("🔌 Disconnect & Exit Fabric", use_container_width=True):
        st.session_state["current_vendor"] = "Home"
        st.session_state["chat_history"] = []  
        st.session_state["cached_telemetry"] = None  
        st.session_state["active_prompt"] = None
        st.rerun()
    st.sidebar.divider()

def navigate_to(page_name):
    st.session_state["current_vendor"] = page_name
    st.session_state["chat_history"] = []  
    st.session_state["cached_telemetry"] = None  
    st.session_state["active_prompt"] = None
    st.rerun()

# --- THE CO-PILOT ENGINEER BRAIN ---
def run_chat_turn(user_query, network_data, vendor_name):
    try:
        if not MY_GROQ_KEY or MY_GROQ_KEY == "PASTE_YOUR_GSK_KEY_HERE":
            return "⚠️ **System Notification:** Counterpart Core offline. Groq API Key missing on Line 11."
        
        ai_client = Groq(api_key=MY_GROQ_KEY)
        
        system_prompt = (
            f"You are MyTacBot, an elite Tier-3 Senior Principal Network Automation Engineer acting as a troubleshooting co-pilot. "
            f"You are looking at live {vendor_name} diagnostic metrics alongside your engineering teammate. "
            "Never talk down to the user, and bypass generic explanations. Speak in authoritative, crisp, real-world infrastructure language. "
            "Analyze metrics through a lens of potential hardware faults, routing anomalies, or configuration discrepancies. "
            "Use clear bullet points for equipment specs and structure responses into two concise sections: "
            "1. TACTICAL REALITY CRITIQUE (What is genuinely broken right now) and 2. RECOMMENDED ENGINEERING REMEDIES."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        for i, msg in enumerate(st.session_state["chat_history"]):
            if i == 0 and msg["role"] == "user":
                messages.append({"role": "user", "content": f"Live Topography Telemetry Payload:\n{str(network_data)}\n\nTeammate Request: {msg['content']}"})
            else:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
        if len(st.session_state["chat_history"]) == 0:
            messages.append({"role": "user", "content": f"Live Topography Telemetry Payload:\n{str(network_data)}\n\nTeammate Request: {user_query}"})
        else:
            messages.append({"role": "user", "content": user_query})
            
        response = ai_client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
        # ✅ FIXED: Added correct list bracket indexing to support the Groq completions schema natively
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ **Co-Pilot Exception:** System trace-loop analytical execution crash: {str(e)}"
# --- MAIN COMMAND PLANE OVERVIEW PAGE ---
if st.session_state["current_vendor"] == "Home":
    st.markdown("<h1 style='margin-bottom: 0px; font-size:2.6rem;'>⚡ MyTacBot Workspace</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af; font-size: 1.05rem; margin-top: 4px; font-family: monospace;'>Active NetOps Counterpart & Generative Incident Response Hub</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### **Select Infrastructure Environment Node**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='hud-card'><h3 style='color: #10b981; margin:0;'>🟢 Ubiquiti UniFi Plane</h3><p style='font-size:0.85rem; color: #9ca3af; margin-top:8px;'>Audit localized access point arrays, radio frequencies, and client experience mapping indexes.</p></div>", unsafe_allow_html=True)
        if st.button("Launch UniFi Core Session 🛠️", use_container_width=True): navigate_to("UniFi")
    with col2:
        st.markdown("<div class='hud-card warning'><h3 style='color: #f59e0b; margin:0;'>☁️ Cisco Meraki Engine</h3><p style='font-size:0.85rem; color: #9ca3af; margin-top:8px;'>Synchronize distributed global organizations, trace loss/latency thresholds, and log link failures.</p></div>", unsafe_allow_html=True)
        if st.button("Launch Meraki Cloud Monitor 🛠️", use_container_width=True): navigate_to("Meraki")
    with col3:
        st.markdown("<div class='hud-card critical'><h3 style='color: #ef4444; margin:0;'>⛓️ Cisco Catalyst Node</h3><p style='font-size:0.85rem; color: #9ca3af; margin-top:8px;'>Initialize Rest API loops across IOS-XE edge blocks, distribution backbones, and webhooks.</p></div>", unsafe_allow_html=True)
        if st.button("Launch Catalyst Controller 🛠️", use_container_width=True): navigate_to("Catalyst")

# --- CONSOLE FABRIC INDIVIDUAL COMPONENT LOGIC ---
elif st.session_state["current_vendor"] == "UniFi":
    st.title("🟢 Environment Node: Ubiquiti UniFi Control Plane")
    with st.sidebar.form(key="unifi_form_v7"):
        st.header("🔌 Local Fabric Gateway")
        unifi_ip = st.text_input("Controller IP / Hostname", value="192.168.1.1")
        unifi_user = st.text_input("Username", value="admin")
        unifi_pass = st.text_input("Password", type="password")
        unifi_port = st.text_input("Port", value="8443")
        unifi_site = st.text_input("Site ID", value="default")
        connect_unifi = st.form_submit_button("🔌 Bind Fabric Handshake", use_container_width=True)

    if connect_unifi and unifi_user and unifi_pass:
        st.session_state["cached_telemetry"] = None
        with st.status("🔍 Compiling UniFi Local Topography Matrix...", expanded=True) as status_box:
            try:
                c = Controller(unifi_ip, unifi_user, unifi_pass, port=int(unifi_port), version='UDMP-unifiOS', ssl_verify=False)
                device_data = c.get_aps()
                if device_data:
                    st.session_state["cached_telemetry"] = [{"name": d.get("name"), "model": d.get("model"), "ip": d.get("ip"), "state": d.get("state"), "satisfaction": d.get("satisfaction")} for d in device_data]
                status_box.update(label="✅ Synchronization Complete", state="complete", expanded=False)
            except Exception as e:
                status_box.update(label="❌ Handshake Timeout", state="error")
                st.sidebar.error(f"Error Context: {str(e)}")
elif st.session_state["current_vendor"] == "Meraki":
    st.markdown("<h2 style='margin-bottom:0px;'>☁️ Cloud Node: Cisco Meraki Management Plane</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:monospace; color:#9ca3af; font-size:0.9rem; margin-top:2px;'>Isolated Session Buffer Terminal</p>", unsafe_allow_html=True)
    st.divider()
    
    with st.sidebar.form(key="meraki_form_v7"):
        st.header("🔑 Access Credentials")
        meraki_key = st.text_input("Meraki API Token", type="password")
        org_id = st.text_input("Target Organization ID")
        target_site = st.text_input("Geographic Focus Scope Filter (Optional)", value="")
        demo_mode = st.checkbox("🛠️ Mount Local Playbook Simulator Sandbox", value=True)
        connect_meraki = st.form_submit_button("🔌 Establish Telemetry Stream", use_container_width=True)
    
    if connect_meraki:
        st.session_state["cached_telemetry"] = None
        if demo_mode:
            with st.status("🛠️ Spin up Demo Mode Sandbox Environment...", expanded=True) as status_box:
                mock_leaderboard = [
                    {"network_name": "CA - Peninsula Yacht Marina - 217", "offline_device_count": 217, "known_uplink_circuit_failures": ["WAN1 (100% Loss)"], "sample_down_devices": ["Inside Front Door", "Main Office Side", "198 Gate", "185 Gate", "G7 Gate"]},
                    {"network_name": "FL - Seaside Resort - 104", "offline_device_count": 104, "known_uplink_circuit_failures": ["WAN2 (100% Loss)"], "sample_down_devices": ["Pool Deck AP", "Cabana East AP", "Main Lobby Switch"]},
                    {"network_name": "NY - Manhattan Office - 57", "offline_device_count": 57, "known_uplink_circuit_failures": ["Clear"], "sample_down_devices": ["Floor 4 Switch", "Conf Room AP"]}
                ]
                st.session_state["cached_telemetry"] = {
                    "mode": "org_summary", "total_organization_devices": 5690, "total_currently_offline": 766, "top_networks_with_most_down_devices": mock_leaderboard
                }
                status_box.update(label="✅ Playbook Simulator Loaded", state="complete", expanded=False)
        elif meraki_key and org_id:
            with st.status("🔐 Pulling Cloud Metrics...", expanded=True) as status_box:
                try:
                    dashboard = meraki.DashboardAPI(api_key=meraki_key, suppress_logging=True)
                    networks_list = dashboard.organizations.getOrganizationNetworks(org_id, total_pages='all')
                    network_name_map = {net["id"]: net["name"] for net in networks_list}
                    raw_device_data = dashboard.organizations.getOrganizationDevicesStatuses(org_id, total_pages='all')
                    try: uplink_data = dashboard.organizations.getOrganizationDevicesUplinksLossAndLatency(org_id, total_pages='all')
                    except Exception: uplink_data = [] 
                    uplink_map = {item.get("serial"): item.get("uplinks", []) for item in uplink_data if item.get("serial")}
                    
                    if raw_device_data:
                        network_counts, network_samples, total_offline, network_uplink_issues = {}, {}, 0, {}
                        for device in raw_device_data:
                            if device.get("status") != "online":
                                total_offline += 1
                                net_friendly_name = network_name_map.get(device.get("networkId"), f"Unknown Network")
                                dev_name = device.get("name") or device.get("model") or "Unnamed"
                                network_counts[net_friendly_name] = network_counts.get(net_friendly_name, 0) + 1
                                dev_uplinks = uplink_map.get(device.get("serial"), [])
                                broken_links = [f"{ul.get('interface')} (100% Loss)" for ul in dev_uplinks if ul.get("lossPercent") == 100.0]
                                if broken_links:
                                    if net_friendly_name not in network_uplink_issues: network_uplink_issues[net_friendly_name] = []
                                    network_uplink_issues[net_friendly_name].extend(broken_links)
                                if net_friendly_name not in network_samples: network_samples[net_friendly_name] = []
                                if len(network_samples[net_friendly_name]) < 5: network_samples[net_friendly_name].append(dev_name)
                        sorted_bad = sorted(network_counts.items(), key=lambda x: x, reverse=True)
                        leaderboard = [{"network_name": n, "offline_device_count": c, "known_uplink_circuit_failures": list(set(network_uplink_issues.get(n, ["Clear"]))), "sample_down_devices": network_samples.get(n, [])} for n, c in sorted_bad[:5]]
                        st.session_state["cached_telemetry"] = {"mode": "org_summary", "total_organization_devices": len(raw_device_data), "total_currently_offline": total_offline, "top_networks_with_most_down_devices": leaderboard}
                    status_box.update(label="✅ Global Topography Loaded", state="complete", expanded=False)
                except Exception as e:
                    status_box.update(label="❌ Pipeline Sync Exception", state="error")
                    st.sidebar.error(f"Context: {str(e)}")

elif st.session_state["current_vendor"] == "Catalyst":
    st.title("⛓️ Workspace Node: Cisco Catalyst Center Configuration Engine")
    st.info("⚙️ REST API Endpoints and webhooks ready to expand onto local IOS-XE edge switch nodes.")

# --- DYNAMIC NETOPS COUNTERPART MONITOR HUD INTERFACE ---
if st.session_state["current_vendor"] in ["UniFi", "Meraki"] and st.session_state["cached_telemetry"] is not None:
    
    col_hud1, col_hud2, col_hud3 = st.columns(3)
    if st.session_state["current_vendor"] == "Meraki" and st.session_state["cached_telemetry"]["mode"] == "org_summary":
        with col_hud1:
            st.markdown(f"<div class='hud-card'><div class='hud-lbl'>📡 Global Monitored Fleet Size</div><div class='hud-val'>{st.session_state['cached_telemetry']['total_organization_devices']:,}</div></div>", unsafe_allow_html=True)
        with col_hud2:
            st.markdown(f"<div class='hud-card critical'><div class='hud-lbl'>🚨 Critical Device Outages</div><div class='hud-val' style='color:#ef4444;'>{st.session_state['cached_telemetry']['total_currently_offline']}</div></div>", unsafe_allow_html=True)
        with col_hud3:
            st.markdown(f"<div class='hud-card warning'><div class='hud-lbl'>⚠️ Outage Ratio Index</div><div class='hud-val' style='color:#f59e0b;'>{round((st.session_state['cached_telemetry']['total_currently_offline']/st.session_state['cached_telemetry']['total_organization_devices'])*100, 1)}%</div></div>", unsafe_allow_html=True)
        
        with st.expander("📝 Live Infrastructure Topography Array Logs", expanded=False):
            st.dataframe(st.session_state["cached_telemetry"]["top_networks_with_most_down_devices"], use_container_width=True)
    else:
        st.markdown("<div class='hud-card'><div class='hud-lbl'>⚡ Active Node Interface Plane</div><div class='hud-val'>READY</div></div>", unsafe_allow_html=True)

    st.divider()
    
    st.markdown("🛠️ **Co-Pilot Active Response Playbooks:**")
    cp_col1, cp_col2, cp_col3 = st.columns(3)
    if cp_col1.button("🔥 Run High-Impact Triage Protocol", use_container_width=True): 
        st.session_state["active_prompt"] = "Identify the highest priority operational failures right now. Run a deep-dive triage assessment on the top sites experiencing hardware drops, analyze link failures, and tell me where to dispatch on-site help first."
    if cp_col2.button("📡 Audit Circuit Performance Logs", use_container_width=True): 
        st.session_state["active_prompt"] = "Scan the telemetry payload specifically for complete 100% loss packet anomalies or carrier uplink drops. Give me the breakdown of affected interfaces."
    if cp_col3.button("📋 Build Outage Handover Report", use_container_width=True): 
        st.session_state["active_prompt"] = "Generate a comprehensive shift engineering summary. Group issues by localized site hierarchy, list sample down gear names, and detail actionable steps for the incoming shift team."

    # Display rolling conversational history using clean, safe multi-platform emoji assets [6]
    for chat in st.session_state["chat_history"]:
        avatar_asset = BOT_LOGO_AVATAR if chat["role"] == "assistant" else USER_LOGO_AVATAR
        with st.chat_message(chat["role"], avatar=avatar_asset): 
            st.write(chat["content"])

    # Core Command Input Collection Field with Context-Aware Unique Keys
    prompt_input = st.chat_input(
        "Dispatch command query to TacBot Co-Pilot...", 
        key=f"tacbot_input_field_{st.session_state['current_vendor'].lower()}"
    )
    eval_prompt = st.session_state["active_prompt"] if st.session_state["active_prompt"] else prompt_input

    if eval_prompt:
        st.session_state["active_prompt"] = None 
        st.session_state["chat_history"].append({"role": "user", "content": eval_prompt})
        
        with st.chat_message("user", avatar=USER_LOGO_AVATAR): 
            st.write(eval_prompt)
            
        with st.chat_message("assistant", avatar=BOT_LOGO_AVATAR):
            with st.spinner("🧠 TacBot calculating root-cause analysis..."):
                answer = run_chat_turn(eval_prompt, st.session_state["cached_telemetry"], st.session_state["current_vendor"])
                st.write(answer)
                
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        st.rerun()
