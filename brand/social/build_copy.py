#!/usr/bin/env python3
"""Generate SOCIAL-COPY.md: per-image, per-platform ready-to-paste copy with exact character counts."""
import pathlib

EN_NAME   = "BIOHACK.IT"
EN_NAME_L = "BIOHACK.IT — Hacking Biology"
ZH_NAME   = "BIOHACK.IT 生物黑客"

EN_TAG    = "Turn self-experimentation into evidence."
EN_CAT    = "Open infrastructure for structured human self-experimentation."
EN_PAYOFF = "An open laboratory for longevity."

ZH_TAG    = "把自我实验变成证据。"
ZH_CAT    = "面向结构化人体自我实验的开放基础设施。"
ZH_PAYOFF = "一个开放的长寿实验室。"

EN_SHORT  = f"{EN_TAG} {EN_CAT} Non-profit · open source · biohack.it"
EN_MED    = ("Document your protocol, measure it with standards-coded biomarkers, and share it — "
             "so thousands of individual experiments become comparable human data. "
             "Safety engineered in, not bolted on. Open source, non-profit. biohack.it")
EN_LONG   = (
 "BIOHACK.IT is open infrastructure for structured human self-experimentation.\n\n"
 "Document what you take and do — substances, therapies, exercise, nutrition — with dose, timing and real cycle "
 "schemas. Measure efficacy and safety with standards-coded biomarkers (LOINC/UCUM), including biological clocks. "
 "Upload the lab reports you already have and get your history in graphs, free. Then share your protocol and its "
 "outcomes, so that thousands of individual experiments become comparable human data.\n\n"
 "Safety is engineered in, not bolted on: follow a protocol and you inherit its safety markers and a mandatory baseline.\n\n"
 "We are not a clinical trial, and we say so first. This is self-managed, self-declared, self-selected "
 "experimentation — no randomisation, no blinding. The honest comparison is not against a trial, but against what "
 "exists today: a dose written in prose, a screenshot of a lab report, a spreadsheet nobody else can open.\n\n"
 "Open source under AGPL-3.0. A non-profit project of the Hacking Biology Foundation.\n"
 "https://biohack.it")

ZH_SHORT  = f"{ZH_TAG}{ZH_CAT}开源·非营利。biohack.it"
ZH_MED    = ("记录你的方案，用标准编码的生物标志物测量效果与安全性，并公开分享——"
             "让成千上万个体实验成为可比较的人类数据。安全内建，而非事后附加。开源·非营利。biohack.it")
ZH_LONG   = (
 "BIOHACK.IT 是面向结构化人体自我实验的开放基础设施。\n\n"
 "记录你所服用和所做的一切——药物、疗法、运动、营养——包含剂量、时间与真实的周期方案；"
 "用标准编码（LOINC/UCUM）的生物标志物测量有效性与安全性，并支持生物年龄时钟。"
 "上传你已有的化验报告，免费获得你的历史曲线。然后公开分享你的方案与结果，"
 "让成千上万个体实验成为可比较的人类数据。\n\n"
 "安全是内建的，而非事后附加：采用他人方案时，其安全标志物与强制基线检测会一并继承。\n\n"
 "我们不是临床试验，并且我们首先说明这一点。这是自我管理、自我申报、自我选择的实验，"
 "没有随机化，也没有盲法。诚实的比较对象不是临床试验，而是今天的现状："
 "写在论坛帖子里的剂量、化验单截图、别人打不开的表格。\n\n"
 "开源许可 AGPL-3.0，由 Hacking Biology 基金会运营的非营利项目。\n"
 "https://biohack.it")

def fit(text, limit):
    """Trim to limit on a word/char boundary, never mid-word for latin."""
    if len(text) <= limit: return text
    cut = text[:limit]
    return (cut.rsplit(" ", 1)[0] if " " in cut[-20:] else cut).rstrip(" ,·—-")

