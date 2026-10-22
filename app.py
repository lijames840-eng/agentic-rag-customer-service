import time
from urllib.parse import quote

import streamlit as st

st.set_page_config(
    page_title="智扫通 · 机器人智能客服",
    page_icon=":material/smart_toy:",
    layout="wide",
    initial_sidebar_state="expanded",
)

STYLE = """
<style>
:root {
  --zst-bg: #F5F7FB;
  --zst-surface: #FFFFFF;
  --zst-ink: #0B1220;
  --zst-muted: #64748B;
  --zst-line: #E5EAF3;
  --zst-accent: #4F46E5;
  --zst-accent-2: #0EA5E9;
}

html, body, [data-testid="stApp"], [data-testid="stMain"],
[data-testid="stSidebar"], textarea, input, button {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Microsoft YaHei", "Noto Sans SC", sans-serif !important;
}

[data-testid="stAppViewContainer"] {
  background-color: var(--zst-bg) !important;
  background-image:
    radial-gradient(1000px 520px at 88% -12%, rgba(79, 70, 229, 0.10), transparent 62%),
    radial-gradient(900px 440px at -8% 6%, rgba(14, 165, 233, 0.08), transparent 58%),
    linear-gradient(180deg, #F7F9FC 0%, #F4F6FB 100%) !important;
}
[data-testid="stMain"],
[data-testid="stAppScrollToBottomContainer"] {
  background: transparent !important;
  align-items: flex-start !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
[data-testid="stMainMenu"],
[data-testid="stStatusWidget"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { background: transparent !important; }

[data-testid="stMainBlockContainer"] {
  max-width: 1000px !important;
  padding-top: 1.6rem !important;
  padding-bottom: 7rem !important;
}
[data-testid="stMainBlockContainer"]:has(.zst-landing) {
  padding-bottom: 1.5rem !important;
}
[data-testid="stElementContainer"]:has(iframe[title="st.iframe"]) {
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0A1020 0%, #0D1628 55%, #0A1020 100%) !important;
  border-right: 1px solid rgba(148, 163, 184, 0.12) !important;
  box-shadow: 20px 0 60px -40px rgba(2, 6, 23, 0.6);
  color: #CBD5E1;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  background: transparent !important;
  padding: 0.4rem 0.85rem 1rem !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
  padding: 0.45rem 0.55rem 0.1rem !important;
}
[data-testid="stSidebarCollapseButton"] button {
  color: #94A3B8 !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
  color: #E2E8F0 !important;
  background: rgba(148, 163, 184, 0.1) !important;
}
[data-testid="stSidebarResizeHandle"] {
  background: rgba(148, 163, 184, 0.14) !important;
}

.zst-sb-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 6px 18px;
}
.zst-sb-logo {
  width: 42px;
  height: 42px;
  flex: none;
  border-radius: 13px;
  display: grid;
  place-items: center;
  color: #FFFFFF;
  background: linear-gradient(135deg, #4F46E5 0%, #2563EB 55%, #0EA5E9 100%);
  box-shadow: 0 14px 30px -14px rgba(79, 70, 229, 0.8),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.zst-sb-logo svg { width: 22px; height: 22px; }
.zst-sb-name {
  color: #F8FAFC;
  font-size: 1.06rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.2;
}
.zst-sb-tag {
  color: #7C8BA5;
  font-size: 0.6rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-top: 3px;
}

.zst-sb-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 18px 6px 8px;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #7C8BA5;
}
.zst-sb-label em {
  font-style: normal;
  color: #46566E;
  letter-spacing: 0.1em;
}

.zst-caps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0 2px 6px;
}
.zst-cap {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 11px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(255, 255, 255, 0.025);
}
.zst-cap-icon {
  width: 30px;
  height: 30px;
  flex: none;
  border-radius: 9px;
  display: grid;
  place-items: center;
}
.zst-cap-icon img { width: 16px; height: 16px; }
.zst-cap-title {
  color: #E2E8F0;
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.35;
}
.zst-cap-desc {
  color: #7C8BA5;
  font-size: 0.7rem;
  line-height: 1.55;
  margin-top: 2px;
}
.tone-sb-indigo { background: rgba(99, 102, 241, 0.16); color: #A5B4FC; }
.tone-sb-cyan { background: rgba(14, 165, 233, 0.14); color: #7DD3FC; }
.tone-sb-emerald { background: rgba(16, 185, 129, 0.14); color: #6EE7B7; }

[class*="st-key-zst_sbq_"] button {
  width: 100% !important;
  min-height: 38px !important;
  justify-content: flex-start !important;
  gap: 8px !important;
  padding: 7px 10px !important;
  background: rgba(255, 255, 255, 0.028) !important;
  border: 1px solid rgba(148, 163, 184, 0.13) !important;
  border-radius: 10px !important;
  color: #C7D2E0 !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  line-height: 1.35 !important;
  text-align: left !important;
  box-shadow: none !important;
  transition: background 0.18s ease, border-color 0.18s ease,
    color 0.18s ease, transform 0.18s ease;
}
[class*="st-key-zst_sbq_"] button:hover {
  background: rgba(99, 102, 241, 0.16) !important;
  border-color: rgba(129, 140, 248, 0.42) !important;
  color: #F8FAFC !important;
  transform: translateX(2px);
}
[class*="st-key-zst_sbq_"] button:active { transform: translateX(1px); }
[class*="st-key-zst_sbq_"] button * { color: inherit !important; }
[class*="st-key-zst_sbq_"] button p {
  white-space: normal !important;
  text-align: left !important;
  margin: 0 !important;
}
[class*="st-key-zst_sbq_"] button svg { color: #818CF8 !important; }

[class*="st-key-zst_clear"] button {
  width: 100% !important;
  justify-content: center !important;
  gap: 6px !important;
  padding: 7px 10px !important;
  background: transparent !important;
  border: 1px solid rgba(148, 163, 184, 0.12) !important;
  border-radius: 10px !important;
  color: #7C8BA5 !important;
  font-size: 0.74rem !important;
  font-weight: 500 !important;
  box-shadow: none !important;
  transition: color 0.18s ease, background 0.18s ease, border-color 0.18s ease;
}
[class*="st-key-zst_clear"] button:hover {
  color: #FCA5A5 !important;
  border-color: rgba(248, 113, 113, 0.32) !important;
  background: rgba(248, 113, 113, 0.07) !important;
}
[class*="st-key-zst_clear"] button:disabled { opacity: 0.4 !important; }
[class*="st-key-zst_clear"] button * { color: inherit !important; }

.zst-engine {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 18px 2px 10px;
  padding: 12px;
  border-radius: 13px;
  border: 1px solid rgba(148, 163, 184, 0.13);
  background: rgba(255, 255, 255, 0.03);
}
.zst-engine-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 4px;
  flex: none;
}
.state-ready .zst-engine-dot {
  background: #34D399;
  box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.12);
  animation: zst-pulse 2.4s ease-in-out infinite;
}
.state-busy .zst-engine-dot {
  background: #FBBF24;
  box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.12);
  animation: zst-pulse 1s ease-in-out infinite;
}
.state-error .zst-engine-dot {
  background: #F87171;
  box-shadow: 0 0 0 4px rgba(248, 113, 113, 0.12);
}
.zst-engine-title {
  color: #E2E8F0;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.3;
}
.zst-engine-sub {
  color: #7C8BA5;
  font-size: 0.68rem;
  line-height: 1.5;
  margin-top: 2px;
}

.zst-sb-foot {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin: 14px 6px 2px;
  padding-top: 12px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  color: #475569;
  font-size: 0.6rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* ---------- Top bar ---------- */
.zst-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 4px 2px 14px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  margin-bottom: 20px;
}
.zst-topbar-brand {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
}
.zst-logo {
  width: 36px;
  height: 36px;
  flex: none;
  border-radius: 11px;
  display: grid;
  place-items: center;
  color: #FFFFFF;
  background: linear-gradient(135deg, #4F46E5 0%, #2563EB 55%, #0EA5E9 100%);
  box-shadow: 0 10px 24px -12px rgba(79, 70, 229, 0.75),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.zst-logo svg { width: 19px; height: 19px; }
.zst-topbar-name {
  color: var(--zst-ink);
  font-size: 0.96rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.25;
}
.zst-topbar-sub {
  color: #94A3B8;
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-top: 2px;
}
.zst-topbar-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 7px;
  flex-wrap: wrap;
}
.zst-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid #E5EAF3;
  color: #475569;
  font-size: 0.7rem;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}
.zst-pill-muted { color: #64748B; background: rgba(255, 255, 255, 0.5); }
.zst-live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.14);
}

/* ---------- Hero ---------- */
.zst-hero {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 36px 42px;
  background: linear-gradient(135deg, #FFFFFF 0%, #FBFCFE 55%, #F3F6FF 100%);
  border: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 30px 80px -40px rgba(15, 23, 42, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  margin-bottom: 22px;
}
.zst-hero::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 3px;
  background: linear-gradient(90deg, #4F46E5, #0EA5E9, #22D3EE);
}
.zst-hero::after {
  content: "";
  position: absolute;
  width: 380px;
  height: 380px;
  right: -80px;
  top: -160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(79, 70, 229, 0.13), transparent 68%);
}
.zst-hero > * { position: relative; z-index: 1; }
.zst-eyebrow {
  color: #6366F1;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}
.zst-hero h1 {
  color: var(--zst-ink);
  font-size: clamp(1.85rem, 3.1vw, 2.7rem);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.12;
  margin: 12px 0 12px;
}
.zst-hero h1 .zst-grad {
  background: linear-gradient(100deg, #4F46E5 10%, #2563EB 52%, #0891B2 92%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.zst-hero p {
  max-width: 530px;
  margin: 0;
  color: #5B6B82;
  font-size: 0.92rem;
  line-height: 1.72;
  text-wrap: balance;
}
.zst-nowrap { white-space: nowrap; }
.zst-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}
.zst-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 11px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid #E3E9F4;
  color: #475569;
  font-size: 0.71rem;
  font-weight: 500;
}
.zst-chip-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4F46E5, #0EA5E9);
}
.zst-orbit {
  position: absolute;
  right: 34px;
  top: 50%;
  width: 250px;
  height: 250px;
  transform: translateY(-50%);
  pointer-events: none;
  z-index: 0;
}
.zst-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid rgba(79, 70, 229, 0.14);
}
.zst-ring-a { animation: zst-spin 26s linear infinite; }
.zst-ring-a::after {
  content: "";
  position: absolute;
  top: -4px;
  left: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4F46E5;
  box-shadow: 0 0 14px rgba(79, 70, 229, 0.7);
}
.zst-ring-b {
  inset: 38px;
  border-color: rgba(14, 165, 233, 0.18);
  animation: zst-spin 18s linear infinite reverse;
}
.zst-ring-b::after {
  content: "";
  position: absolute;
  bottom: -3px;
  left: 30%;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #06B6D4;
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.7);
}
.zst-core {
  position: absolute;
  inset: 88px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: #FFFFFF;
  background: linear-gradient(135deg, #4F46E5, #0EA5E9);
  box-shadow: 0 24px 50px -20px rgba(79, 70, 229, 0.65);
}
.zst-core svg { width: 30px; height: 30px; }

/* ---------- Welcome / features ---------- */
.zst-welcome { margin: 2px 0 14px; }
.zst-welcome h2 {
  color: var(--zst-ink);
  font-size: 1.24rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
}
.zst-welcome p {
  color: var(--zst-muted);
  font-size: 0.84rem;
  line-height: 1.65;
  margin: 0;
  text-wrap: balance;
}
.zst-feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
  margin-top: 4px;
}
.zst-feature {
  background: #FFFFFF;
  border: 1px solid #E8EDF5;
  border-radius: 16px;
  padding: 17px 18px;
  box-shadow: 0 14px 40px -28px rgba(15, 23, 42, 0.28);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.zst-feature:hover {
  transform: translateY(-3px);
  border-color: #C7D2FE;
  box-shadow: 0 24px 50px -28px rgba(79, 70, 229, 0.35);
}
.zst-feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  margin-bottom: 10px;
}
.zst-feature-icon img { width: 20px; height: 20px; }
.tone-indigo { background: #EEF2FF; color: #4F46E5; }
.tone-cyan { background: #E0F2FE; color: #0284C7; }
.tone-emerald { background: #ECFDF5; color: #059669; }
.zst-feature h3 {
  color: var(--zst-ink);
  font-size: 0.92rem;
  font-weight: 650;
  margin: 0 0 5px;
}
.zst-feature p {
  color: #64748B;
  font-size: 0.8rem;
  line-height: 1.62;
  margin: 0;
}
.zst-feature .zst-feature-meta {
  margin-top: 10px;
  color: #94A3B8;
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.zst-sugg-label {
  margin: 20px 0 8px;
  color: #94A3B8;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
[class*="st-key-zst_suggest_"] button {
  width: 100% !important;
  min-height: 44px !important;
  justify-content: flex-start !important;
  gap: 7px !important;
  padding: 8px 11px !important;
  background: rgba(255, 255, 255, 0.86) !important;
  border: 1px solid #E4EAF3 !important;
  border-radius: 12px !important;
  color: #334155 !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  text-align: left !important;
  box-shadow: 0 8px 24px -22px rgba(15, 23, 42, 0.4) !important;
  transition: transform 0.18s ease, border-color 0.18s ease,
    box-shadow 0.18s ease, background 0.18s ease, color 0.18s ease;
}
[class*="st-key-zst_suggest_"] button:hover {
  transform: translateY(-2px);
  border-color: #C7D2FE !important;
  background: #FFFFFF !important;
  color: #312E81 !important;
  box-shadow: 0 18px 40px -26px rgba(79, 70, 229, 0.45) !important;
}
[class*="st-key-zst_suggest_"] button * { color: inherit !important; }
[class*="st-key-zst_suggest_"] button p {
  white-space: normal !important;
  text-align: left !important;
  margin: 0 !important;
}
[class*="st-key-zst_suggest_"] button svg { color: #4F46E5 !important; }

/* ---------- Conversation ---------- */
.zst-rule {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 2px 0 20px;
  color: #94A3B8;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.zst-rule::after {
  content: "";
  height: 1px;
  flex: 1;
  background: linear-gradient(90deg, #E2E8F0, transparent);
}

[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0 !important;
  gap: 0.8rem !important;
  margin-bottom: 1.4rem !important;
  display: flex !important;
  align-items: flex-start !important;
  animation: zst-rise 0.4s ease both;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  flex-direction: row-reverse !important;
}
[data-testid^="stChatMessageAvatar"] {
  width: 36px !important;
  height: 36px !important;
  min-width: 36px !important;
  border-radius: 11px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  align-self: flex-start !important;
  margin-top: 2px;
  overflow: hidden;
  box-shadow: 0 6px 16px -10px rgba(15, 23, 42, 0.35);
}
[data-testid="stChatMessageAvatarAssistant"] {
  background: linear-gradient(135deg, #4F46E5, #2563EB) !important;
  color: #FFFFFF !important;
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
}
[data-testid="stChatMessageAvatarUser"] {
  background: #FFFFFF !important;
  color: #475569 !important;
  border: 1px solid #E2E8F0 !important;
}
[data-testid^="stChatMessageAvatar"] img,
[data-testid^="stChatMessageAvatar"] svg {
  width: 20px !important;
  height: 20px !important;
}
[data-testid="stChatMessageContent"] {
  max-width: 86% !important;
  padding: 14px 18px !important;
  border-radius: 4px 18px 18px 18px !important;
  border: 1px solid #E7ECF5 !important;
  background: linear-gradient(180deg, #FFFFFF 0%, #FDFDFF 100%) !important;
  color: #1E293B !important;
  box-shadow: 0 18px 40px -30px rgba(15, 23, 42, 0.4);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"])
  [data-testid="stChatMessageContent"] { margin-right: auto; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
  flex: 0 1 auto !important;
  width: fit-content !important;
  max-width: 74% !important;
  margin-left: auto;
  border-radius: 18px 4px 18px 18px !important;
  border-color: rgba(255, 255, 255, 0.08) !important;
  background: linear-gradient(135deg, #111827 0%, #1E293B 100%) !important;
  color: #F1F5F9 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] li,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] h3,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] strong,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] em,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] span,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] td,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] th {
  color: #F1F5F9 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] a { color: #A5B4FC !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] code {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.12) !important;
  color: #E2E8F0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] pre {
  background: rgba(2, 6, 23, 0.45) !important;
}

[data-testid="stChatMessageContent"] p {
  margin: 0 0 0.65rem !important;
  font-size: 0.92rem;
  line-height: 1.78;
}
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }
[data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessageContent"] ol {
  margin: 0.2rem 0 0.8rem !important;
  padding-left: 1.2rem !important;
}
[data-testid="stChatMessageContent"] li {
  margin: 0.28rem 0 !important;
  font-size: 0.92rem;
  line-height: 1.7;
}
[data-testid="stChatMessageContent"] h1 {
  font-size: 1.35rem !important;
  letter-spacing: -0.02em;
  margin: 0.9rem 0 0.5rem !important;
  color: #0B1220;
}
[data-testid="stChatMessageContent"] h2 {
  font-size: 1.18rem !important;
  letter-spacing: -0.015em;
  margin: 0.9rem 0 0.45rem !important;
  color: #0B1220;
}
[data-testid="stChatMessageContent"] h3 {
  font-size: 1.02rem !important;
  margin: 0.8rem 0 0.4rem !important;
  color: #0B1220;
}
[data-testid="stChatMessageContent"] h1:first-child,
[data-testid="stChatMessageContent"] h2:first-child,
[data-testid="stChatMessageContent"] h3:first-child { margin-top: 0 !important; }
[data-testid="stChatMessageContent"] a {
  color: #4F46E5;
  text-decoration: none;
  border-bottom: 1px solid rgba(79, 70, 229, 0.2);
}
[data-testid="stChatMessageContent"] code {
  padding: 1px 5px;
  border-radius: 6px;
  border: 1px solid #E8EDF5;
  background: #F4F6FB;
  color: #4338CA;
  font-size: 0.84em;
}
[data-testid="stChatMessageContent"] pre {
  padding: 14px 16px !important;
  border-radius: 12px !important;
  background: #0F172A !important;
  overflow-x: auto;
}
[data-testid="stChatMessageContent"] pre code {
  padding: 0;
  border: none;
  background: transparent;
  color: #E2E8F0;
}
[data-testid="stChatMessageContent"] table {
  width: 100%;
  margin: 0.6rem 0;
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid #E8EDF5;
  border-radius: 10px;
  overflow: hidden;
}
[data-testid="stChatMessageContent"] th {
  padding: 8px 10px;
  background: #F8FAFC;
  color: #334155;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: left;
}
[data-testid="stChatMessageContent"] td {
  padding: 8px 10px;
  border-top: 1px solid #EDF1F7;
  font-size: 0.8rem;
}
[data-testid="stChatMessageContent"] blockquote {
  margin: 0.5rem 0;
  padding: 0.4rem 0.8rem;
  border-left: 3px solid #C7D2FE;
  border-radius: 0 8px 8px 0;
  background: #F8FAFF;
  color: #475569;
}
[data-testid="stChatMessageContent"] hr {
  border: none;
  border-top: 1px solid #E8EDF5;
  margin: 1rem 0;
}

.zst-msg-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 9px;
}
.zst-msg-name {
  color: #64748B;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}
.zst-msg-tag {
  padding: 2px 7px;
  border-radius: 999px;
  border: 1px solid #E0E7FF;
  background: #EEF2FF;
  color: #4F46E5;
  font-size: 0.56rem;
  font-weight: 600;
  letter-spacing: 0.06em;
}
.zst-msg-meta-user { justify-content: flex-end; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .zst-msg-name {
  color: rgba(241, 245, 249, 0.72) !important;
}

/* ---------- Chat input ---------- */
[data-testid="stBottom"] {
  background: linear-gradient(180deg, rgba(245, 247, 251, 0) 0%,
    rgba(245, 247, 251, 0.92) 42%, #F5F7FB 100%) !important;
  border-top: none !important;
}
[data-testid="stBottom"] > div { background: transparent !important; }
[data-testid="stBottomBlockContainer"] {
  max-width: 1000px !important;
  padding-top: 0.6rem !important;
  padding-bottom: 1.1rem !important;
}
[data-testid="stChatInput"] {
  min-height: 54px;
  border-radius: 16px !important;
  border: 1px solid #DEE5F0 !important;
  background: #FFFFFF !important;
  box-shadow: 0 20px 50px -30px rgba(15, 23, 42, 0.45),
    0 2px 6px rgba(15, 23, 42, 0.03) !important;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}
[data-testid="stChatInput"]:focus-within {
  border-color: #A5B4FC !important;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1),
    0 20px 50px -30px rgba(15, 23, 42, 0.45) !important;
}
[data-testid="stChatInputTextArea"] {
  padding: 0.55rem 0.3rem 0.55rem 0.55rem !important;
  background: transparent !important;
  color: #0F172A !important;
  font-size: 0.92rem !important;
  caret-color: #4F46E5;
}
[data-testid="stChatInputTextArea"]::placeholder { color: #94A3B8 !important; }
[data-testid="stChatInputSubmitButton"] {
  margin: 0.35rem !important;
  border: none !important;
  border-radius: 11px !important;
  background: linear-gradient(135deg, #4F46E5, #2563EB) !important;
  color: #FFFFFF !important;
  box-shadow: 0 8px 20px -10px rgba(79, 70, 229, 0.7) !important;
}
[data-testid="stChatInputSubmitButton"]:hover { filter: brightness(1.06); }
[data-testid="stChatInputSubmitButton"] svg { color: #FFFFFF !important; }

/* ---------- Motion / responsive ---------- */
@keyframes zst-rise {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: none; }
}
@keyframes zst-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.55; transform: scale(0.85); }
}
@keyframes zst-spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .zst-orbit { display: none; }
  .zst-hero { padding: 32px 26px; }
  .zst-hero p { max-width: 100%; }
  .zst-pill-muted { display: none; }
  [data-testid="stMainBlockContainer"] {
    padding-top: 0.9rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
  }
  [data-testid="stChatMessageContent"] { max-width: 100% !important; }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
    [data-testid="stChatMessageContent"] { max-width: 88% !important; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
  }
}
</style>
"""

