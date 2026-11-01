import asyncio
import json
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

BOT_TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE"
ADMIN_IDS = [8630108906]
WEB_APP_URL = "https://tinchlik-yemxona-1.vercel.app"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class AdminStates(StatesGroup):
    waiting_for_new_price = State()
    selected_product_id = State()
    new_product_name = State()
    new_product_price = State()

def load_products():
    if not os.path.exists("products.json"):
        return []
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_products(products):
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Yem do'konini ochish", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="⚙️ Admin panel (Boshqaruv)", callback_data="admin_panel")]
        ])
        text = "Assalomu alaykum, xo'jayin! **Tinchlik yemxona** boshqaruv paneliga xush kelibsiz."
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Yem katalogini ochish", web_app=WebAppInfo(url=WEB_APP_URL))]
        ])
        text = "Assalomu alaykum! **Tinchlik yemxona** rasmiy botiga xush kelibsiz."
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_panel")
async def open_admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
    products = load_products()
    kb_buttons = [
        [InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="add_product")]
    ]
    for p in products:
        kb_buttons.append([
            InlineKeyboardButton(text=f"✏️ {p['name']} ({p['price']:,} so'm)", callback_data=f"edit_price_{p['id']}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_prod_{p['id']}")
        ])
    kb_buttons.append([InlineKeyboardButton(text="« Orqaga qaytish", callback_data="back_to_start")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await callback.message.edit_text("⚙️ **Admin Panel**\nMahsulotlarni boshqarish:", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("delete_prod_"))
async def delete_product(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    product_id = int(callback.data.split("_")[2])
    products = load_products()
    products = [p for p in products if p["id"] != product_id]
    save_products(products)
    await callback.answer("❌ Mahsulot o'chirildi!", show_alert=True)
    await open_admin_panel(callback)

# --- FAQAT NOMI VA NARXI BILAN MAHSULOT QO'SHISH ---
@dp.callback_query(F.data == "add_product")
async def start_add_product(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminStates.new_product_name)
    await callback.message.answer("📦 Yangi mahsulot nomini kiriting (masalan: <em>Bug'doy</em>):", parse_mode="HTML")
    await callback.answer()

@dp.message(AdminStates.new_product_name)
async def process_new_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.new_product_price)
    await message.answer("💰 Mahsulot narxini kiriting (faqat raqam, masalan: 45000):")

@dp.message(AdminStates.new_product_price)
async def process_new_product_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
    price = int(message.text)
    data = await state.get_data()
    
    products = load_products()
    new_id = max([p["id"] for p in products], default=0) + 1
    
    new_product = {
        "id": new_id,
        "name": data["name"],
        "price": price,
        "unit": "dona"
    }
    
    products.append(new_product)
    save_products(products)
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚙️ Admin panelga qaytish", callback_data="admin_panel")]])
    await message.answer(f"✅ Yangi mahsulot qo'shildi!\n\n<b>{new_product['name']}</b> — {new_product['price']:,} so'm", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.startswith("edit_price_"))
async def ask_new_price(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    await state.update_data(selected_product_id=product_id)
    await state.set_state(AdminStates.waiting_for_new_price)
    await callback.message.edit_text(f"📦 **{product['name']}**\nJoriy narxi: {product['price']:,} so'm\n\nYangi narxni kiriting:", parse_mode="Markdown")
    await callback.answer()

@dp.message(AdminStates.waiting_for_new_price)
async def save_new_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Faqat raqam kiriting:")
        return
    new_price = int(message.text)
    data = await state.get_data()
    product_id = data.get("selected_product_id")
    products = load_products()
    for p in products:
        if p["id"] == product_id:
            p["price"] = new_price
            break
    save_products(products)
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚙️ Admin panelga qaytish", callback_data="admin_panel")]])
    await message.answer(f"✅ Narx **{new_price:,} so'm** qilib yangilandi.", parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: types.CallbackQuery):
    await cmd_start(callback.message)
    await callback.answer()

# Buyurtma kelganda adminga xabar berish
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        items = data.get("items", [])
        total_price = data.get("totalPrice", 0)
        phone = data.get("phone", "Kiritilmadi")
        address = data.get("address", "Kiritilmadi")

        text = f"📦 **YANGI BUYURTMA!**\n👤 Mijoz: {message.from_user.full_name}\n📞 Tel: {phone}\n📍 Manzil: {address}\n\n"
        for item in items:
            text += f"• {item['name']}: {item['qty']} dona — {item['price']:,} so'm\n"
        text += f"\n💰 **Jami:** {total_price:,} so'm"

        await message.answer("✅ Buyurtmangiz muvaffaqiyatli qabul qilindi!")
        for admin_id in ADMIN_IDS:
            await bot.send_message(chat_id=admin_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print("Xatolik:", e)
        await message.answer("❌ Buyurtmani yuborishda xatolik yuz berdi.")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Tinchlik Yemxona boti ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())