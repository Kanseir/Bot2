import telebot
import yt_dlp
import os

# 🔹 حط التوكن بتاع البوت هنا
TOKEN = "7663196465:AAHs-ARraYzRxv0U013t0TnOzSJFcbZNdN4"
bot = telebot.TeleBot(TOKEN)

# 🔹 تحميل الفيديو بجودة محددة مع استخدام الكوكيز
def download_video(url, quality):
    ydl_opts = {
        'cookies': 'cookies.txt',  # استخدام ملف الكوكيز
        'format': quality,  # اختيار الجودة المطلوبة
        'outtmpl': 'video.%(ext)s',  # اسم الملف المحمل
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# 🔹 لما المستخدم يبعت رابط يوتيوب
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أرسل رابط فيديو يوتيوب مع اختيار الجودة (مثلاً: 360p, 720p, 1080p)")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_video(message):
    chat_id = message.chat.id
    url = message.text
    
    # 🔹 عرض خيارات الجودة
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    btn_360p = telebot.types.KeyboardButton("360p")
    btn_720p = telebot.types.KeyboardButton("720p")
    btn_1080p = telebot.types.KeyboardButton("1080p")
    markup.add(btn_360p, btn_720p, btn_1080p)
    
    msg = bot.send_message(chat_id, "اختَر الجودة المطلوبة:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda q: process_quality(q, url))

def process_quality(message, url):
    chat_id = message.chat.id
    quality = message.text

    if quality not in ["360p", "720p", "1080p"]:
        bot.send_message(chat_id, "❌ جودة غير صحيحة، حاول مرة أخرى.")
        return

    bot.send_message(chat_id, "⏳ جاري تحميل الفيديو...")
    
    # 🔹 تحويل الجودة لصيغة `yt-dlp`
    format_map = {"360p": "best[height=360]", "720p": "best[height=720]", "1080p": "best[height=1080]"}
    selected_quality = format_map[quality]
    
    try:
        download_video(url, selected_quality)
        bot.send_video(chat_id, open("video.mp4", "rb"))
        os.remove("video.mp4")  # 🔹 حذف الفيديو بعد الإرسال
    except Exception as e:
        bot.send_message(chat_id, f"❌ حصل خطأ: {str(e)}")

# 🔹 تشغيل البوت
bot.polling()
