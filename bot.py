"""Tinchlik Yemxona boti: katalog (mini app) + buyurtma qabul qilish + kunlik hisobot.

Render > Environment bo'limida kiritiladi:
    BOT_TOKEN    (majburiy)  BotFather bergan token
    ADMIN_ID     (ixtiyoriy) sotuvchi Telegram ID, bir nechta bo'lsa vergul bilan: 111,222
    WEBAPP_URL   (ixtiyoriy) katalog manzili
    REPORT_HOUR  (ixtiyoriy) kunlik hisobot soati, Toshkent vaqti bilan (standart: 21)
"""
import asyncio
import hashlib
import hmac
import html
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
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
TOKEN = os.environ["BOT_TOKEN"]
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_ID", "8630108906").replace(" ", "").split(",") if x]
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://tinchlik-yemxona-1.onrender.com")
REPORT_HOUR = int(os.environ.get("REPORT_HOUR", "21"))
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.environ.get("DATA_FILE", os.path.join(BASE, "orders.json"))
TZ = timezone(timedelta(hours=5))  # Toshkent (UTC+5)

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

fmt = lambda n: f"{int(n):,}".replace(",", " ")
esc = lambda s: html.escape(str(s))


# ---------------- BUYURTMALAR OMBORI (JSON fayl) ----------------
state = {"orders": [], "last_report": ""}


def load_state():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            state.update(json.load(f))
    except FileNotFoundError:
        pass
    except Exception:
        log.exception("orders.json o'qilmadi, bo'sh holatdan boshlanadi")


def save_state():
    try:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)
        os.replace(tmp, DATA_FILE)
    except Exception:
        log.exception("orders.json yozilmadi")


def add_order(rec: dict):
    cutoff = (datetime.now(TZ) - timedelta(days=90)).strftime("%Y-%m-%d")
    state["orders"] = [o for o in state["orders"] if o["date"] >= cutoff] + [rec]
    save_state()


# ---------------- KUNLIK HISOBOT ----------------
STATUS = {
    "acc": ("✅ Qabul qilindi", "✅ Buyurtmangiz qabul qilindi. Tez orada yetkazib berish tashkil qilinadi."),
    "way": ("🚚 Yo'lda", "🚚 Buyurtmangiz yo'lga chiqdi. Iltimos, telefoningiz yoningizda bo'lsin."),
    "done": ("📦 Yetkazildi", "📦 Buyurtmangiz yetkazildi. Xaridingiz uchun rahmat! 🌾"),
    "cancel": ("❌ Bekor qilindi", "❌ Buyurtmangiz bekor qilindi. Savollaringiz bo'lsa, sotuvchi bilan bog'laning."),
}
STATUS_LABEL = {"new": "🆕 Ko'rilmagan", **{k: v[0] for k, v in STATUS.items()}}


def build_report(day: str) -> str:
    orders = [o for o in state["orders"] if o["date"] == day]
    title = f"📊 <b>KUNLIK HISOBOT: {datetime.strptime(day, '%Y-%m-%d').strftime('%d.%m.%Y')}</b>"
    if not orders:
        return f"{title}\n\nBugun buyurtma bo'lmadi."

    active = [o for o in orders if o["status"] != "cancel"]
    cancelled = len(orders) - len(active)
    total = sum(o["total"] for o in active)
    cash = [o for o in active if o["pay"] == "cash"]
    card = [o for o in active if o["pay"] == "card"]

    lines = [title, "",
             f"🧾 Buyurtmalar: <b>{len(orders)} ta</b>" + (f" (bekor qilingan: {cancelled})" if cancelled else ""),
             f"💰 Jami savdo: <b>{fmt(total)} so'm</b>",
             f"💵 Naqd: {len(cash)} ta — {fmt(sum(o['total'] for o in cash))} so'm",
             f"💳 Karta: {len(card)} ta — {fmt(sum(o['total'] for o in card))} so'm",
             "", "<b>Holatlar:</b>"]
    for code, label in STATUS_LABEL.items():
        n = sum(1 for o in orders if o["status"] == code)
        if n:
            lines.append(f"{label}: {n}")

    prod = {}
    for o in active:
        for i in o["items"]:
            k = (i["name"], i["unit"])
            q, s = prod.get(k, (0, 0))
            prod[k] = (q + i["qty"], s + i["sum"])
    if prod:
        lines += ["", "<b>🏆 Eng ko'p sotilgan:</b>"]
        for (name, unit), (q, s) in sorted(prod.items(), key=lambda x: -x[1][1])[:5]:
            lines.append(f"• {esc(name)} — {q:g} {esc(unit)} ({fmt(s)} so'm)")
    return "\n".join(lines)