st.html(STYLE)

ICON_ROBOT = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect x="4" y="7" width="16" height="12" rx="4"></rect>'
    '<path d="M12 3v4"></path>'
    '<circle cx="9" cy="13" r="1.2" fill="currentColor" stroke="none"></circle>'
    '<circle cx="15" cy="13" r="1.2" fill="currentColor" stroke="none"></circle>'
    '<path d="M9 17h6"></path>'
    "</svg>"
)
ICON_DATABASE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<ellipse cx="12" cy="5" rx="7" ry="3"></ellipse>'
    '<path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5"></path>'
    '<path d="M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"></path>'
    "</svg>"
)
ICON_CLOUD = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M7 18h9a4 4 0 0 0 .8-7.9A5.5 5.5 0 0 0 6.3 9 3.5 3.5 0 0 0 7 18Z"></path>'
    '<path d="M8 21h8"></path>'
    "</svg>"
)
ICON_CHART = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect x="3" y="3" width="18" height="18" rx="3"></rect>'
    '<path d="M7 15l3-4 3 2 4-6"></path>'
    "</svg>"
)


def icon_img(svg, color, size):
    """st.html sanitizes inline <svg>, so ship icons as data-URI images."""
    raw = svg.replace("currentColor", color).replace(
        "<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1
    )
    return (
        f'<img src="data:image/svg+xml;utf8,{quote(raw, safe="")}" '
        f'width="{size}" height="{size}" alt="" '
        f'style="width:{size}px;height:{size}px;display:block" />'
    )

