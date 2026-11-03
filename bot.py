import asyncio
import logging
import os
import json
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

# Mahsulotlarni faylda saqlash uchun fayl nomi
DATA_FILE = "products.json"

def load_products():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Faylni o'qishda xatolik: {e}")
            return []
    return []

def save_products(prods):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prods, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Faylga yozishda xatolik: {e}")

# Mahsulotlar bazasi fayldan yuklanadi
PRODUCTS = load_products()

# /start buyrug'i - iliq kutib olish va Mini App tugmasi
@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Tinchlik Yemxona Katalogi", 
                    web_app=WebAppInfo(url="https://tinchlik-yemxona.onrender.com")
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

async def handle_index(request):
    return web.FileResponse('index.html')

async def get_products(request):
    return web.json_response(PRODUCTS)

async def add_product_api(request):
    try:
        data = await request.json()
        new_prod = {
            "id": int(asyncio.get_event_loop().time() * 1000),
            "name": data.get('name'),
            "price": data.get('price'),
            "unit": data.get('unit')
        }
        PRODUCTS.append(new_prod)
        save_products(PRODUCTS)  # Faylga saqlash
        return web.json_response({"status": "success", "product": new_prod})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=400)

async def delete_product_api(request):
    try:
        data = await request.json()
        prod_id = data.get('id')
        global PRODUCTS
        PRODUCTS = [p for p in PRODUCTS if p['id'] != prod_id]
        save_products(PRODUCTS)  # Faylga saqlash
        return web.json_response({"status": "success"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=400)

async def handle_order(request):
    try:
        data = await request.json()
        user_id = data.get('user_id')
        user_name = data.get('user_name', 'Mijoz')
        phone = data.get('phone')
        items = data.get('items', [])
        total = data.get('total', 0)

        items_text = "\n".join([f"• {item['name']} - {item['qty']} {item['unit']} ({item['price']:,} so'mdan)" for item in items])
        
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
    app.router.add_get('/', handle_index)
    app.router.add_get('/api/products', get_products)
    app.router.add_post('/api/add-product', add_product_api)
    app.router.add_post('/api/delete-product', delete_product_api)
    app.router.add_post('/api/order', handle_order)
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