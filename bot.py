import json
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE"
bot = telebot.TeleBot(TOKEN)

PRODUCTS_FILE = "products.json"
ADMIN_ID = None 

# Har bir foydalanuvchining savatchasi va ma'lumotlarini saqlash
user_carts = {}
user_data = {}

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    push_to_github()

def push_to_github():
    try:
        os.system('git add products.json')
        os.system('git commit -m "Auto update products.json from Telegram Bot"')
        os.system('git push origin main')
        print("GitHub va Vercel muvaffaqiyatli yangilandi!")
    except Exception as e:
        print(f"GitHub'ga yuborishda xatolik: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global ADMIN_ID
    ADMIN_ID = message.from_user.id
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📦 Mahsulotlar va Xarid qilish"), KeyboardButton("🛒 Savatcham"), KeyboardButton("➕ Mahsulot qo'shish (Admin)"))
    
    bot.reply_to(message, f"Assalomu alaykum! Tinchlik Yemxona boshqaruv botiga xush kelibsiz.\n\nSizning ID raqamingiz saqlandi: `{ADMIN_ID}`", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📦 Mahsulotlar va Xarid qilish")
def show_shop_products(message):
    products = load_products()
    if not products:
        bot.reply_to(message, "Hozircha sotuvda mahsulotlar mavjud emas.")
        return
    
    markup = InlineKeyboardMarkup()
    for idx, p in enumerate(products):
        markup.add(InlineKeyboardButton(f"➕ {p.get('name')} - {p.get('price')} so'm", callback_data=f"add_{idx}"))
    
    bot.reply_to(message, "🛒 Kerakli mahsulotni tanlang (ustiga bossangiz savatchaga qo'shiladi):", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def handle_add_to_cart(call):
    idx = int(call.data.split('_')[1])
    products = load_products()
    user_id = call.from_user.id
    
    if idx < len(products):
        product = products[idx]
        
        if user_id not in user_carts:
            user_carts[user_id] = []
        
        user_carts[user_id].append(product)
        bot.answer_callback_query(call.id, f"✅ {product.get('name')} savatchaga qo'shildi!")
        
        # Savatchani ko'rish va buyurtma berish tugmalari
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛍 Xaridni davom ettirish", callback_data="continue_shopping"))
        markup.add(InlineKeyboardButton("🚀 Buyurtmani rasmiylashtirish", callback_data="checkout"))
        
        bot.send_message(call.message.chat.id, f"📦 Tanlangan mahsulot: *{product.get('name')}* ({product.get('price')} so'm)\n\nSavatchangizda mahsulotlar bor. Davom etasizmi?", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "continue_shopping")
def continue_shopping(call):
    bot.answer_callback_query(call.id)
    show_shop_products(call.message)

@bot.message_handler(func=lambda message: message.text == "🛒 Savatcham")
def show_cart(message):
    user_id = message.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        bot.reply_to(message, "🛒 Savatchangiz hozircha bo'sh.")
        return
    
    cart = user_carts[user_id]
    text = "🛒 **Sizning savatchangiz:**\n\n"
    total_price = 0
    
    for idx, p in enumerate(cart, 1):
        price = float(p.get('price', 0))
        total_price += price
        text += f"{idx}. {p.get('name')} — {p.get('price')} so'm\n"
    
    text += f"\n💰 **Jami summa:** {total_price} so'm"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Buyurtma berish", callback_data="checkout"))
    markup.add(InlineKeyboardButton("🗑 Savatchani tozalash", callback_data="clear_cart"))
    
    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
def clear_cart(call):
    user_id = call.from_user.id
    user_carts[user_id] = []
    bot.answer_callback_query(call.id, "Savatcha tozalandi!")
    bot.send_message(call.message.chat.id, "🛒 Savatchangiz tozalandi.")

@bot.callback_query_handler(func=lambda call: call.data == "checkout")
def checkout_start(call):
    user_id = call.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        bot.answer_callback_query(call.id, "Savatchangiz bo'sh!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Iltimos, bog'lanish uchun **telefon raqamingizni** yuboring (masalan: +998901234567):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_customer_phone)

def get_customer_phone(message):
    user_id = message.from_user.id
    phone = message.text
    
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["phone"] = phone
    
    msg = bot.reply_to(message, "Qabul qilindi! Endi aniq **manzilingizni** (orientir bilan) yozib yuboring:")
    bot.register_next_step_handler(msg, get_customer_address)

def get_customer_address(message):
    user_id = message.from_user.id
    address = message.text
    
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_data[user_id]["address"] = address
    cart = user_carts.get(user_id, [])
    data = user_data[user_id]
    customer_name = message.from_user.first_name or "Mijoz"
    
    # Buyurtma matnini shakllantirish
    order_details = ""
    total_price = 0
    for idx, p in enumerate(cart, 1):
        order_details += f"{idx}. {p.get('name')} — {p.get('price')} so'm\n"
        total_price += float(p.get('price', 0))
    
    order_details += f"\n💰 **Jami: {total_price} so'm**"
    
    # Mijozga xabar
    bot.reply_to(message, "✅ Buyurtmangiz qabul qilindi! Tez orada operatorlarimiz siz bilan bog'lanishadi.")
    
    # Adminga xabar yuborish
    if ADMIN_ID:
        admin_text = f"🚨 **YANGI BUYURTMA (Bir nechta mahsulot)!**\n\n" \
                     f"👤 Mijoz: {customer_name}\n" \
                     f"📞 Tel: {data.get('phone')}\n" \
                     f"📍 Manzil: {address}\n\n" \
                     f"🛒 **Buyurtmalar:**\n{order_details}"
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    
    # Savatchani tozalash
    user_carts[user_id] = []

@bot.message_handler(func=lambda message: message.text == "➕ Mahsulot qo'shish (Admin)")
def ask_product_name(message):
    msg = bot.reply_to(message, "Yangi mahsulot nomini kiriting (masalan: Bug'doy kepagi):")
    bot.register_next_step_handler(msg, process_product_name)

def process_product_name(message):
    name = message.text
    msg = bot.reply_to(message, f"Mahsulot nomi: *{name}*.\nEndi narxini kiriting (faqat raqamda, masalan: 2500):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_product_price, name)

def process_product_price(message, name):
    price = message.text
    products = load_products()
    
    products.append({"name": name, "price": price})
    save_products(products)
    
    bot.reply_to(message, f"✅ Muvaffaqiyatli qo'shildi!\n\n📦 Nomi: {name}\n💰 Narxi: {price} so'm\n\n*Saytga va botga avtomatik qo'shildi!*", parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot mukammal rejimda ishga tushdi...")
    bot.infinity_polling()