QUICK_PROMPTS = [
    ("小户型怎么选？", "小户型适合哪些扫地机器人？", "search"),
    ("天气适合使用吗？", "我所在的城市现在适合使用扫地机器人吗？", "cloud"),
    ("生成本月报告", "生成我本月的使用报告", "assessment"),
    ("边刷不转排查", "边刷不转了，应该如何排查？", "build"),
]

SUGGESTIONS = [
    ("小户型怎么选？", "小户型适合哪些扫地机器人？", "search"),
    ("天气适合使用吗？", "我所在的城市现在适合使用扫地机器人吗？", "cloud"),
    ("生成本月报告", "生成我本月的使用报告", "assessment"),
    ("边刷不转排查", "边刷不转了，应该如何排查？", "build"),
]

FEATURES = [
    (
        "tone-indigo",
        ICON_DATABASE,
        "专业知识问答",
        "选购、清洁、耗材与保养，基于专业资料给出可执行建议。",
        "RAG · 知识库检索",
    ),
    (
        "tone-cyan",
        ICON_CLOUD,
        "环境适配分析",
        "结合所在城市天气、湿度与空气质量，判断当前使用条件。",
        "WEATHER · 环境感知",
    ),
    (
        "tone-emerald",
        ICON_CHART,
        "个性化使用报告",
        "按月汇总清洁效率、耗材状态与使用趋势，生成专属报告。",
        "REPORT · 月度分析",
    ),
]

