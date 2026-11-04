import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Token va Admin ID
TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE" 
ADMIN_ID = 8630108906

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

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

# Mijoz chek rasmini yuborganda ishlaydigan qism
@router.message(F.photo)
async def handle_photo(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 **Yangi to'lov cheki keldi!**\n👤 Mijoz: {message.from_user.full_name} (ID: `{message.from_user.id}`)\nUsername: @{message.from_user.username or 'yoq'}",
        parse_mode="Markdown"
    )
    await message.forward(chat_id=ADMIN_ID)
    await message.answer("✅ To'lov chekingiz adminga yuborildi! Tez orada tekshirib tasdiqlashadi.")

# Serverdan buyurtmani qabul qilish
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
        payment_type = data.get('payment_type', 'cash')

        items_text = "\n".join([f"• {item['name']} - {item['qty']} {item['unit']} ({item['price']:,} so'mdan)" for item in items])
        
        if payment_type == 'card':
            payment_text = (
                f"💳 **To'lov turi:** Karta orqali\n"
                f"📌 **Karta raqam:** `5614 6821 0937 9760` (Isayev Nodirjon)\n"
                f"💰 **To'lanishi kerak:** {total:,} so'm\n\n"
                f"⏳ *Iltimos, yuqoridagi kartaga to'lovni amalga oshiring va chek rasmini shu botga yuboring!*"
            )
        else:
            payment_text = "💵 **To'lov turi:** Naqd pul (Yetkazib berilganda / Yemxonada)"

        client_message = (
            f"✅ **Buyurtmangiz muvaffaqiyatli qabul qilindi!**\n\n"
            f"📦 **Sizning xaridlaringiz:**\n{items_text}\n\n"
            f"💰 **Jami summa:** {total:,} so'm\n"
            f"{payment_text}\n\n"
            f"📞 **Telefon raqamingiz:** {phone}\n\n"
            f"⏳ *Tez orada mutaxassisimiz yoki sotuvchi siz bilan bog'lanadi.* Xaridingiz uchun rahmat! 😊"
        )
        
        if user_id and user_id != 'unknown':
            try:
                await bot.send_message(chat_id=user_id, text=client_message, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Mijozga xabar yuborishda xatolik: {e}")

        admin_payment_label = "💳 Karta orqali (Chek kutilmoqda)" if payment_type == 'card' else "💵 Naqd pul"
        admin_message = (
            f"🔔 **YANGI BUYURTMA KELDI!** 🚀\n\n"
            f"👤 **Mijoz:** {user_name} (ID: `{user_id}`)\n"
            f"📞 **Telefon:** {phone}\n"
            f"💳 **To'lov turi:** {admin_payment_label}\n\n"
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
    app.router.add_post('/api/order', handle_order)
    app.router.add_static('/', path='.', name='static')
    
    runner = web.AppRunner(app)
    app_runner = await runner.setup()
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