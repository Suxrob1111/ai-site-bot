import os
import tempfile
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from google import genai

# Maxfiy kalitlar va tokenlar
TELEGRAM_TOKEN = "8798889526:AAEQ05WFNp-vGi5KwqLJRULZI8QuqzCc1g0"  # Bot tokeningiz

# Yangi formatdagi Gemini API kaliti
GEMINI_API_KEY = "AQ.Ab8RN6JhMaWcyAjlDsG3X-QGbxfWv85HLsBqdJYDs_OAqoaZfQ"

# Gemini kalitini muhit o'zgaruvchisiga o'rnatamiz
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Bot va Dispatcher yaratish
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Gemini mijozini ishga tushirish
client = genai.Client()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Salom! Men AlchemiX AI veb-sayt yaratish botiman. 🚀\n\n"
        "Menga do'koningiz uchun qanday sayt kerakligini yozing. "
        "Telefon raqamingiz va do'kon nomingizni qo'shib yozsangiz, sayt ichiga yozib beraman "
        "(masalan: *'Telefon raqamim: +998901234567, do'kon nomi: MegaStore, va "
        "menga kiyimlar do'koni uchun sayt yaratib ber'*).\n"
        "Men sizga to'liq tayyor veb-sayt faylini yasab beraman!"
    )


# Foydalanuvchidan kelgan xabarlarga AI orqali javob berish
@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text

    # Foydalanuvchiga jarayon boshlanganini bildiramiz
    waiting_msg = await message.answer(
        "⏳ Saytingiz uchun zamonaviy dizayn va kodlar tayyorlanmoqda, iltimos kuting..."
    )

    try:
        # Gemini AI'dan to'liq HTML va CSS kodini so'raymiz
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                f"Sen professional veb-dasturchisan. Foydalanuvchi quyidagi talabni yubordi: '{user_text}'. "
                f"Unga faqat va faqat to'liq, ishlaydigan bitta fayldagi HTML kodini (CSS va JS bilan birga <style> va <script> teglari ichida) yozib ber. "
                f"Hech qanday ortiqcha tushuntirish yoki matn yozma, faqat sof HTML kodini ```html ... ``` bloki ichida qaytar."
            ),
        )

        ai_reply = response.text

        # AI javobidan faqat HTML kodini ajratib olamiz
        html_code = ai_reply
        if "```html" in ai_reply:
            parts = ai_reply.split("```html")
            if len(parts) > 1:
                html_code = parts[1].split("```")[0].strip()
        elif "```" in ai_reply:
            parts = ai_reply.split("```")
            if len(parts) > 1:
                html_code = parts[1].strip()

        # Vaqtinchalik fayl yaratib, unga kodni yozamiz
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html_code)
            file_path = f.name

        # Foydalanuvchiga fayl ko'rinishida yuboramiz
        document = FSInputFile(file_path, filename="index.html")
        await message.answer_document(
            document=document,
            caption="🎉 Mana sizning talabingiz asosida tayyorlangan veb-sayt fayli! Uni yuklab olib, istalgan brauzerda ochib ko'rishingiz mumkin."
        )

        # Kutish xabarini o'chiramiz
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)

        # Vaqtinchalik faylni o'chirib tashlaymiz
        os.unlink(file_path)

    except Exception as e:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=waiting_msg.message_id,
            text=f"❌ Xatolik yuz berdi: {e}",
        )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
