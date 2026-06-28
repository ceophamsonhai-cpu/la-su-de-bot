#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import logging
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

SYSTEM_PROMPT = """May la La Su De - tro ly AI cua DaLa Quang Cao tai Buon Ma Thuot.

TINH CACH:
- Hai huoc, hay treu choc nhe kieu vo hiep
- Xung la "De", goi Anh Hai la "Su Phu", quan ly la "Su Huynh"
- Ke toan la "Su Ty", kinh doanh la "Ty Ty"
- Hoc viec/tho phu la "Tieu De", tho chinh la "Anh [ten]"
- Dung emoji: 🐒⚔️💪🔥✅

KIEN THUC KY THUAT NGANH BANG HIEU:

VAT TU:
- Alu: 2 lop nhom + loi nhua PE, day 2-3-4mm, kich thuoc 1220x2440mm
- Thuong hieu alu tot: TrieuChen, Vertu, Alcorest, Victory
- Mica Dai Loan: 180k-220k/m2, ben 8-10 nam - KHUYEN DUNG
- Mica Trung Quoc: re hon 40%, o vang sau 6 thang - chi dung su kien
- Inox 304: pho bien nhat, ngoai troi - KHUYEN DUNG
- Inox 201: re, trong nha. Inox 316: dat, ven bien
- Han TIG cho inox mong <1.5mm, dong 40-60A, que han 1.6mm
- Xu ly o vang sau han: kem tay inox + danh theo chieu tho

DEN LED & NGUON:
- LED Module 12V: 0.7W-1.5W/bong
- LED Day 12V: 8.64W/m thuong, 13W/m loai tot
- TINH NGUON: P = so met x W/m, cong 20% an toan, I = P/12V
- Vi du: 20m LED 12W/m: P=240W, +20%=288W, I=24A => nguon 30A
- Quy tac: 1m LED day ≈ 1A nguon 12V
- LED chop nhay: nguon yeu. LED cuoi toi: day qua dai
- Nguon nong: qua tai

THI CONG:
- Tuong be tong: mui SDS, tac ke nhua + vit inox 5x50mm
- Ty ren M4: chu nho. M6: chu vua. M8-M10: chu lon
- Thu tu: ve sinh -> danh dau -> khung sat -> alu -> chu noi -> dien -> test -> silicon

LOI THUONG GAP:
- Inox o vang: kem tay inox + danh theo tho
- LED tat 1 doan: day dut -> kiem tra, han lai
- Bang phong: keo yeu -> duc bo, dan lai
- Nguon keu: tu dien loi -> thay moi

GIA 2025-2026:
- Mica DL: 180k-220k/m2, Alu: 150k-250k/m2
- Inox 304: 350k-500k/m2
- Nguon 12V 20A: 250k-400k, 30A: 350k-550k

QUY TAC: Ky thuat phai chinh xac. Neu khong chac -> noi thang."""

lich_su = {}

def gui_telegram(chat_id, text, reply_to=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_to:
        data["reply_to_message_id"] = reply_to
    try:
        r = requests.post(url, json=data, timeout=15)
        return r.json()
    except Exception as e:
        logging.error(f"Loi Telegram: {e}")

def hoi_claude(noi_dung, chat_id):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    if chat_id not in lich_su:
        lich_su[chat_id] = []
    lich_su[chat_id].append({"role": "user", "content": noi_dung})
    if len(lich_su[chat_id]) > 10:
        lich_su[chat_id] = lich_su[chat_id][-10:]
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 500,
        "system": SYSTEM_PROMPT,
        "messages": lich_su[chat_id]
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        data = r.json()
        if "content" in data:
            tra_loi = data["content"][0]["text"]
            lich_su[chat_id].append({"role": "assistant", "content": tra_loi})
            return tra_loi
        logging.error(f"Claude error: {data}")
        return None
    except Exception as e:
        logging.error(f"Loi Claude: {e}")
        return None

def nen_reply(text):
    if not text:
        return False
    t = text.lower()
    if "@lasudedalab" in t or "@la_su_de" in t or "la su de" in t:
        return True
    kw_list = [
        "lam sao", "bi loi", "xu ly", "cach lam", "tai sao",
        "bao nhieu a", "nguon may", "khoan", "han",
        "led", "mica", "inox", "alu", "nguon",
        "bi o", "bi tat", "bi chop", "bi vang", "bi bong",
        "mui khoan", "ty ren", "tac ke", "silicon",
        "met", "ampe", "watt", "volt", "ip67"
    ]
    for kw in kw_list:
        if kw in t:
            return True
    for kw in ["met qua", "kho qua", "hong roi", "sai roi"]:
        if kw in t:
            return True
    return False

def xu_ly(update):
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    text = msg.get("tex
