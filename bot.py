import asyncio
import logging
import time
import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from google import genai

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# --- KONFIGURATSIYA ---
TELEGRAM_TOKEN = "8798889526:AAEQ05WFNp-vGi5KwqLJRULZI8QuqzCc1g0"  # Bot tokeningiz
GEMINI_API_KEY = "AQ.Ab8RN6KFOLu3OMFfCMl8gAM-nbhp_bNccNX8pTgDE6e7B0-Pvw"      # Gemini API kalitingiz
VERCEL_TOKEN = "vcp_82iTbPFMIdyvtVGv194yZAA1fyBVqSXjURsnqUFjHSeENbM6qH0BOZLJ"    # Vercel tokeningiz

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Gemini mijozini ishga tushirish
client = genai.Client(api_key=GEMINI_API_KEY)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Salom! Men AlchemiX AI veb-sayt yaratish botiman. 🚀\n\n"
        "Menga do'koningiz uchun qanday sayt kerakligini yozing. "
        "Agar xohlasangiz, o'z **telefon raqamingizni** va **do'kon nomingizni** ham qo'shib yozing "
        "(masalan: *'Telefon raqamim: +998901234567, do'kon nomi: MegaStore, va menga telefonlar do'koni kerak'*).\n\n"
        "Men uni bir zumda tayyorlab, internetga chiqarib beraman!"
    )

# Foydalanuvchi yuborgan g'oya bo'yicha sayt yaratish va avtomatik deploy qilish
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_website_request(message: types.Message):
    prompt = message.text
    status_msg = await message.answer("⏳ Saytingiz uchun zamonaviy dizayn va kodlar tayyorlanmoqda, iltimos kuting...")

    try:
        # 1. Gemini orqali HTML kodini generatsiya qilish (telefon raqam va nomlarni hisobga olgan holda)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"""
            You are an expert web developer. Create a complete, beautiful, and modern single-page website using HTML and CSS (Tailwind CSS via CDN is preferred) based on this request: "{prompt}".
            If the user provided a phone number, store name, or specific details in their prompt, make sure to include them visibly in the website (e.g., in the header, contact section, or phone button).
            Return ONLY valid HTML code. Do not include markdown formatting blocks like ```html ... ```, just pure HTML code starting with <!DOCTYPE html>.
            """
        )
        html_code = response.text.strip()
        
        # Markdown belgilarni tozalash
        if html_code.startswith("```html"):
            html_code = html_code[7:]
        if html_code.endswith("```"):
            html_code = html_code[:-3]
        html_code = html_code.strip()

        await status_msg.edit_text("🚀 Sayt tayyorlanmoqda va Vercel orqali internetga chiqarilmoqda...")

        # Unikal loyiha nomi
        project_name = f"store-{int(time.time())}"

        # 2. Vercel API orqali to'g'ridan-to'g'ri faylni deploy qilish
        vercel_headers = {
            "Authorization": f"Bearer {VERCEL_TOKEN}",
            "Content-Type": "application/json"
        }
        
        deployment_payload = {
            "name": project_name,
            "files": [
                {
                    "file": "index.html",
                    "data": html_code
                }
            ],
            "projectSettings": {
                "framework": None
            }
        }

        vercel_res = requests.post(
            "https://api.vercel.com/v13/deployments?skipAutoDetectionConfirmation=1",
            headers=vercel_headers,
            json=deployment_payload
        )

        if vercel_res.status_code in [200, 201]:
            data = vercel_res.json()
            url = data.get("url")
            site_url = f"https://{url}" if url else f"https://{project_name}.vercel.app"
            
            await status_msg.edit_text(
                f"✅ **Saytingiz muvaffaqiyatli tayyor bo'ldi!** 🎉\n\n"
                f"🔗 **Sayt havolasi:** {site_url}\n\n"
                f"📌 *Ushbu havolani saqlab qo'ying va xohlagan joyingizda ishlating.*\n\n"
                f"🙏 Botimizdan foydalanganingiz uchun rahmat!"
            )
        else:
            err_text = vercel_res.text
            await status_msg.edit_text(f"❌ Deploy qilishda xatolik yuz berdi: {err_text}")

    except Exception as e:
        logging.error(e)
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")

async def main():
    print("AlchemiX AI platformasi to'liq ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())