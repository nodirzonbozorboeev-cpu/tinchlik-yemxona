import asyncio
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

# --- SOZLAMALAR ---
TOKEN = "9284978024:AAF3iLGeXEv7k_dBayVuzmhW1USZwDwxqRE"
WEB_APP_URL = "https://tinchlik-yemxona.onrender.com"
PORT = 10000

router = Router()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# --- HTML KATALOG SAHIFASI ---
HTML_CATALOG = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tinchlik Yemxona Katalogi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding-bottom: 90px; }
        .navbar { background-color: #198754; color: white; }
        .card { border: none; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
        .product-price { color: #198754; font-weight: bold; font-size: 1.1rem; }
        .cart-bar { position: fixed; bottom: 0; left: 0; right: 0; background: white; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); padding: 15px; z-index: 1000; border-top-left-radius: 16px; border-top-right-radius: 16px; }
        .kg-input { width: 80px; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark px-3 py-3 shadow-sm">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <span class="navbar-brand mb-0 h1 fw-bold">🌾 Tinchlik Yemxona</span>
            <span class="badge bg-light text-success fs-6 px-3 py-2" id="cartCountBadge">Savatcha: 0 ta</span>
        </div>
    </nav>

    <div class="container mt-3">
        <h5 class="mb-3 text-secondary fw-semibold">Barcha mahsulotlar:</h5>
        <div class="row g-3" id="productList"></div>
    </div>

    <div class="cart-bar d-none" id="cartBar">
        <div class="container d-flex justify-content-between align-items-center">
            <div>
                <span class="text-muted d-block small">Jami summa:</span>
                <span class="fs-5 fw-bold text-dark" id="cartTotalText">0 so'm</span>
            </div>
            <button class="btn btn-success px-4 py-2 fw-bold rounded-pill shadow-sm" data-bs-toggle="modal" data-bs-target="#checkoutModal">
                🛒 Buyurtma berish
            </button>
        </div>
    </div>

    <div class="modal fade" id="checkoutModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 rounded-4 shadow">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title fw-bold">📋 Buyurtmani rasmiylashtirish</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div id="cartItemsSummary" class="mb-3 border-bottom pb-2 small text-muted"></div>
                    <div class="mb-3">
                        <label for="phoneInput" class="form-label fw-bold">Telefon raqamingiz:</label>
                        <input type="tel" class="form-control" id="phoneInput" placeholder="+998 90 123 45 67" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">To'lov turini tanlang:</label>
                        <div class="form-check p-3 border rounded-3 mb-2 bg-light">
                            <input class="form-check-input" type="radio" name="paymentType" id="payCash" value="cash" onclick="toggleReceiptBox()" checked>
                            <label class="form-check-label fw-semibold" for="payCash">💵 Naqd pul (Yemxonada / Yetkazilganda)</label>
                        </div>
                        <div class="form-check p-3 border rounded-3 bg-light">
                            <input class="form-check-input" type="radio" name="paymentType" id="payCard" value="card" onclick="toggleReceiptBox()">
                            <label class="form-check-label fw-semibold" for="payCard">💳 Karta orqali<br><span class="text-muted small">Karta: <code>5614 6821 0937 9760</code> (Isayev Nodirjon)</span></label>
                        </div>
                    </div>
                    <div class="mb-3 d-none" id="receiptBox">
                        <label for="receiptInput" class="form-label fw-bold text-danger">📸 To'lov chekini yuklash (Majburiy):</label>
                        <input type="file" class="form-control" id="receiptInput" accept="image/*">
                    </div>
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">Bekor qilish</button>
                    <button type="button" class="btn btn-success rounded-pill px-4 fw-bold" onclick="sendOrder()">Tasdiqlash va yuborish</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        const products = [
            { id: 1, name: "Kepak Motabar", unit: "qop (25kg)", price: 85000, type: "qop" },
            { id: 2, name: "Kepak Mayda", unit: "qop (25kg)", price: 85000, type: "qop" },
            { id: 3, name: "MasterFeed (Buqalar uchun)", unit: "qop (40kg)", price: 200000, type: "qop" },
            { id: 4, name: "MasterFeed (Qoylar uchun)", unit: "qop (40kg)", price: 200000, type: "qop" },
            { id: 5, name: "MasterFeed (Sigirlar uchun)", unit: "qop (40kg)", price: 225000, type: "qop" },
            { id: 6, name: "MasterFeed (Quyonlar uchun)", unit: "kg", price: 6000, type: "kg" },
            { id: 7, name: "MasterFeed (Bruler 1,2,3)", unit: "kg", price: 10000, type: "kg" },
            { id: 8, name: "ArganicFeed (Buqa va Sigirlar uchun)", unit: "qop (40kg)", price: 175000, type: "qop" },
            { id: 9, name: "Xusnidin Chorvador (Buqalar uchun)", unit: "qop (40kg)", price: 240000, type: "qop" },
            { id: 10, name: "Silyos", unit: "qop (20kg)", price: 18000, type: "qop" },
            { id: 11, name: "Kunjara", unit: "kg", price: 6500, type: "kg" },
            { id: 12, name: "Raps Shrot", unit: "kg", price: 6000, type: "kg" },
            { id: 13, name: "Mayda Tuz", unit: "pachka (1kg)", price: 2000, type: "kg" },
            { id: 14, name: "Vitamin tuz", unit: "dona", price: 12000, type: "kg" },
            { id: 15, name: "Makka Johori", unit: "kg", price: 4000, type: "kg" },
            { id: 16, name: "Arpa", unit: "kg", price: 4000, type: "kg" },
            { id: 17, name: "Bug'doy", unit: "kg", price: 4500, type: "kg" },
            { id: 18, name: "555 Omuxta yem (Qoylar uchun)", unit: "kg", price: 5000, type: "kg" },
            { id: 19, name: "555 Omuxta yem (Tovuqlar uchun)", unit: "kg", price: 5000, type: "kg" }
        ];

        let cart = {};

        function renderProducts() {
            const listEl = document.getElementById('productList');
            listEl.innerHTML = '';
            products.forEach(p => {
                let qty = cart[p.id] || 0;
                let controlHtml = p.type === 'qop' 
                    ? `<div class="d-flex align-items-center gap-2"><button class="btn btn-outline-success btn-sm px-2 py-1 rounded-circle fw-bold" onclick="updateQty(${p.id}, -1)">-</button><span class="fw-bold px-1" id="qty-${p.id}">${qty}</span><button class="btn btn-success btn-sm px-2 py-1 rounded-circle fw-bold" onclick="updateQty(${p.id}, 1)">+</button></div>`
                    : `<div class="d-flex align-items-center gap-1"><input type="number" min="0" class="form-control form-control-sm kg-input" id="qty-${p.id}" value="${qty}" oninput="setKgQty(${p.id}, this.value)" placeholder="0"><span class="small text-muted">${p.unit}</span></div>`;

                listEl.innerHTML += `<div class="col-12"><div class="card p-3"><div class="d-flex justify-content-between align-items-center"><div><h6 class="mb-1 fw-bold text-dark">${p.name}</h6><span class="text-muted small">O'lchovi: ${p.unit}</span><div class="product-price mt-1">${p.price.toLocaleString()} so'm</div></div><div>${controlHtml}</div></div></div></div>`;
            });
        }

        function updateQty(id, change) {
            if (!cart[id]) cart[id] = 0;
            cart[id] += change;
            if (cart[id] < 0) cart[id] = 0;
            if (cart[id] === 0) delete cart[id];
            let el = document.getElementById(`qty-${id}`);
            if (el) el.innerText = cart[id] || 0;
            updateCartBar();
        }

        function setKgQty(id, value) {
            let val = parseInt(value);
            if (isNaN(val) || val <= 0) delete cart[id];
            else cart[id] = val;
            updateCartBar();
        }

        function toggleReceiptBox() {
            let payCard = document.getElementById('payCard').checked;
            let receiptBox = document.getElementById('receiptBox');
            if (payCard) receiptBox.classList.remove('d-none');
            else receiptBox.classList.add('d-none');
        }

        function updateCartBar() {
            let totalCount = 0, totalPrice = 0, summaryHtml = '';
            for (let id in cart) {
                let p = products.find(prod => prod.id == id);
                let count = cart[id];
                totalCount += count;
                let sum = count * p.price;
                totalPrice += sum;
                summaryHtml += `<div class="d-flex justify-content-between"><span>${p.name} (${count} ${p.unit})</span> <strong>${sum.toLocaleString()} so'm</strong></div>`;
            }
            const cartBar = document.getElementById('cartBar');
            if (totalCount > 0) {
                cartBar.classList.remove('d-none');
                document.getElementById('cartCountBadge').innerText = `Savatcha: ${totalCount} ta`;
                document.getElementById('cartTotalText').innerText = `${totalPrice.toLocaleString()} so'm`;
                document.getElementById('cartItemsSummary').innerHTML = summaryHtml;
            } else {
                cartBar.classList.add('d-none');
                document.getElementById('cartCountBadge').innerText = `Savatcha: 0 ta`;
            }
        }

        function sendOrder() {
            let phone = document.getElementById('phoneInput').value.trim();
            if (!phone) { alert("Iltimos, telefon raqamingizni kiriting!"); return; }
            let paymentType = document.querySelector('input[name="paymentType"]:checked').value;
            let receiptInput = document.getElementById('receiptInput');
            if (paymentType === 'card' && receiptInput.files.length === 0) {
                alert("Iltimos, karta orqali to'lov chekining rasmini yuklang!"); return;
            }

            let cartItems = [];
            let totalAmount = 0;
            for (let id in cart) {
                let p = products.find(prod => prod.id == id);
                let qty = cart[id];
                cartItems.push({ name: p.name, qty: qty, unit: p.unit, price: p.price });
                totalAmount += qty * p.price;
            }

            fetch('/api/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: tg.initDataUnsafe?.user?.id || 'unknown',
                    user_name: tg.initDataUnsafe?.user?.first_name || 'Mijoz',
                    phone: phone, items: cartItems, total: totalAmount, payment_type: paymentType
                })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    alert("Buyurtmangiz muvaffaqiyatli yuborildi!");
                    tg.close();
                } else { alert("Xatolik yuz berdi."); }
            });
        }

        renderProducts();
    </script>