CAPABILITIES = [
    ("tone-sb-indigo", ICON_DATABASE, "专业知识问答", "选购 / 故障 / 保养"),
    ("tone-sb-cyan", ICON_CLOUD, "环境适配建议", "天气 / 湿度 / 空气质量"),
    ("tone-sb-emerald", ICON_CHART, "个性化使用报告", "月度效率 / 耗材状态"),
]

FEATURE_ICON_COLORS = {
    "tone-indigo": "#4F46E5",
    "tone-cyan": "#0284C7",
    "tone-emerald": "#059669",
}
CAP_ICON_COLORS = {
    "tone-sb-indigo": "#A5B4FC",
    "tone-sb-cyan": "#7DD3FC",
    "tone-sb-emerald": "#6EE7B7",
}

ASSISTANT_META = (
    '<div class="zst-msg-meta">'
    '<span class="zst-msg-name">智扫通 AI</span>'
    '<span class="zst-msg-tag">RAG · ReAct</span>'
    "</div>"
)
USER_META = (
    '<div class="zst-msg-meta zst-msg-meta-user">'
    '<span class="zst-msg-name">你</span>'
    "</div>"
)


def html_topbar(landing=False):
    landing_class = " zst-landing" if landing else ""
    return f"""
    <div class="zst-topbar{landing_class}">
      <div class="zst-topbar-brand">
        <div class="zst-logo">{icon_img(ICON_ROBOT, "#FFFFFF", 19)}</div>
        <div>
          <div class="zst-topbar-name">智扫通</div>
          <div class="zst-topbar-sub">RoboCare · AI Console</div>
        </div>
      </div>
      <div class="zst-topbar-right">
        <span class="zst-pill"><span class="zst-live-dot"></span>服务在线</span>
        <span class="zst-pill zst-pill-muted">Qwen-Plus</span>
        <span class="zst-pill zst-pill-muted">RAG · Chroma</span>
      </div>
    </div>
    """


