from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

ration_router = Router()

# 1. Start komandasi - Majburiy obunasiz, to'g'ridan-to'g'ri ishlaydi
@ration_router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐂 Aqlli Ratsion Kalkulyatori", callback_data="open_calc")]
    ])
    await message.answer(
        "<b>Assalomu alaykum! \"Tinchlik Yemxona\" rasmiy botiga xush kelibsiz.</b>\n\n"
        "Moldingiz uchun 100% natija beradigan kunlik ratsionni hisoblash uchun quyidagi tugmani bosing:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# 2. Kalkulyator menyusini ochish
@ration_router.callback_query(F.data == "open_calc")
async def open_calculator(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐂 Buqani Semirtirish (Go'sht)", callback_data="type_buqa")],
        [InlineKeyboardButton(text="🐄 Sigirning Sutini Oshirish", callback_data="type_sigir")]
    ])
    await callback.message.edit_text(
        "<b>\"Tinchlik Yemxona\" Ratsion Kalkulyatori</b>\n\n"
        "Moldingiz yo'nalishini tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# 3. Vazn oralig'ini tanlash (Buqa uchun)
@ration_router.callback_query(F.data == "type_buqa")
async def buqa_weight(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="300 kg gacha", callback_data="buqa_300_2mahal")],
        [InlineKeyboardButton(text="350 - 400 kg", callback_data="buqa_400_2mahal")],
        [InlineKeyboardButton(text="450 kg dan yuqori", callback_data="buqa_500_2mahal")]
    ])
    await callback.message.edit_text("Buqangizning taxminiy vaznini tanlang:", reply_markup=keyboard)
    await callback.answer()

# 4. Vazn oralig'ini tanlash (Sigir uchun)
@ration_router.callback_query(F.data == "type_sigir")
async def sigir_weight(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="350 - 400 kg", callback_data="sigir_400_2mahal")],
        [InlineKeyboardButton(text="450 - 500 kg", callback_data="sigir_500_2mahal")]
    ])
    await callback.message.edit_text("Sigiringizning taxminiy vaznini tanlang:", reply_markup=keyboard)
    await callback.answer()

# --- 5. NATIJA: 350-400 kg li Buqa uchun 2 mahalga bo'lingan ratsion ---
@ration_router.callback_query(F.data == "buqa_400_2mahal")
async def result_buqa_400_2mahal(callback: CallbackQuery):
    text = (
        "<b>🐂 350–400 kg Buqa uchun (2 Mahal) Ratsion</b>\n"
        "<i>(MasterFeed va do'koningiz mahsulotlari asosida taqsimlandi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalabki to'yintiruvchi ovqat):</b>\n"
        "• Silyos: <b>8 kg</b>\n"
        "• MasterFeed (Buqalar uchun): <b>2 kg</b>\n"
        "• Kepak Motabar: <b>1.5 kg</b>\n"
        "• Arpa (maydalangan): <b>1 kg</b>\n"
        "• Mayda Tuz: <b>15-20 gramm</b>\n\n"
        
        "🌙 <b>2-mahal (Kechki to'yintiruvchi ovqat):</b>\n"
        "• Silyos: <b>7 kg</b>\n"
        "• MasterFeed (Buqalar uchun): <b>1.5 kg</b>\n"
        "• Kunjara: <b>1 kg</b>\n"
        "• Kepak Motabar: <b>1 kg</b>\n\n"
        
        "🛒 <b>Ushbu mahsulotlarni sotib olish uchun buyurtma bering:</b>\n"
        "👉 @tinchlik_yemxonaN1_bot"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Shu mahsulotlarni sotib olish", url="https://t.me/tinchlik_yemxonaN1_bot")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="open_calc")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# --- 6. NATIJA: 450-500 kg li Sigir uchun 2 mahalga bo'lingan ratsion ---
@ration_router.callback_query(F.data == "sigir_500_2mahal")
async def result_sigir_500_2mahal(callback: CallbackQuery):
    text = (
        "<b>🐄 450–500 kg Sigir uchun Sut Ko'paytirish Ratsioni (2 Mahal)</b>\n"
        "<i>(MasterFeed va do'koningiz mahsulotlari asosida taqsimlandi)</i>\n\n"
        
        "🌅 <b>1-mahal (Ertalabki sog'im oldidan):</b>\n"
        "• Silyos: <b>8 kg</b>\n"
        "• MasterFeed (Sigirlar uchun): <b>2.5 kg</b>\n"
        "• Kepak Motabar: <b>1.5 kg</b>\n"
        "• Arpa: <b>1 kg</b>\n"
        "• Mayda Tuz: <b>20 gramm</b>\n\n"
        
        "🌙 <b>2-mahal (Kechqurun, sog'imdan keyin):</b>\n"
        "• Silyos: <b>8 kg</b>\n"
        "• MasterFeed (Sigirlar uchun): <b>2 kg</b>\n"
        "• Kunjara: <b>1 kg</b>\n"
        "• Raps Shrot: <b>0.5 kg</b>\n"
        "• Vitamin tuz: <b>Berib boriladi</b>\n\n"
        
        "🛒 <b>Ushbu mahsulotlarni sotib olish uchun buyurtma bering:</b>\n"
        "👉 @tinchlik_yemxonaN1_bot"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Shu mahsulotlarni sotib olish", url="https://t.me/tinchlik_yemxonaN1_bot")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="open_calc")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()