# (image file, platform, [(field, limit, text)])
PLATFORMS = [
 ("x-header.png", "X / Twitter — header 1500×500", [
   ("Name", 50, EN_NAME_L), ("Bio", 160, EN_SHORT), ("Location", 30, "Open source · worldwide")]),
 ("linkedin-company.png", "LinkedIn — company page cover 1128×191", [
   ("Page name", 100, EN_NAME_L), ("Tagline", 120, f"{EN_TAG} {EN_CAT}"), ("About", 2000, EN_LONG)]),
 ("linkedin-profile.png", "LinkedIn — personal profile cover 1584×396", [
   ("Headline", 220, f"{EN_CAT} · Founder, BIOHACK.IT — {EN_TAG}"), ("About", 2600, EN_LONG)]),
 ("youtube-channel.png", "YouTube — channel art 2560×1440 (safe area 1546×423)", [
   ("Channel name", 100, EN_NAME_L), ("Handle", 30, "@biohackit"), ("Description", 1000, EN_LONG)]),
 ("facebook-cover.png", "Facebook — page cover 820×312", [
   ("Page name", 75, EN_NAME_L), ("Short description", 101, EN_TAG + " Open, non-profit."), ("About", 255, EN_MED)]),
 ("square-1080.png", "Instagram / general square 1080×1080", [
   ("Name", 30, EN_NAME), ("Bio", 150, f"{EN_TAG}\n{EN_CAT}\nOpen source · non-profit")]),
 ("telegram-preview.png", "Telegram — channel · preview 1200×630 (link/pinned) + avatar telegram-avatar-512.png", [
   ("Channel name", 128, EN_NAME_L), ("Description", 255, EN_MED), ("Description (中文)", 255, ZH_MED)]),
 ("weibo-cover.png", "微博 Weibo — cover 920×300", [
   ("昵称 Nickname", 30, ZH_NAME), ("简介 Bio", 140, ZH_SHORT), ("Bio (EN)", 140, EN_SHORT)]),
 ("wechat-cover.png", "微信公众号 WeChat Official Account — cover 900×383", [
   ("名称 Name", 30, ZH_NAME), ("功能介绍 Description", 120, ZH_SHORT), ("Description (EN)", 120, f"{EN_TAG} {EN_CAT}")]),
 ("xiaohongshu-cover.png", "小红书 Xiaohongshu (RED) — vertical 1080×1440", [
   ("昵称 Nickname", 24, ZH_NAME), ("简介 Bio", 100, ZH_MED), ("Bio (EN)", 100, EN_SHORT)]),
 ("banner-wide.png", "Generic wide banner 1600×600 (events, decks, press)", [
   ("Title", 100, f"{EN_NAME} — {EN_PAYOFF}"), ("Subtitle", 200, EN_CAT)]),
 ("avatar-512.png", "Avatar — all platforms (400/512/800/1080 available)", [
   ("Alt text", 125, "BIOHACK.IT mark: a white ring above a teal bar on charcoal.")]),
]

out=["# BIOHACK.IT — social copy",
 "",
 "Ready-to-paste text for every image in this folder, fitted to each platform's field limits.",
 "Character counts are exact (`n/limit`). Chinese provided for the Chinese platforms, with an English",
 "fallback where the field accepts it. Limits are the platform maximums at time of writing — if a field",
 "rejects the text, trim from the end; every entry is written so the first sentence stands alone.",
 "",
 "**Core lines** — reuse anywhere:",
 "",
 f"- Promise — `{EN_TAG}` · `{ZH_TAG}`",
 f"- Category — `{EN_CAT}` · `{ZH_CAT}`",
 f"- Brand payoff — `{EN_PAYOFF}` · `{ZH_PAYOFF}`",
 "- Link — `https://biohack.it` · Source — `https://github.com/hackingbiology/biohackit`",
 "- Telegram — `https://t.me/+0qg9-HC4Nx45OTI8` · Email — `research@hackingbiology.com`",
 "",
 "---",
 ""]

for img, plat, fields in PLATFORMS:
    out.append(f"## {plat}")
    out.append("")
    out.append(f"**Image:** `{img}`")
    out.append("")
    for name, limit, text in fields:
        t=fit(text, limit); n=len(t)
        flag = "" if n<=limit else "  ⚠ OVER"
        out.append(f"**{name}** — {n}/{limit}{flag}")
        out.append("")
        out.append("```")
        out.append(t)
        out.append("```")
        out.append("")
    out.append("---")
    out.append("")

p=pathlib.Path(__file__).resolve().parent/"SOCIAL-COPY.md"
p.write_text("\n".join(out), encoding="utf-8")
print("wrote", p, len("\n".join(out)), "bytes")