async def report_scheduler():
    """Har kuni REPORT_HOUR da (Toshkent vaqti) sotuvchilarga hisobot yuboradi."""
    while True:
        try:
            now = datetime.now(TZ)
            today = now.strftime("%Y-%m-%d")
            if now.hour >= REPORT_HOUR and state["last_report"] != today:
                text = build_report(today)
                for admin in ADMIN_IDS:
                    try:
                        await bot.send_message(admin, text)
                    except Exception:
                        log.exception("Hisobotni yuborib bo'lmadi: %s", admin)
                state["last_report"] = today
                save_state()
        except Exception:
            log.exception("Hisobot rejalovchisida xato")
        await asyncio.sleep(60)


# ---------------- MIJOZ TOMONI ----------------
def catalog_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Tinchlik Yemxona Katalogi", web_app=WebAppInfo(url=WEBAPP_URL))]])


WELCOME = (
    "<b>Assalomu alaykum, hurmatli mijozimiz! 😊</b>\n\n"
    "\"Tinchlik Yemxona\" rasmiy botiga xush kelibsiz.\n\n"
    "Chorvangiz uchun sifatli yem va oziqalarni katalogdan tanlang, "
    "buyurtma bering, biz uyingizgacha yetkazib beramiz.\n\n"
    "Boshlash uchun quyidagi tugmani bosing 👇"
)


@router.message(Command("start"))
async def cmd_start(m: Message):
    await m.answer(WELCOME, reply_markup=catalog_kb())


@router.message(Command("hisobot"))
async def cmd_report(m: Message):
    """Sotuvchi istalgan payt bugungi hisobotni so'rashi mumkin."""
    if m.from_user.id not in ADMIN_IDS:
        return
    await m.answer(build_report(datetime.now(TZ).strftime("%Y-%m-%d")))


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

    for o in reversed(state["orders"]):
        if o["oid"] == oid:
            o["status"] = code
            save_state()
            break

    base = cb.message.html_text.split("\n\n📌")[0]
    await cb.message.edit_text(f"{base}\n\n📌 Holat: <b>{label}</b>", reply_markup=cb.message.reply_markup)
    try:
        await bot.send_message(int(uid), f"{text}\n\n<i>Buyurtma №{oid}</i>")
        await cb.answer("Mijozga xabar yuborildi")
    except Exception:
        await cb.answer("Mijozga xabar yuborib bo'lmadi (botni bloklagan bo'lishi mumkin)", show_alert=True)


@router.message(F.text)
async def fallback(m: Message):
    await m.answer("Katalogni ochish uchun /start ni bosing 👇", reply_markup=catalog_kb())


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
    now = datetime.now(TZ)
    oid = now.strftime("%d%H%M%S")
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

    add_order({
        "oid": oid, "date": now.strftime("%Y-%m-%d"), "ts": now.isoformat(timespec="seconds"),
        "uid": uid, "total": total, "pay": "card" if card else "cash", "status": "new",
        "items": [{"name": i["name"], "unit": i["unit"], "qty": i["qty"],
                   "sum": int(i["qty"] * i["price"])} for i in items],
    })

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
    load_state()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(dp.start_polling(bot), web_server(), report_scheduler())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())