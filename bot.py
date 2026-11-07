"""Tinchlik Yemxona boti: ratsion kalkulyatori + katalog (mini app) + buyurtma qabul qilish.

Render > Environment bo'limida kiritiladi:
    BOT_TOKEN   (9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE)  BotFather bergan token
    ADMIN_ID    (8630108906) sotuvchi Telegram ID, bir nechta bo'lsa vergul bilan: 111,222
    WEBAPP_URL  (https://tinchlik-yemxona.onrender.com) katalog manzili
"""
import asyncio
import hashlib
import hmac
import html
import json
import logging
import os
import time
from datetime import datetime
from urllib.parse import parse_qsl

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, WebAppInfo)

log = logging.getLogger("yemxona")

# ---------------- SOZLAMALAR ----------------
TOKEN = os.environ["9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE"]
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_ID", "8630108906").replace(" ", "").split(",") if x]
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://tinchlik-yemxona.onrender.com")
BASE = os.path.dirname(os.path.abspath(__file__))

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

fmt = lambda n: f"{int(n):,}".replace(",", " ")
esc = lambda s: html.escape(str(s))


# ---------------- RATSION MA'LUMOTLARI ----------------
# Raqamlarni o'zgartirish uchun faqat shu qismni tahrirlang.
ANIMALS = {
    "buqa": ("🐂 Buqani Semirtirish (Go'sht)", "🐂 Buqaning vaznini tanlang:",
             [("⚖️ 300 - 350 kg", "buqa_350"), ("⚖️ 400 - 450 kg", "buqa_450")]),
    "sigir": ("🐄 Sigirning Sutini Oshirish", "🐄 Sigirning vaznini tanlang:",
              [("⚖️ 350 - 400 kg", "sigir_400"), ("⚖️ 450 - 500 kg", "sigir_500")]),
    "qoy": ("🐑 Qo'y va Sovliqlarni Boqish", "🐑 Qo'yning vaznini tanlang:",
            [("⚖️ 40 - 50 kg", "qoy_50"), ("⚖️ 60 - 70 kg", "qoy_70")]),
}

