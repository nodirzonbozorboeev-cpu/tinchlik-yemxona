import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Sening ma'lumotlaring
TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE" 
ADMIN_ID = 8630108906

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# /start buyrug'i - iliq kutib olish va Mini App tugmasi
@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Tinchlik Yemxona Katalogi", 
                    web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com") # Render'dagi saytingiz havolasi
                )
            ]
        ]
    )
    await message.answer(
        f"Assalomu alaykum, hurmatli mijozimiz! 😊\n"
        f"🌾 **Tinchlik Yemxona** rasmiy buyurtma botiga xush kelibsiz.\n\n"
        f"Bugun mol-holingiz uchun qanday yem-hasak kerak? Pastdagi tugmani bosing va o'zingizga kerakli mahsulotlarni tanlang!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Aiohttp server qismi: Mini App sahifasini ochish va buyurtmalarni qabul qilish
async def handle_index(request):
    return web.FileResponse('index.html')

async def handle_order(request):
    try:
        data = await request.json()
        user_id = data.get('user_id')
        user_name = data.get('user_name', 'Mijoz')
        phone = data.get('phone')
        items = data.get('items', [])
        total = data.get('total', 0)

        # Mahsulotlar ro'yxatini shakllantirish
        items_text = "\n".join([f"• {item['name']} - {item['qty']} {item['unit']} ({item['price']:,} so'mdan)" for item in items])
        
        # Mijozga yuboriladigan iliq xabar
        client_message = (
            f"✅ **Buyurtmangiz muvaffaqiyatli qabul qilindi!**\n\n"
            f"📦 **Sizning xaridlaringiz:**\n{items_text}\n\n"
            f"💰 **Jami summa:** {total:,} so'm\n"
            f"📞 **Telefon raqamingiz:** {phone}\n\n"
            f"⏳ *Tez orada mutaxassisimiz yoki sotuvchi 5 daqiqa ichida siz bilan bog'lanadi.* Xaridingiz uchun rahmat! 😊"
        )
        
        if user_id and user_id != 'unknown':
            try:
                await bot.send_message(chat_id=user_id, text=client_message, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Mijozga xabar yuborishda xatolik: {e}")

        # Adminga yuboriladigan xabar
        admin_message = (
            f"🔔 **YANGI BUYURTMA KELDI!** 🚀\n\n"
            f"👤 **Mijoz:** {user_name} (ID: {user_id})\n"
            f"📞 **Telefon:** {phone}\n\n"
            f"📋 **Mahsulotlar:**\n{items_text}\n\n"
            f"💵 **Jami summa:** {total:,} so'm"
        )
        await bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")

        return web.json_response({"status": "success"})
    except Exception as e:
        logging.error(f"Buyurtmani qayta ishlashda xatolik: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=400)

async def web_server():
    app = web.Application()
    # Asosiy sahifani (index.html) to'g'ridan-to'g'ri ochish uchun route
    app.router.add_get('/', handle_index)
    # Buyurtma qabul qilish API
    app.router.add_post('/api/order', handle_order)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    dp.include_router(router)
    # Bot polling va veb-serverni birgalikda ishga tushirish
    await asyncio.gather(
        dp.start_polling(bot),
        web_server()
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())