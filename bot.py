import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "9284978024:AAF3iLGexV7k_dBayVuzmH1USzWDwxqRE"
ADMIN_ID = 8630108906

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# 1. Start komandasi - Katalog va Ratsion kalkulyatori
@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐂 Aqlli Ratsion Kalkulyatori (3 Mahal)", callback_data="open_calc")],
        [InlineKeyboardButton(text="🛒 Tinchlik Yemxona Katalogi", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))]
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
        [InlineKeyboardButton(text="🛒 Tinchlik Yemxona Katalogi", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))]
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

# Buqa 400-450 kg
@router.callback_query(F.data == "buqa_450")
async def res_buqa_450(callback: CallbackQuery):
    text = (
        "<b>🐂 400–450 kg Buqa Uchun Semirtirish Ratsioni (3 Mahal)</b>\n"
        "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalabki to'yintiruvchi ovqat):</b>\n"
        "• Silyos: <b>8 kg</b>\n"
        "• MasterFeed (Buqalar uchun): <b>2 kg</b>\n"
        "• Kepak (Motabar): <b>1.5 kg</b>\n"
        "• Arpa (maydalangan): <b>1 kg</b>\n"
        "• Mayda Tuz: <b>20 gramm</b>\n\n"
        
        "☀️ <b>2-mahal (Tushlik payti):</b>\n"
        "• Silyos: <b>5 kg</b>\n"
        "• Kunjara: <b>1 kg</b>\n"
        "• Kepak: <b>0.5 kg</b>\n\n"
        
        "🌙 <b>3-mahal (Kechki to'yintiruvchi ovqat):</b>\n"
        "• Silyos: <b>7 kg</b>\n"
        "• MasterFeed (Buqalar uchun): <b>1.5 kg</b>\n"
        "• Arpa (maydalangan): <b>1 kg</b>\n"
        "• Kunjara: <b>0.5 kg</b>\n\n"
        
        "🛒 <b>Kerakli yem-hasaklarni to'g'ridan-to'g'ri buyurtma bering:</b>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_buqa")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# Buqa 300-350 kg
@router.callback_query(F.data == "buqa_350")
async def res_buqa_350(callback: CallbackQuery):
    text = (
        "<b>🐂 300–350 kg Buqa Uchun Semirtirish Ratsioni (3 Mahal)</b>\n"
        "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalab):</b> Silyos 6kg | MasterFeed 1.5kg | Kepak 1kg | Arpa 0.8kg | Tuz 15g\n"
        "☀️ <b>2-mahal (Tushlik):</b> Silyos 4kg | Kunjara 0.7kg | Kepak 0.3kg\n"
        "🌙 <b>3-mahal (Kechqurun):</b> Silyos 5kg | MasterFeed 1kg | Arpa 0.7kg | Kunjara 0.3kg\n\n"
        "🛒 <b>Kerakli yem-hasaklarni buyurtma qiling:</b>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_buqa")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# Sigir 450-500 kg (Sut uchun)
@router.callback_query(F.data == "sigir_500")
async def res_sigir_500(callback: CallbackQuery):
    text = (
        "<b>🐄 450–500 kg Sigir Uchun Sut Oshirish Ratsioni (3 Mahal)</b>\n"
        "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalabki sog'imdan oldin):</b>\n"
        "• Silyos: <b>8 kg</b>\n"
        "• MasterFeed (Sigirlar uchun): <b>2.5 kg</b>\n"
        "• Kepak (Motabar): <b>1.5 kg</b>\n"
        "• Arpa: <b>1 kg</b>\n"
        "• Mayda Tuz: <b>20 gramm</b>\n\n"
        
        "☀️ <b>2-mahal (Tushlik payti):</b>\n"
        "• Silyos: <b>5 kg</b>\n"
        "• Kunjara: <b>0.5 kg</b>\n"
        "• Raps Shrot: <b>0.3 kg</b>\n\n"
        
        "🌙 <b>3-mahal (Kechqurun, sog'imdan keyin):</b>\n"
        "• Silyos: <b>7 kg</b>\n"
        "• MasterFeed (Sigirlar uchun): <b>2 kg</b>\n"
        "• Kepak: <b>1 kg</b>\n"
        "• Vitamin tuz: <b>10 gramm</b>\n\n"
        
        "🛒 <b>Kerakli yem-hasaklarni buyurtma qiling:</b>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_sigir")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# Sigir 350-400 kg
@router.callback_query(F.data == "sigir_400")
async def res_sigir_400(callback: CallbackQuery):
    text = (
        "<b>🐄 350–400 kg Sigir Uchun Sut Oshirish Ratsioni (3 Mahal)</b>\n"
        "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalab):</b> Silyos 7kg | MasterFeed 2kg | Kepak 1kg | Arpa 0.8kg | Tuz 15g\n"
        "☀️ <b>2-mahal (Tushlik):</b> Silyos 4kg | Kunjara 0.4kg\n"
        "🌙 <b>3-mahal (Kechqurun):</b> Silyos 6kg | MasterFeed 1.5kg | Kepak 0.8kg | Raps Shrot 0.3kg\n\n"
        "🛒 <b>Kerakli yem-hasaklarni buyurtma qiling:</b>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_sigir")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# Qo'y 60-70 kg
@router.callback_query(F.data == "qoy_70")
async def res_qoy_70(callback: CallbackQuery):
    text = (
        "<b>🐑 60–70 kg Qo'y / Sovliq Uchun Semirtirish Ratsioni (3 Mahal)</b>\n"
        "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalab):</b>\n"
        "• Silyos: <b>1.8 kg</b>\n"
        "• MasterFeed (Universal): <b>0.5 kg</b>\n"
        "• Kepak: <b>0.3 kg</b>\n"
        "• Tuz: <b>5 gramm</b>\n\n"
        
        "☀️ <b>2-mahal (Tushlik):</b>\n"
        "• Silyos: <b>1.2 kg</b>\n"
        "• Arpa (maydalangan): <b>0.3 kg</b>\n"
        "• Kunjara: <b>0.2 kg</b>\n\n"
        
        "🌙 <b>3-mahal (Kechqurun):</b>\n"
        "• Silyos: <b>1.5 kg</b>\n"
        "• MasterFeed (Universal): <b>0.4 kg</b>\n"
        "• Kepak: <b>0.3 kg</b>\n\n"
        
        "🛒 <b>Kerakli yem-hasaklarni buyurtma qiling:</b>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_qoy")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# Qo'y 40-50 kg
@router.callback_query(F.data == "qoy_50")
async def res_qoy_50(callback: CallbackQuery):
    text = (
        "<b>🐑 40–50 kg Qo'y / Sovliq Uchun Ratsion (3 Mahal)</b>\n"
        "<i>(MasterFeed va do'konimiz mahsulotlari asosida tuzildi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalab):</b> Silyos 1.3kg | MasterFeed 0.4kg | Kepak 0.2kg | Tuz 3g\n"
        "☀️ <b>2-mahal (Tushlik):</b> Silyos 0.8kg | Arpa 0.2kg | Kunjara 0.15kg\n"
        "🌙 <b>3-mahal (Kechqurun):</b> Silyos 1.1kg | MasterFeed 0.3kg | Kepak 0.2kg\n\n"
        "🛒 <b>Kerakli yem-hasaklarni buyurtma qiling:</b>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Katalogdan sotib olish", web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com"))],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="calc_qoy")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# Veb-server qismi
async def web_server():
    app = web.Application()
    app.router.add_static('/', path='.', name='static')
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    dp.include_router(router)
    await asyncio.gather(
        dp.start_polling(bot),
        web_server()
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())