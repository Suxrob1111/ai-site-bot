import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai

# Maxfiy kalitlar va tokenlar
TELEGRAM_TOKEN = "8798889526:AAEQ05WFNp-vGi5KwqLJRULZI8QuqzCc1g0"  # Bot tokeningiz

# Yangi formatdagi Gemini API kaliti (AQ... bilan boshlanadigani)
GEMINI_API_KEY = "AQ.Ab8RN6LP2eXmhEMes0uCNO47pyAsjhzETfCgCKKmS3LDOGdY-w"

# Gemini kalitini muhit o'zgaruvchisiga o'rnatamiz (yangi kutubxona shuni talab qiladi)
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
      "Agar xohlasangiz, o'z **telefon raqamingizni** va **do'kon nomingizni** ham"
      " qo'shib yozing "
      "(masalan: *'Telefon raqamim: +998901234567, do'kon nomi: MegaStore, va"
      " menga telefonlar do'koni uchun sayt yaratib ber'*).\n"
      "Men uni bir zumda tayyorlab, internetga chiqarib beraman!"
  )


# Foydalanuvchidan kelgan xabarlarga AI orqali javob berish
@dp.message()
async def handle_message(message: types.Message):
  user_text = message.text

  # Foydalanuvchiga jarayon boshlanganini bildiramiz
  waiting_msg = await message.answer(
      "⏳ Saytingiz uchun zamonaviy dizayn va kodlar tayyorlanmoqda, iltimos"
      " kuting..."
  )

  try:
    # Gemini AI'dan javob olish (gemini-3.6-flash yoki mos model)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=(
            f"Sen professional veb-dasturchisan. Foydalanuvchi quyidagi talabni yubordi: '{user_text}'. Unga to'liq va tayyor HTML va CSS kodlarini yozib ber. Kodlar chiroyli va ishlaydigan bo'lsin."
        ),
    )

    ai_reply = response.text
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=waiting_msg.message_id,
        text=ai_reply,
    )

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
