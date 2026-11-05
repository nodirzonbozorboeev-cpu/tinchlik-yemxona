import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

# Sizning haqiqiy tokeningiz va Web App havolangiz
TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE"
WEB_APP_URL = "https://tinchlik-yemxona.onrender.com"

router = Router()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# ----------------- ASOSIY MENYU (KEYBOARD) -----------------
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Tinchlik Yemxona Katalogi")],
            [KeyboardButton(text="🎁 VIP Xaridor shartlari"), KeyboardButton(text="💬 Fermerlar maslahatxonasi")],
            [KeyboardButton(text="📍 Do'kon manzili va Ish vaqti"), KeyboardButton(text="📞 Biz bilan aloqa")]
        ],
        resize_keyboard=True
    )

# ----------------- START BUYrug'I -----------------
@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        "🌾 <b>'Tinchlik Yemxona'</b> rasmiy botiga xush kelibsiz.\n"
        "Sifatli yem, silyos va kunjara mahsulotlarini eng qulay narxlarda xarid qiling!"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu())

# ----------------- 1. KATALOG (WEB-APP) -----------------
@router.message(F.text == "🛒 Tinchlik Yemxona Katalogi")
async def open_catalog(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Katalog ochish", web_app=WebAppInfo(url=WEB_APP_URL))]
        ]
    )
    await message.answer(
        "Katalogimizni ochish uchun pastdagi tugmani bosing va kerakli mahsulotlarni tanlang:",
        reply_markup=keyboard
    )

# ----------------- 2. VIP XARIDOR DASTURI -----------------
@router.message(F.text == "🎁 VIP Xaridor shartlari")
async def vip_conditions(message: Message):
    vip_text = (
        "⭐ <b>'Tinchlik Yemxona' VIP Xaridor Dasturi</b>\n\n"
        "Haftasiga <b>1,5 million so'mdan</b> ortiq tovar xarid qiling va avtomatik ravishda <b>VIP Xaridor</b> maqomini qo'lga kiriting!\n\n"
        "<b>VIP mijozlarga beriladigan imtiyozlar:</b>\n"
        "• 🏷️ Keyingi xaridlar uchun maxsus chegirmalar;\n"
        "• ⚡ Do'konda navbatsiz va birinchi navbatda yuklab berish;\n"
        "• 📢 Yangi kelgan sifatli silyos va yemlarni birinchi bo'lib band qilish imkoniyati;\n"
        "• 🚚 Yetkazib berishda maxsus qulayliklar va bonuslar.\n\n"
        "<i>Savollar bo'yicha operatorga murojaat qiling!</i>"
    )
    await message.answer(vip_text, parse_mode="HTML")

# ----------------- 3. FERMERLAR MASLAHATXONASI -----------------
@router.message(F.text == "💬 Fermerlar maslahatxonasi")
async def farmers_advice(message: Message):
    advice_text = (
        "💬 <b>Fermerlar va Chorvadorlar Maslahatxonasi</b>\n\n"
        "Mol parvarish qilish, yem tanlash, silyos saqlash yoki ozuqa ratsioni bo'yicha savollaringiz bormi?\n\n"
        "✍️ O'z savolingizni shu yerga yozib qoldiring, mutaxassisimiz tez fursatda sizga javob beradi va to'g'ri maslahat beradi!"
    )
    await message.answer(advice_text, parse_mode="HTML")

# ----------------- 4. DO'KON MANZILI VA ISH VAQTI -----------------
@router.message(F.text == "📍 Do'kon manzili va Ish vaqti")
async def shop_location(message: Message):
    address_text = (
        "📍 <b>'Tinchlik Yemxona' manzili va ma'lumotlari:</b>\n\n"
        "🏠 <b>Manzil:</b> Changtepa MFY\n"
        "⏰ <b>Ish vaqti:</b> Har kuni 08:00 dan 19:00 gacha (Dam olish kunisiz)\n"
        "📞 <b>Telefon raqam:</b> +998 (XX) XXX-XX-XX\n\n"
        "<i>Do'konimiz joylashgan aniq lokatsiya:</i>"
    )
    await message.answer(address_text, parse_mode="HTML")
    # Siz yuborgan lokatsiya koordinatalari
    await message.answer_location(latitude=41.1333, longitude=69.2667)

# ----------------- 5. BIZ BILAN ALOQA -----------------
@router.message(F.text == "📞 Biz bilan aloqa")
async def contact_us(message: Message):
    contact_text = (
        "📞 <b>Tezkor aloqa:</b>\n\n"
        "Operatorimizga to'g'ridan-to'g'ri bog'lanish uchun quyidagi profilga yozing:\n\n"
        "👤 Menedjer: @tinchlik_admin"
    )
    await message.answer(contact_text, parse_mode="HTML")

# ----------------- ASOSIY FUNKSIYA (MAIN) -----------------
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