</body>
</html>"""

# --- WEB SERVER (Aiohttp) ---
async def handle_index(request):
    return web.Response(text=HTML_CATALOG, content_type='text/html')

async def handle_order(request):
    try:
        data = await request.json()
        print("Yangi buyurtma keldi:", data)
        return web.json_response({"status": "success"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_post('/api/order', handle_order)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Veb-server {PORT}-portda ishga tushdi...")

# --- TELEGRAM BOT BUYRUQLARI ---
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Tinchlik Yemxona Katalogi")],
            [KeyboardButton(text="🎁 VIP Xaridor shartlari"), KeyboardButton(text="💬 Fermerlar maslahatxonasi")],
            [KeyboardButton(text="📍 Do'kon manzili va Ish vaqti"), KeyboardButton(text="📞 Biz bilan aloqa")]
        ],
        resize_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        "🌾 <b>'Tinchlik Yemxona'</b> rasmiy botiga xush kelibsiz.",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "🛒 Tinchlik Yemxona Katalogi")
async def open_catalog(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Katalog ochish", web_app=WebAppInfo(url=WEB_APP_URL))]
        ]
    )
    await message.answer("Katalogimizni ochish uchun pastdagi tugmani bosing:", reply_markup=keyboard)

@router.message(F.text == "🎁 VIP Xaridor shartlari")
async def vip_conditions(message: Message):
    await message.answer(
        "⭐ <b>'Tinchlik Yemxona' VIP Xaridor Dasturi</b>\n\n"
        "Haftasiga <b>1,5 million so'mdan</b> ortiq tovar xarid qiling va VIP maqomini qo'lga kiriting!",
        parse_mode="HTML"
    )

@router.message(F.text == "💬 Fermerlar maslahatxonasi")
async def farmers_advice(message: Message):
    await message.answer(
        "💬 <b>Fermerlar maslahatxonasi</b>\n\n"
        "Yem tanlash yoki parvarish qilish bo'yicha savollaringizni shu yerga yozib qoldiring!",
        parse_mode="HTML"
    )

@router.message(F.text == "📍 Do'kon manzili va Ish vaqti")
async def shop_location(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗺️ Xaritadan ochish (Google Maps)", url="https://maps.app.goo.gl/7cBuzGdWhxWbTpiN8")]
        ]
    )
    await message.answer(
        "📍 <b>Manzil:</b> Changtepa MFY\n⏰ <b>Ish vaqti:</b> 08:00 – 23:30\n📞 <b>Tel:</b> +998 99 892 01 39",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.message(F.text == "📞 Biz bilan aloqa")
async def contact_us(message: Message):
    await message.answer(
        "📞 <b>Aloqa:</b>\n📱 Tel: +998 99 892 01 39\n👤 Menedjer: @gofurov_df",
        parse_mode="HTML"
    )

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    # Veb-server va botni bir vaqtning o'zida (parallel) ishga tushiramiz
    await web_server()
    print("Bot polling boshlandi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