def html_hero():
    return f"""
    <section class="zst-hero">
      <div class="zst-orbit" aria-hidden="true">
        <div class="zst-ring zst-ring-a"></div>
        <div class="zst-ring zst-ring-b"></div>
        <div class="zst-core">{icon_img(ICON_ROBOT, "#FFFFFF", 30)}</div>
      </div>
      <div class="zst-eyebrow">Intelligent Service Console</div>
      <h1>扫地机器人<br><span class="zst-grad">智能客服</span></h1>
      <p>融合 RAG 知识库与 ReAct 推理，覆盖选购建议、清洁维护、故障排查与<span class="zst-nowrap">个性化报告</span>。</p>
      <div class="zst-chips">
        <span class="zst-chip"><span class="zst-chip-dot"></span>RAG 专业知识库</span>
        <span class="zst-chip"><span class="zst-chip-dot"></span>ReAct 推理引擎</span>
        <span class="zst-chip"><span class="zst-chip-dot"></span>实时环境感知</span>
      </div>
    </section>
    """


def html_welcome():
    return """
    <div class="zst-welcome">
      <h2>今天需要什么帮助？</h2>
      <p>选择一个常见场景，或直接描述您的问题。系统会自动判断是否需要检索知识库或调用工具。</p>
    </div>
    """