RATIONS = {
    "buqa_450": ("🐂 400–450 kg Buqa Uchun Semirtirish Ratsioni (3 Mahal)", [
        ("🌅 1-mahal (Ertalabki to'yintiruvchi ovqat)", [("Silyos", "8 kg"), ("MasterFeed (Buqalar uchun)", "2 kg"), ("Kepak (Motabar)", "1.5 kg"), ("Arpa (maydalangan)", "1 kg"), ("Mayda tuz", "20 gramm")]),
        ("☀️ 2-mahal (Tushlik payti)", [("Silyos", "5 kg"), ("Kunjara", "1 kg"), ("Kepak", "0.5 kg")]),
        ("🌙 3-mahal (Kechki to'yintiruvchi ovqat)", [("Silyos", "7 kg"), ("MasterFeed (Buqalar uchun)", "1.5 kg"), ("Arpa (maydalangan)", "1 kg"), ("Kunjara", "0.5 kg")]),
    ]),
    "buqa_350": ("🐂 300–350 kg Buqa Uchun Semirtirish Ratsioni (3 Mahal)", [
        ("🌅 1-mahal (Ertalab)", [("Silyos", "6 kg"), ("MasterFeed", "1.5 kg"), ("Kepak", "1 kg"), ("Arpa", "0.8 kg"), ("Tuz", "15 gramm")]),
        ("☀️ 2-mahal (Tushlik)", [("Silyos", "4 kg"), ("Kunjara", "0.7 kg"), ("Kepak", "0.3 kg")]),
        ("🌙 3-mahal (Kechqurun)", [("Silyos", "5 kg"), ("MasterFeed", "1 kg"), ("Arpa", "0.7 kg"), ("Kunjara", "0.3 kg")]),
    ]),
    "sigir_500": ("🐄 450–500 kg Sigir Uchun Sut Oshirish Ratsioni (3 Mahal)", [
        ("🌅 1-mahal (Ertalabki sog'imdan oldin)", [("Silyos", "8 kg"), ("MasterFeed (Sigirlar uchun)", "2.5 kg"), ("Kepak (Motabar)", "1.5 kg"), ("Arpa", "1 kg"), ("Mayda tuz", "20 gramm")]),
        ("☀️ 2-mahal (Tushlik payti)", [("Silyos", "5 kg"), ("Kunjara", "0.5 kg"), ("Raps Shrot", "0.3 kg")]),
        ("🌙 3-mahal (Kechqurun, sog'imdan keyin)", [("Silyos", "7 kg"), ("MasterFeed (Sigirlar uchun)", "2 kg"), ("Kepak", "1 kg"), ("Vitamin tuz", "10 gramm")]),
    ]),
    "sigir_400": ("🐄 350–400 kg Sigir Uchun Sut Oshirish Ratsioni (3 Mahal)", [
        ("🌅 1-mahal (Ertalab)", [("Silyos", "7 kg"), ("MasterFeed", "2 kg"), ("Kepak", "1 kg"), ("Arpa", "0.8 kg"), ("Tuz", "15 gramm")]),
        ("☀️ 2-mahal (Tushlik)", [("Silyos", "4 kg"), ("Kunjara", "0.4 kg")]),
        ("🌙 3-mahal (Kechqurun)", [("Silyos", "6 kg"), ("MasterFeed", "1.5 kg"), ("Kepak", "0.8 kg"), ("Raps Shrot", "0.3 kg")]),
    ]),
    "qoy_70": ("🐑 60–70 kg Qo'y / Sovliq Uchun Semirtirish Ratsioni (3 Mahal)", [
        ("🌅 1-mahal (Ertalab)", [("Silyos", "1.8 kg"), ("MasterFeed (Universal)", "0.5 kg"), ("Kepak", "0.3 kg"), ("Tuz", "5 gramm")]),
        ("☀️ 2-mahal (Tushlik)", [("Silyos", "1.2 kg"), ("Arpa (maydalangan)", "0.3 kg"), ("Kunjara", "0.2 kg")]),
        ("🌙 3-mahal (Kechqurun)", [("Silyos", "1.5 kg"), ("MasterFeed (Universal)", "0.4 kg"), ("Kepak", "0.3 kg")]),
    ]),
    "qoy_50": ("🐑 40–50 kg Qo'y / Sovliq Uchun Ratsion (3 Mahal)", [
        ("🌅 1-mahal (Ertalab)", [("Silyos", "1.3 kg"), ("MasterFeed", "0.4 kg"), ("Kepak", "0.2 kg"), ("Tuz", "3 gramm")]),
        ("☀️ 2-mahal (Tushlik)", [("Silyos", "0.8 kg"), ("Arpa", "0.2 kg"), ("Kunjara", "0.15 kg")]),
        ("🌙 3-mahal (Kechqurun)", [("Silyos", "1.1 kg"), ("MasterFeed", "0.3 kg"), ("Kepak", "0.2 kg")]),
    ]),
}


def ration_text(key: str) -> str:
    title, meals = RATIONS[key]
    out = [f"<b>{title}</b>", "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>", ""]
    for meal, items in meals:
        out.append(f"<b>{meal}:</b>")
        out += [f"• {n}: <b>{a}</b>" for n, a in items]
        out.append("")
    out.append("🛒 <b>Kerakli yem-hasaklarni buyurtma qiling:</b>")
    return "\n".join(out)


# ---------------- KLAVIATURALAR ----------------
def btn(text, data):
    return InlineKeyboardButton(text=text, callback_data=data)


def catalog_btn(text="🛒 Tinchlik Yemxona Katalogi"):
    return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=WEBAPP_URL))


def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("🐂 Aqlli Ratsion Kalkulyatori (3 Mahal)", "open_calc")],
        [catalog_btn()],
    ])


WELCOME = (
    "<b>Assalomu alaykum, hurmatli mijozimiz! 😊</b>\n\n"
    "\"Tinchlik Yemxona\" rasmiy botiga xush kelibsiz.\n\n"
    "Moldingiz uchun 100% natija beradigan 3 mahal kundalik ratsionni hisoblash "
    "yoki mahsulotlarni tanlab buyurtma berish uchun quyidagi tugmalardan foydalaning:"
)


# ---------------- MIJOZ TOMONI ----------------
@router.message(Command("start"))
async def cmd_start(m: Message):
    await m.answer(WELCOME, reply_markup=main_kb())


