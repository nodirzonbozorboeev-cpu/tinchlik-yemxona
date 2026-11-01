import json
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE"
bot = telebot.TeleBot(TOKEN)

PRODUCTS_FILE = "products.json"
ADMIN_ID = 8630108906  

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
        os.system('git commit -m "Update products.json from bot"')
        os.system('git push origin main')
        print("GitHub muvaffaqiyatli yangilandi!")
    except Exception as e:
        print(f"GitHub'ga yuborishda xatolik: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📦 Mahsulotlar va Xarid qilish"), KeyboardButton("🛒 Savatcham"), KeyboardButton("➕ Mahsulot qo'shish (Admin)"))
    bot.reply_to(message, "Assalomu alaykum! Tinchlik Yemxona boshqaruv botiga xush kelibsiz.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📦 Mahsulotlar va Xarid qilish")
def show_shop_products(message):
    products = load_products()
    if not products:
        bot.reply_to(message, "Hozircha sotuvda mahsulotlar mavjud emas. Admin mahsulot qo'shishi kerak.")
        return
    
    markup = InlineKeyboardMarkup()
    for idx, p in enumerate(products):
        u_type = p.get('unit', 'kg')
        unit_label = "kg" if u_type == 'kg' else "qop"
        markup.add(InlineKeyboardButton(f"🌾 {p.get('name')} - {p.get('price')} so'm ({unit_label})", callback_data=f"prod_{idx}"))
    
    bot.reply_to(message, "🛒 Kerakli mahsulotni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('prod_'))
def handle_product_select(call):
    idx = int(call.data.split('_')[1])
    products = load_products()
    
    if idx < len(products):
        product = products[idx]
        unit = product.get('unit', 'kg')
        price = product.get('price')
        name = product.get('name')
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        if unit == 'kg':
            markup.add(
                InlineKeyboardButton("10 kg", callback_data=f"qty_{idx}_10"),
                InlineKeyboardButton("25 kg", callback_data=f"qty_{idx}_25"),
                InlineKeyboardButton("50 kg", callback_data=f"qty_{idx}_50"),
                InlineKeyboardButton("100 kg", callback_data=f"qty_{idx}_100"),
                InlineKeyboardButton("500 kg", callback_data=f"qty_{idx}_500"),
                InlineKeyboardButton("1000 kg (1 tonna)", callback_data=f"qty_{idx}_1000")
            )
            unit_text = "1 kg uchun narx"
        else:
            markup.add(
                InlineKeyboardButton("1 qop", callback_data=f"qty_{idx}_1"),
                InlineKeyboardButton("2 qop", callback_data=f"qty_{idx}_2"),
                InlineKeyboardButton("3 qop", callback_data=f"qty_{idx}_3"),
                InlineKeyboardButton("5 qop", callback_data=f"qty_{idx}_5"),
                InlineKeyboardButton("10 qop", callback_data=f"qty_{idx}_10"),
                InlineKeyboardButton("20 qop", callback_data=f"qty_{idx}_20")
            )
            unit_text = "1 qop uchun narx"
            
        markup.add(InlineKeyboardButton("⬅️ Ortga qaytish", callback_data="back_to_products"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📦 Mahsulot: *{name}*\n💰 {unit_text}: {price} so'm\n\nKerakli **miqdorni** tanlang:",
            parse_mode="Markdown",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('qty_'))
def handle_quantity_select(call):
    parts = call.data.split('_')
    idx = int(parts[1])
    amount = float(parts[2])
    
    products = load_products()
    user_id = call.from_user.id
    
    if idx < len(products):
        product = products[idx]
        price_per_unit = float(product.get('price', 0))
        total_item_price = price_per_unit * amount
        unit = product.get('unit', 'kg')
        unit_label = "kg" if unit == 'kg' else "qop"
        
        cart_item = {
            "name": product.get('name'),
            "price_per_unit": price_per_unit,
            "amount": amount,
            "unit": unit_label,
            "total_price": total_item_price
        }
        
        if user_id not in user_carts:
            user_carts[user_id] = []
        user_carts[user_id].append(cart_item)
        
        bot.answer_callback_query(call.id, f"✅ {amount} {unit_label} {product.get('name')} savatchaga qo'shildi!")
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛍 Xaridni davom ettirish", callback_data="back_to_products"))
        markup.add(InlineKeyboardButton("🚀 Buyurtmani rasmiylashtirish", callback_data="checkout"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ Savatchaga qo'shildi:\n\n"
                 f"🔹 *{product.get('name')}* — {amount} {unit_label}\n"
                 f"💰 Summa: {total_item_price} so'm\n\n"
                 f"Davom etasizmi?",
            parse_mode="Markdown",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_products")
def back_to_products(call):
    bot.answer_callback_query(call.id)
    products = load_products()
    if not products:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Hozircha sotuvda mahsulotlar mavjud emas.")
        return
    
    markup = InlineKeyboardMarkup()
    for idx, p in enumerate(products):
        u_type = p.get('unit', 'kg')
        unit_label = "kg" if u_type == 'kg' else "qop"
        markup.add(InlineKeyboardButton(f"🌾 {p.get('name')} - {p.get('price')} so'm ({unit_label})", callback_data=f"prod_{idx}"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🛒 Kerakli mahsulotni tanlang:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🛒 Savatcham")
def show_cart(message):
    user_id = message.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        bot.reply_to(message, "🛒 Savatchangiz hozircha bo'sh.")
        return
    
    cart = user_carts[user_id]
    text = "🛒 **Sizning savatchangiz:**\n\n"
    total_sum = 0
    
    for idx, item in enumerate(cart, 1):
        text += f"{idx}. {item['name']} — {item['amount']} {item['unit']} x {item['price_per_unit']} so'm = *{item['total_price']} so'm*\n"
        total_sum += item['total_price']
    
    text += f"\n💰 **Umumiy to'lov:** {total_sum} so'm"
    
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
    
    order_details = ""
    total_sum = 0
    for idx, item in enumerate(cart, 1):
        order_details += f"{idx}. {item['name']} — {item['amount']} {item['unit']} ({item['total_price']} so'm)\n"
        total_sum += item['total_price']
    
    order_details += f"\n💰 **Jami summa: {total_sum} so'm**"
    
    bot.reply_to(message, "✅ Buyurtmangiz qabul qilindi! Tez orada operatorlarimiz siz bilan bog'lanishadi.")
    
    if ADMIN_ID:
        admin_text = f"🚨 **YANGI BUYURTMA!**\n\n" \
                     f"👤 Mijoz: {customer_name}\n" \
                     f"📞 Tel: {data.get('phone')}\n" \
                     f"📍 Manzil: {address}\n\n" \
                     f"🛒 **Buyurtma qilingan mahsulotlar:**\n{order_details}"
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    
    user_carts[user_id] = []

# --- ADMIN QISMI ---
@bot.message_handler(func=lambda message: message.text == "➕ Mahsulot qo'shish (Admin)")
def ask_product_name(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Kechirasiz, bu buyruq faqat admin uchun.")
        return
        
    msg = bot.reply_to(message, "Yangi mahsulot nomini kiriting (masalan: Arpa yoki Tayyor yem):")
    bot.register_next_step_handler(msg, process_product_name)

def process_product_name(message):
    name = message.text
    msg = bot.reply_to(message, f"Mahsulot nomi: *{name}*.\nBu mahsulot **kiloga (kg)** sotiladimi yoki **qopga**?\n\nFaqatgina **kg** yoki **qop** deb yuboring:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_product_unit, name)

def process_product_unit(message, name):
    unit_input = message.text.strip().lower()
    if "qop" in unit_input:
        unit = "bag"
    else:
        unit = "kg"
        
    unit_name = "Qop" if unit == "bag" else "Kilogramm (kg)"
    msg = bot.reply_to(message, f"O'lchov birligi: *{unit_name}*.\nEndi 1 {('qop' if unit=='bag' else 'kg')} uchun **narxini** kiriting (faqat raqamda, masalan: 85000):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_product_price, name, unit)

def process_product_price(message, name, unit):
    price = message.text
    products = load_products()
    
    products.append({"name": name, "price": price, "unit": unit})
    save_products(products)
    
    unit_label = "kg" if unit == "kg" else "qop"
    bot.reply_to(message, f"✅ Muvaffaqiyatli qo'shildi!\n\n📦 Nomi: {name}\n💰 Narxi: {price} so'm ({unit_label})\n\n*Botga avtomatik qo'shildi!*", parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot mukammal rejimda ishga tushdi...")
    bot.infinity_polling()