def html_features():
    cards = "".join(
        f"""
        <div class="zst-feature">
          <div class="zst-feature-icon {tone}">{icon_img(icon, FEATURE_ICON_COLORS[tone], 20)}</div>
          <h3>{title}</h3>
          <p>{desc}</p>
          <div class="zst-feature-meta">{meta}</div>
        </div>
        """
        for tone, icon, title, desc, meta in FEATURES
    )
    return f'<div class="zst-feature-grid">{cards}</div>'


def html_sidebar_brand():
    return f"""
    <div class="zst-sb-brand">
      <div class="zst-sb-logo">{icon_img(ICON_ROBOT, "#FFFFFF", 22)}</div>
      <div>
        <div class="zst-sb-name">智扫通</div>
        <div class="zst-sb-tag">RoboCare AI Console</div>
      </div>
    </div>
    """


def html_sidebar_label(title, en):
    return f'<div class="zst-sb-label"><span>{title}</span><em>{en}</em></div>'


def html_capabilities():
    rows = "".join(
        f"""
        <div class="zst-cap">
          <div class="zst-cap-icon {tone}">{icon_img(icon, CAP_ICON_COLORS[tone], 16)}</div>
          <div>
            <div class="zst-cap-title">{title}</div>
            <div class="zst-cap-desc">{desc}</div>
          </div>
        </div>
        """
        for tone, icon, title, desc in CAPABILITIES
    )
    return f'<div class="zst-caps">{rows}</div>'