@router.callback_query(F.data == "back_to_start")
async def back_to_start(cb: CallbackQuery):
    await cb.message.edit_text(WELCOME, reply_markup=main_kb())
    await cb.answer()


@router.callback_query(F.data == "open_calc")
async def open_calc(cb: CallbackQuery):
    rows = [[btn(label, f"calc_{k}")] for k, (label, _, _) in ANIMALS.items()]
    rows.append([btn("🔙 Orqaga", "back_to_start")])
    await cb.message.edit_text(
        "<b>🐂 \"Tinchlik Yemxona\" Ratsion Kalkulyatori</b>\n\n"
        "Qaysi turdagi jonivor uchun ratsion hisoblamoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()


@router.callback_query(F.data.in_({f"calc_{k}" for k in ANIMALS}))
async def pick_weight(cb: CallbackQuery):
    _, question, weights = ANIMALS[cb.data[5:]]
    rows = [[btn(label, key)] for label, key in weights]
    rows.append([btn("🔙 Orqaga", "open_calc")])
    await cb.message.edit_text(f"<b>{question}</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()


@router.callback_query(F.data.in_(set(RATIONS)))
async def show_ration(cb: CallbackQuery):
    back = f"calc_{cb.data.split('_')[0]}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[catalog_btn("🛒 Katalogdan sotib olish")], [btn("🔙 Orqaga", back)]])
    await cb.message.edit_text(ration_text(cb.data), reply_markup=kb)
    await cb.answer()


@router.message(F.photo)
async def receipt(m: Message):
    """Mijoz to'lov chekini yuborsa, sotuvchiga uzatiladi."""
    u = m.from_user
    if u.id in ADMIN_IDS:
        return
    caption = f"🧾 <b>To'lov cheki</b>\n👤 <a href='tg://user?id={u.id}'>{esc(u.full_name)}</a>"
    for admin in ADMIN_IDS:
        try:
            await bot.send_photo(admin, m.photo[-1].file_id, caption=caption)
        except Exception:
            log.exception("Chekni adminga yuborib bo'lmadi: %s", admin)
    await m.answer("✅ Chekingiz qabul qilindi, rahmat!")


# ---------------- SOTUVCHI (ADMIN) TUGMALARI ----------------
STATUS = {
    "acc": ("✅ Qabul qilindi", "✅ Buyurtmangiz qabul qilindi. Tez orada yetkazib berish tashkil qilinadi."),
    "way": ("🚚 Yo'lda", "🚚 Buyurtmangiz yo'lga chiqdi. Iltimos, telefoningiz yoningizda bo'lsin."),
    "done": ("📦 Yetkazildi", "📦 Buyurtmangiz yetkazildi. Xaridingiz uchun rahmat! 🌾"),
    "cancel": ("❌ Bekor qilindi", "❌ Buyurtmangiz bekor qilindi. Savollaringiz bo'lsa, sotuvchi bilan bog'laning."),
}


def admin_kb(uid, oid):
    b = lambda code: InlineKeyboardButton(text=STATUS[code][0], callback_data=f"st:{code}:{uid}:{oid}")
    return InlineKeyboardMarkup(inline_keyboard=[[b("acc"), b("way")], [b("done"), b("cancel")]])


@router.callback_query(F.data.startswith("st:"))
async def set_status(cb: CallbackQuery):
    if cb.from_user.id not in ADMIN_IDS:
        return await cb.answer("Sizda ruxsat yo'q", show_alert=True)
    try:
        _, code, uid, oid = cb.data.split(":")
        label, text = STATUS[code]
    except (ValueError, KeyError):
        return await cb.answer("Xatolik")
    base = cb.message.html_text.split("\n\n📌")[0]
    await cb.message.edit_text(f"{base}\n\n📌 Holat: <b>{label}</b>", reply_markup=cb.message.reply_markup)
    try:
        await bot.send_message(int(uid), f"{text}\n\n<i>Buyurtma №{oid}</i>")
        await cb.answer("Mijozga xabar yuborildi")
    except Exception:
        await cb.answer("Mijozga xabar yuborib bo'lmadi (botni bloklagan bo'lishi mumkin)", show_alert=True)


@router.message(F.text)
async def fallback(m: Message):
    await m.answer("Menyuni ochish uchun /start ni bosing 👇", reply_markup=main_kb())


# ---------------- MINI APP BILAN ALOQA (BUYURTMA) ----------------
def verify_init_data(init_data: str):
    """Telegram imzosini tekshiradi: faqat haqiqiy mini app foydalanuvchisi buyurtma bera oladi."""
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
        got = pairs.pop("hash")
        check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
        secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, got):
            return None
        if time.time() - int(pairs.get("auth_date", 0)) > 2 * 86400:
            return None
        return json.loads(pairs["user"])
    except Exception:
        return None


def clean_items(raw):
    items = []
    for i in list(raw)[:50]:
        qty, price = float(i["qty"]), int(i["price"])
        if not (0 < qty <= 100000 and 0 <= price <= 100_000_000):
            raise ValueError("noto'g'ri miqdor yoki narx")
        items.append({"name": str(i["name"])[:80], "unit": str(i["unit"])[:30], "qty": qty, "price": price})
    if not items:
        raise ValueError("savat bo'sh")
    return items


async def api_order(request: web.Request):
    try:
        d = await request.json()
    except Exception:
        return web.json_response({"status": "error"}, status=400)

    user = verify_init_data(str(d.get("init_data", "")))
    if not user:
        return web.json_response({"status": "error", "message": "auth"}, status=403)
    try:
        items = clean_items(d["items"])
        phone = str(d["phone"]).strip()[:25]
        if not 9 <= sum(c.isdigit() for c in phone) <= 15:
            raise ValueError("telefon")
    except Exception:
        return web.json_response({"status": "error", "message": "data"}, status=400)

    card = d.get("payment_type") == "card"
    uid = user["id"]
    oid = datetime.now().strftime("%d%H%M%S")
    total = sum(int(i["qty"] * i["price"]) for i in items)
    lines = [f"• {esc(i['name'])} — {i['qty']:g} {esc(i['unit'])} = <b>{fmt(i['qty'] * i['price'])}</b> so'm" for i in items]
    name = esc(((user.get("first_name") or "") + " " + (user.get("last_name") or "")).strip() or "Mijoz")
    uname = f" (@{esc(user['username'])})" if user.get("username") else ""

    text = (
        f"🆕 <b>YANGI BUYURTMA №{oid}</b> (dastavka)\n\n"
        f"👤 <a href='tg://user?id={uid}'>{name}</a>{uname}\n"
        f"📞 Telefon: <b>{esc(phone)}</b>\n"
        f"💳 To'lov: {'Karta (chek botga yuboriladi)' if card else 'Naqd pul'}\n\n"
        + "\n".join(lines)
        + f"\n\n💰 Jami: <b>{fmt(total)} so'm</b>\n\n"
        "☎️ Mijozga qo'ng'iroq qilib manzilni aniqlang."
    )
    sent = 0
    for admin in ADMIN_IDS:
        try:
            await bot.send_message(admin, text, reply_markup=admin_kb(uid, oid))
            sent += 1
        except Exception:
            log.exception("Adminga yuborib bo'lmadi: %s", admin)
    if not sent:
        return web.json_response({"status": "error", "message": "admin"}, status=502)

    try:
        extra = "\n\n📸 Karta orqali to'lagan bo'lsangiz, <b>chek rasmini shu yerga yuboring</b>." if card else ""
        await bot.send_message(
            uid,
            f"✅ <b>Buyurtmangiz qabul qilindi!</b> (№{oid})\n💰 Jami: <b>{fmt(total)} so'm</b>\n\n"
            f"Tez orada sotuvchi siz bilan bog'lanib, manzilni so'raydi.{extra}")
    except Exception:
        log.warning("Mijozga tasdiq yuborib bo'lmadi: %s", uid)
    return web.json_response({"status": "success", "order_id": oid})


async def index(request: web.Request):
    return web.FileResponse(os.path.join(BASE, "index.html"))


async def health(request: web.Request):
    return web.Response(text="ok")


async def web_server():
    app = web.Application(client_max_size=1024 * 64)
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    app.router.add_post("/api/order", api_order)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000))).start()
    await asyncio.Event().wait()


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(dp.start_polling(bot), web_server())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())