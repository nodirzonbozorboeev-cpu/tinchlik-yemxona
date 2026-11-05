 import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "9284978024:AAF3iLGexV7k_dBayVuzmH1USzWDwxqRE"
ADMIN_ID = 8630108906

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

WEBAPP_URL = "https://tinchlik-yemxona.onrender.com"

# 1. Start komandasi
@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐂 Aqlli Ratsion Kalkulyatori (3 Mahal)", callback_data="open_calc")],
        [InlineKeyboardButton(text="🛒 Tinchlik Yemxona Katalogi", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        "<b>Assalomu alaykum, hurmatli mijozimiz! 😊</b>\n\n"
        "\"Tinchlik Yemxona\" rasmiy botiga xush kelibsiz.\n\n"
        "Moldingiz uchun 100% natija beradigan 3 mahal kundalik ratsionni hisoblash yoki mahsulotlarni tanlash uchun quyidagi tugmani bosing:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# 2. Asosiy menyu (Hayvon turini tanlash)
@router.callback_query(F.data == "open_calc")
async def open_calculator(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐂 Buqani Semirtirish (Go'sht)", callback_data="calc_buqa")],
        [InlineKeyboardButton(text="🐄 Sigirning Sutini Oshirish", callback_data="calc_sigir")],
        [InlineKeyboardButton(text="🐑 Qo'y va Sovliqlarni Boqish", callback_data="calc_qoy")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_start")]
    ])
    await callback.message.edit_text(
        "<b>🐂 \"Tinchlik Yemxona\" Ratsion Kalkulyatori</b>\n\n"
        "Qaysi turdagi jonivor uchun ratsion hisoblamoqchisiz?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐂 Aqlli Ratsion Kalkulyatori (3 Mahal)", callback_data="open_calc")],
        [InlineKeyboardButton(text="🛒 Tinchlik Yemxona Katalogi", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await callback.message.edit_text(
        "<b>Assalomu alaykum, hurmatli mijozimiz! 😊</b>\n\n"
        "\"Tinchlik Yemxona\" rasmiy botiga xush kelibsiz.\n\n"
        "Moldingiz uchun 100% natija beradigan 3 mahal kundalik ratsionni hisoblash uchun quyidagi tugmani bosing:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# --- 3. BUQA UCHUN VAZN TANLASH ---
@router.callback_query(F.data == "calc_buqa")
async def buqa_weights(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚖️ 300 - 350 kg", callback_data="buqa_350")],
        [InlineKeyboardButton(text="⚖️ 400 - 450 kg", callback_data="buqa_450")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="open_calc")]
    ])
    await callback.message.edit_text("<b>🐂 Buqaning vaznini tanlang:</b>", reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# --- 4. SIGIR UCHUN VAZN TANLASH ---
@router.callback_query(F.data == "calc_sigir")
async def sigir_weights(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚖️ 350 - 400 kg", callback_data="sigir_400")],
        [InlineKeyboardButton(text="⚖️ 450 - 500 kg", callback_data="sigir_500")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="open_calc")]
    ])
    await callback.message.edit_text("<b>🐄 Sigirning vaznini tanlang:</b>", reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# --- 5. QO'Y UCHUN VAZN TANLASH ---
@router.callback_query(F.data == "calc_qoy")
async def qoy_weights(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚖️ 40 - 50 kg", callback_data="qoy_50")],
        [InlineKeyboardButton(text="⚖️ 60 - 70 kg", callback_data="qoy_70")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="open_calc")]
    ])
    await callback.message.edit_text("<b>🐑 Qo'yning vaznini tanlang:</b>", reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# ==========================================
# NATIJALAR (3 MAHALGA BO'LINGAN RATSIONLAR)
# ==========================================

@router.callback_query(F.data == "buqa_450")
async def res_buqa_450(callback: CallbackQuery):
    text = (
        "<b>🐂 400–450 kg Buqa Uchun Semirtirish Ratsioni (3 Mahal)</b>\n"
        "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>\n\n"
        "🌅 <b>1-mahal (Ertalab):</b> Silyos 8kg | MasterFeed 2kg | Kepak 1.5kg | Arpa 1kg | Tuz 20g\n"
        "☀️ <b>2-mahal (Tushlik):</b> Silyos 5kg | Kunjara 1kg | Kepak 0.5kg\n"
        "🌙 <b>3-mahal (Kechqurun):</b> Silyos 7kg | MasterFeed 1.5kg | Arpa 1kg | Kunjara 0.5kg"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_buqa")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "buqa_350")
async def res_buqa_350(callback: CallbackQuery):
    text = (
        "<b>🐂 300–350 kg Buqa Uchun Semirtirish Ratsioni (3 Mahal)</b>\n\n"
        "🌅 <b>1-mahal:</b> Silyos 6kg | MasterFeed 1.5kg | Kepak 1kg | Arpa 0.8kg | Tuz 15g\n"
        "☀️ <b>2-mahal:</b> Silyos 4kg | Kunjara 0.7kg | Kepak 0.3kg\n"
        "🌙 <b>3-mahal:</b> Silyos 5kg | MasterFeed 1kg | Arpa 0.7kg | Kunjara 0.3kg"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_buqa")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "sigir_500")
async def res_sigir_500(callback: CallbackQuery):
    text = (
        "<b>🐄 450–500 kg Sigir Uchun Sut Oshirish Ratsioni (3 Mahal)</b>\n\n"
        "🌅 <b>1-mahal:</b> Silyos 8kg | MasterFeed 2.5kg | Kepak 1.5kg | Arpa 1kg | Tuz 20g\n"
        "☀️ <b>2-mahal:</b> Silyos 5kg | Kunjara 0.5kg | Raps Shrot 0.3kg\n"
        "🌙 <b>3-mahal:</b> Silyos 7kg | MasterFeed 2kg | Kepak 1kg | Vitamin tuz 10g"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_sigir")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "sigir_400")
async def res_sigir_400(callback: CallbackQuery):
    text = (
        "<b>🐄 350–400 kg Sigir Uchun Sut Oshirish Ratsioni (3 Mahal)</b>\n\n"
        "🌅 <b>1-mahal:</b> Silyos 7kg | MasterFeed 2kg | Kepak 1kg | Arpa 0.8kg | Tuz 15g\n"
        "☀️ <b>2-mahal:</b> Silyos 4kg | Kunjara 0.4kg\n"
        "🌙 <b>3-mahal:</b> Silyos 6kg | MasterFeed 1.5kg | Kepak 0.8kg | Raps Shrot 0.3kg"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_sigir")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "qoy_70")
async def res_qoy_70(callback: CallbackQuery):
    text = (
        "<b>🐑 60–70 kg Qo'y / Sovliq Uchun Ratsion (3 Mahal)</b>\n\n"
        "🌅 <b>1-mahal:</b> Silyos 1.8kg | MasterFeed 0.5kg | Kepak 0.3kg | Tuz 5g\n"
        "☀️ <b>2-mahal:</b> Silyos 1.2kg | Arpa 0.3kg | Kunjara 0.2kg\n"
        "🌙 <b>3-mahal:</b> Silyos 1.5kg | MasterFeed 0.4kg | Kepak 0.3kg"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_qoy")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "qoy_50")
async def res_qoy_50(callback: CallbackQuery):
    text = (
        "<b>🐑 40–50 kg Qo'y / Sovliq Uchun Ratsion (3 Mahal)</b>\n\n"
        "🌅 <b>1-mahal:</b> Silyos 1.3kg | MasterFeed 0.4kg | Kepak 0.2kg | Tuz 3g\n"
        "☀️ <b>2-mahal:</b> Silyos 0.8kg | Arpa 0.2kg | Kunjara 0.15kg\n"
        "🌙 <b>3-mahal:</b> Silyos 1.1kg | MasterFeed 0.3kg | Kepak 0.2kg"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_qoy")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# Ishga tushirish qismi
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
