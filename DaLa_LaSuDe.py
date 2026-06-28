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
- Alu: 2 lop nhom + loi nhua PE, day 2-3-4mm, kich thuoc 1220x2440mm
- Mica Dai Loan: 180k-220k/m2, ben 8-10 nam - KHUYEN DUNG
- Mica Trung Quoc: re hon 40%, o vang sau 6 thang - chi dung su kien
- Inox 304: pho bien nhat, ngoai troi - KHUYEN DUNG
- Han TIG cho inox mong, dong 40-60A, que han 1.6mm
- LED Day 12V: 8.64W/m thuong, 13W/m loai tot
- Quy tac: 1m LED day = 1A nguon 12V
- LED chop nhay: nguon yeu. LED cuoi toi: day qua dai
- Ty ren M4: chu nho. M6: chu vua. M8-M10: chu lon
- Inox o vang: kem tay inox + danh theo tho
- GIA: Mica DL 180k-220k/m2, Alu 150k-250k/m2, Inox 304 350k-500k/m2
- QUY TAC: Ky thuat phai chinh xac. Neu khong chac thi noi thang."""

lich_su = {}

def gui_telegram(chat_id, text, reply_to=None):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_to:
        data["reply_to_message_id"] = reply_to
    try:
        r = requests.post(url, json=data, timeout=15)
        return r.json()
    except Exception as e:
        logging.error("Loi Telegram: " + str(e))

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
        logging.error("Claude error: " + str(data))
        return None
    except Exception as e:
        logging.error("Loi Claude: " + str(e))
        return None

def nen_reply(text):
    if not text:
        return False
    t = text.lower()
    if "la su de" in t or "@lasudedalab" in t:
        return True
    kw_list = ["lam sao", "bi loi", "xu ly", "cach lam", "tai sao",
               "bao nhieu", "led", "mica", "inox", "alu", "nguon",
               "bi o", "bi tat", "bi chop", "bi vang", "mui khoan",
               "ty ren", "tac ke", "silicon", "ampe", "watt", "volt"]
    for kw in kw_list:
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
    if not text or len(text) < 2:
        return
    if sender.get("is_bot"):
        return
    ten = sender.get("first_name", "Anh")
    if not nen_reply(text):
        return
    logging.info("Nhan tin tu " + ten + ": " + text[:50])
    noi_dung = text.replace("@LaSuDeDaLaBot", "").strip()
    prompt = "[" + ten + " hoi]: " + noi_dung
    tra_loi = hoi_claude(prompt, chat_id)
    if tra_loi:
        gui_telegram(chat_id, tra_loi, reply_to=msg_id)

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    print("La Su De da khoi dong!")
    offset = 0
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/getUpdates"
    while True:
        try:
            r = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            data = r.json()
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    xu_ly(update)
            else:
                time.sleep(5)
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            logging.error("Loi: " + str(e))
            time.sleep(5)

if __name__ == "__main__":
    main()
