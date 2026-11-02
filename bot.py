import asyncio
import json
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE"
ADMIN_ID = 8630108906
WEBAPP_URL = "https://exclusive-ascent-calzone.ngrok-free.dev"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌾 Tinchlik Yemxona Do'konini Ochish", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    welcome_text = (
        "Assalomu alaykum! 🌟\n"
        "**Tinchlik Yemxona** rasmiy buyurtma botiga xush kelibsiz.\n\n"
        "Eng sifatli yem-hasak mahsulotlarini qulay narxlarda to'g'ridan-to'g'ri xarid qiling. "
        "Buyurtma berish uchun quyidagi tugmani bosing va kerakli mahsulotlarni tanlang! 🚀"
    )
    await message.answer(welcome_text, reply_markup=kb, parse_mode="Markdown")

async def index(request):
    return web.FileResponse('index.html')

async def handle_order(request):
    try:
        data = await request.json()
        items = data.get('items', [])
        total = data.get('total', 0)
        user_id = data.get('user_id', 'Nomaʼlum')
        user_name = data.get('user_name', 'Mijoz')
        phone = data.get('phone', 'Kiritilmagan')

        # Iliq va professional biznes uslubidagi xabar formati
        order_text = (
            f"🔥 **YANGI BUYURTMA KELDI!**\n\n"
            f"👤 **Mijoz:** {user_name}\n"
            f"🆔 **Telegram ID:** `{user_id}`\n"
            f"📞 **Telefon raqam:** `{phone}`\n\n"
            f"📋 **Buyurtma tarkibi:**\n"
        )
        
        for idx, item in enumerate(items, 1):
            name = item.get('name', 'Mahsulot')
            qty = item.get('qty', 0)
            unit = item.get('unit', 'kg')
            price = item.get('price', 0)
            subtotal = qty * price
            order_text += f"{idx}. {name} — {qty} {unit} x {price:,} so'm = **{subtotal:,} so'm**\n"
        
        order_text += (
            f"\n----------------------------------\n"
            f"💰 **JAMI SUMMA: {total:,} so'm**\n"
            f"----------------------------------\n"
            f"✨ *Iltimos, mijoz bilan tezroq bog'lanib, buyurtmani tasdiqlang!*"
        )

        # Adminga xabar yuborish
        await bot.send_message(ADMIN_ID, order_text, parse_mode="Markdown")

        return web.json_response({"status": "success", "message": "Buyurtma muvaffaqiyatli qabul qilindi!"})
    except Exception as e:
        logging.error(f"Buyurtmani qabul qilishda xatolik: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=400)

async def web_server():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/api/order', handle_order)
    app.router.add_static('/', path='.', name='static')
    return app

async def main():
    logging.basicConfig(level=logging.INFO)
    app = await web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print("Aiohttp server http://localhost:8080 da ishga tushdi.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())