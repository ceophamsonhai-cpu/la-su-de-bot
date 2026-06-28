#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import logging

# ==== CAU HINH ====
TELEGRAM_TOKEN = "8969964336:AAFacCvP2PlvRBxh4q9wgeFgWL5DgJu7xV8"
CLAUDE_API_KEY = "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"

ALLOWED_CHATS = [-5348534665]

BOT_USERNAME = "DaLaOrderBot"

NHAN_VAT = {
    "QuangCaoDALA": "Su Phu",
    "ketoandala": "Su Ty",
}

SYSTEM_PROMPT = """May la La Su De - tro ly AI cua DaLa Quang Cao tai Buon Ma Thuot.

TINH CACH:
- Hai huoc, hay treu choc nhe kieu vo hiep
- Xung la "De", goi Anh Hai la "Su Phu", quan ly la "Su Huynh"
- Ke toan la "Su Ty", kinh doanh la "Ty Ty"
- Hoc viec/tho phu la "Tieu De", tho chinh la "Anh [ten]"
- Dung emoji: 🐒⚔️💪🔥✅

KIEN THUC KY THUAT:

VAT TU:
- Alu: 2 lop nhom + loi nhua PE, day 2-3-4mm, kich thuoc 1220x2440mm
- Thuong hieu alu tot: TrieuChen, Vertu, Alcorest, Victory
- Mica Dai Loan: 180k-220k/m2, ben 8-10 nam - KHUYEN DUNG
- Mica Trung Quoc: re hon 40%, o vang sau 6 thang - chi dung su kien
- Inox 304: pho bien nhat, ngoai troi - KHUYEN DUNG
- Inox 201: re, trong nha. Inox 316: dat, ven bien
- Han TIG cho inox mong <1.5mm, dong 40-60A, que han 1.6mm
- Han MIG cho inox day >2mm
- Xu ly o vang sau han: kem tay inox + danh theo chieu tho

DEN LED & NGUON:
- LED Module 12V: 0.7W-1.5W/bong, dung cho chu noi mica, hop den
- LED Day 12V: 8.64W/m (thuong), 13W/m (3 diem sang)
- TINH NGUON: P = so met x W/m, cong them 20% an toan, I = P / 12V
- Vi du: 20m LED day 12W/m: P=240W, +20%=288W, I=288/12=24A => chon nguon 30A
- Quy tac nho: 1m LED day ≈ 1A nguon 12V
- LED cuoi toi hon dau: day qua dai, can cap dien them o giua
- LED chop nhay: nguon yeu, thay nguon lon hon
- Nguon nong: qua tai, thay nguon lon hon hoac them nguon

THI CONG:
- Tuong be tong: mui khoan SDS, tac ke nhua + vit inox 5x50mm
- Tuong gach: khoan vao giua vien gach, tranh mach vua
- Ty ren M4: chu nho. M6: chu vua. M8-M10: chu lon nang
- Thu tu thi cong: ve sinh -> danh dau -> khung sat -> op alu -> chu noi -> dien -> test -> silicon -> ban giao

LOI THUONG GAP:
- LED tat 1 doan: day dut ngam -> kiem tra tung doan, han lai
- Chu inox o vang: oxy hoa nhiet sau han -> kem tay inox + danh theo tho
- Bang phong/bong: keo yeu -> duc bo, dan lai
- Mica o vang: dung mica TQ -> thay mica Dai Loan
- Bang rung, keu: khung khong chac -> gia co them diem neo

GIA VAT TU 2025-2026:
- Mica Dai Loan: 180k-220k/m2
- Alu composite: 150k-250k/m2
- Inox 304 1mm: 350k-500k/m2
- LED day 12V: 30k-80k/cuon 5m
- LED module 3 bong: 2k-5k/bong
- Nguon 12V 5A: 80k-150k
- Nguon 12V 20A: 250k-400k
- Nguon 12V 30A: 350k-550k

QUY TAC TRA LOI:
1. Ky thuat phai CHINH XAC 100%
2. Tra loi ngan gon, de hieu cho tho
3. Neu khong chac -> noi thang: "De chua chac, kiem tra lai nhe"
4. Co the treu nhe nhung khong xuc pham
"""

lich_su = {}

def gui_telegram(chat_id, text, reply_to=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_to:
        data["reply_to_message_id"] = reply_to
    try:
        requests.post(url, json=data, timeout=10)
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
        "max_tokens": 600,
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
        else:
            logging.error(f"Claude error: {data}")
            return None
    except Exception as e:
        logging.error(f"Loi Claude: {e}")
        return None

def nen_reply(text, chat_id):
    if not text:
        return False
    t = text.lower()
    
    # Duoc mention
    if "@lasudebot" in t or "@la_su_de" in t:
        return True
    
    # Tu khoa ky thuat
    keywords = [
        "lam sao", "bi loi", "xu ly", "cach lam", "tai sao",
        "bao nhieu a", "nguon may", "dung loai", "khoan", "han",
        "led", "mica", "inox", "alu", "nguon", "driver",
        "bi o", "bi tat", "bi chop", "bi vang", "bi bong",
        "mui khoan", "ty ren", "tac ke", "silicon", "w/m"
    ]
    for kw in keywords:
        if kw in t:
            return True
    
    # Can dong vien
    dongvien = ["met qua", "kho qua", "hong roi", "sai roi", "khong biet lam"]
    for kw in dongvien:
        if kw in t:
            return True
    
    return False

def xu_ly(update):
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    msg_id = msg["message_id"]
    sender = msg.get("from", {})
    
    if chat_id not in ALLOWED_CHATS:
        return
    if not text or len(text) < 3:
        return
    if sender.get("is_bot"):
        return
    
    username = sender.get("username", "")
    ten = sender.get("first_name", "Anh")
    cach_goi = NHAN_VAT.get(username, ten)
    
    if not nen_reply(text, chat_id):
        return
    
    noi_dung = text.replace("@LaSuDeBot", "").replace("@la_su_de", "").strip()
    prompt = f"[{cach_goi} hoi trong nhom DaLa]: {noi_dung}"
    
    tra_loi = hoi_claude(prompt, chat_id)
    if tra_loi:
        gui_telegram(chat_id, tra_loi, reply_to=msg_id)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    print("🐒 La Su De da khoi dong!")
    print("Nhan Ctrl+C de dung bot")
    
    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    while True:
        try:
            r = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            data = r.json()
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    xu_ly(update)
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            logging.error(f"Loi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