def html_engine_status(state):
    states = {
        "ready": ("state-ready", "引擎待命", "Qwen-Plus · RAG 知识库"),
        "busy": ("state-busy", "正在推理", "检索资料并生成专业答复"),
        "error": ("state-error", "连接异常", "请检查 API Key 与网络"),
    }
    css_class, title, desc = states[state]
    return f"""
    <div class="zst-engine {css_class}">
      <span class="zst-engine-dot"></span>
      <div>
        <div class="zst-engine-title">{title}</div>
        <div class="zst-engine-sub">{desc}</div>
      </div>
    </div>
    """


def html_rule(label):
    return f'<div class="zst-rule">{label}</div>'


def html_suggestions_label():
    return '<div class="zst-sugg-label">试试这样问</div>'


def html_sidebar_footer():
    return """
    <div class="zst-sb-foot">
      <span>AI 生成内容仅供参考</span>
      <span>v1.0</span>
    </div>
    """


LANDING_SCROLL_GUARD = """
<script>
(() => {
  try {
    const doc = window.parent.document;
    let ticks = 0;
    let canceled = false;
    const cancel = () => { canceled = true; };
    ["wheel", "touchstart", "keydown", "pointerdown"].forEach((type) =>
      window.parent.addEventListener(type, cancel, { once: true, passive: true })
    );
    const timer = window.parent.setInterval(() => {
      if (canceled || ++ticks > 75) {
        window.parent.clearInterval(timer);
        return;
      }
      const main = doc.querySelector('[data-testid="stAppScrollToBottomContainer"]');
      if (main && main.scrollTop > 0) main.scrollTop = 0;
    }, 40);
  } catch (err) {}
})();
</script>
"""


@st.cache_resource(show_spinner=False)
def get_agent():
    from agent.react_agent import ReactAgent

    return ReactAgent()


def typewriter(text, chunk_size=3, delay=0.0035):
    for start in range(0, len(text), chunk_size):
        yield text[start : start + chunk_size]
        time.sleep(delay)


def render_message(message):
    role = message.get("role", "assistant")
    with st.chat_message(role):
        if role == "assistant":
            st.markdown(ASSISTANT_META, unsafe_allow_html=True)
            trace = message.get("trace") or []
            if trace:
                elapsed = message.get("elapsed")
                label = (
                    f"推理完成 · {elapsed:.1f} 秒"
                    if isinstance(elapsed, (int, float))
                    else "推理完成"
                )
                with st.status(label, type="compact", state="complete", expanded=False):
                    for index, step in enumerate(trace, 1):
                        st.markdown(f"**步骤 {index}**")
                        st.markdown(step)
        else:
            st.markdown(USER_META, unsafe_allow_html=True)

        if message.get("error"):
            st.error("抱歉，本次请求未能完成。", icon=":material/error:")
            with st.expander("查看错误详情", icon=":material/bug_report:"):
                st.code(message["error"])
        else:
            st.markdown(message.get("content", ""))


def render_assistant_turn(prompt, engine_slot):
    started = time.perf_counter()
    with st.chat_message("assistant"):
        st.markdown(ASSISTANT_META, unsafe_allow_html=True)
        status = st.status(
            ":shimmer[正在分析需求并检索专业知识…]",
            type="compact",
            expanded=False,
        )
        engine_slot.markdown(html_engine_status("busy"), unsafe_allow_html=True)

        try:
            agent = get_agent()
            chunks = [
                chunk.strip()
                for chunk in agent.execute_stream(prompt)
                if chunk and chunk.strip()
            ]
            elapsed = time.perf_counter() - started
            if not chunks:
                raise RuntimeError("模型未返回有效内容")

            answer = chunks[-1]
            trace = chunks[:-1]
            if trace:
                with status:
                    for index, step in enumerate(trace, 1):
                        st.markdown(f"**步骤 {index}**")
                        st.markdown(step)

            status.update(label=f"推理完成 · {elapsed:.1f} 秒", state="complete")
            engine_slot.markdown(html_engine_status("ready"), unsafe_allow_html=True)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "trace": trace,
                    "elapsed": round(elapsed, 1),
                }
            )
            st.write_stream(typewriter(answer), cursor="▍")
        except Exception as exc:
            elapsed = time.perf_counter() - started
            status.update(label="请求未完成", state="error")
            engine_slot.markdown(html_engine_status("error"), unsafe_allow_html=True)
            st.error(
                "服务暂时不可用。请确认 DASHSCOPE_API_KEY 配置正确，并检查网络与知识库连接后重试。",
                icon=":material/settings:",
            )
            with st.expander("查看错误详情", icon=":material/bug_report:"):
                st.code(f"{type(exc).__name__}: {exc}")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "抱歉，本次请求未能完成。",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )


if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.pop("message", [])

notice = st.session_state.pop("notice", None)

messages = st.session_state.messages
typed_prompt = st.chat_input(
    "描述您的问题，例如：扫地机器人边刷不转怎么办？",
    key="chat_input",
    submit_mode="disable",
)
pending_prompt = st.session_state.pop("pending_prompt", None)
prompt = pending_prompt or typed_prompt
if prompt:
    prompt = str(prompt).strip()
is_landing = not messages and not prompt

with st.sidebar:
    st.html(html_sidebar_brand())
    st.html(html_sidebar_label("能力矩阵", "Capabilities"))
    st.html(html_capabilities())
    st.html(html_sidebar_label("快捷提问", "Quick Prompts"))
    for index, (label, prompt_text, icon_name) in enumerate(QUICK_PROMPTS):
        if st.button(
            label,
            key=f"zst_sbq_{index}",
            icon=f":material/{icon_name}:",
            width="stretch",
        ):
            st.session_state.pending_prompt = prompt_text
            st.rerun()
    engine_slot = st.empty()
    engine_slot.markdown(html_engine_status("ready"), unsafe_allow_html=True)
    if st.button(
        "清空当前会话",
        key="zst_clear",
        icon=":material/restart_alt:",
        width="stretch",
        disabled=not (messages or prompt),
    ):
        st.session_state.messages = []
        st.session_state.notice = "会话已清空"
        st.rerun()
    st.html(html_sidebar_footer())

st.html(html_topbar(landing=is_landing))

if is_landing:
    st.html(html_hero())
    st.html(html_welcome())
    st.html(html_features())
    st.html(html_suggestions_label())
    suggestion_columns = st.columns(4, gap="small")
    for index, (label, prompt_text, icon_name) in enumerate(SUGGESTIONS):
        with suggestion_columns[index]:
            if st.button(
                label,
                key=f"zst_suggest_{index}",
                icon=f":material/{icon_name}:",
                width="stretch",
            ):
                st.session_state.pending_prompt = prompt_text
                st.rerun()
    st.iframe(LANDING_SCROLL_GUARD, height=1)
else:
    st.html(html_rule("对话记录"))
    for message in messages:
        render_message(message)

if prompt:
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    render_message(user_message)
    render_assistant_turn(prompt, engine_slot)

if notice:
    st.toast(notice, icon=":material/check_circle:")
