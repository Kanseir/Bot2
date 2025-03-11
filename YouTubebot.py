import telebot
import yt_dlp
import os
import threading

# حط التوكن بتاع البوت هنا
TOKEN = "7663196465:AAFOASXX9l5WiknczOGnZt5ioeUmbXLidBI"
bot = telebot.TeleBot(TOKEN)

# قائمة الجودات المدعومة
QUALITIES = {
    "144p": "worst",
    "240p": "best[height<=240]",
    "360p": "best[height<=360]",
    "480p": "best[height<=480]",
    "720p": "best[height<=720]",
    "1080p": "best[height<=1080]"
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أرسل رابط يوتيوب، وبعدها اختار الجودة:\n" +
                 "\n".join([f"🎥 {q}" for q in QUALITIES.keys()]))

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def ask_quality(message):
    url = message.text
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for quality in QUALITIES.keys():
        markup.add(quality)
    bot.send_message(message.chat.id, "اختار الجودة:", reply_markup=markup)
    bot.register_next_step_handler(message, download_video, url)

def download_video(message, url):
    quality = message.text
    if quality not in QUALITIES:
        bot.reply_to(message, "❌ جودة غير صحيحة، حاول مرة أخرى.")
        return

    bot.reply_to(message, f"🔄 جاري تحميل الفيديو بجودة {quality}...")

    ydl_opts = {
        'format': QUALITIES[quality],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'n_threads': 4,  # زيادة عدد الـ Threads لسرعة التحميل
        'progress_hooks': [lambda d: bot.send_message(message.chat.id, "⬇ التحميل شغال...") if d['status'] == 'downloading' else None]
    }

    def process():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_name = ydl.prepare_filename(info)

            # إرسال الفيديو
            with open(file_name, "rb") as video:
                bot.send_video(message.chat.id, video, caption=f"✅ تم التحميل بجودة {quality}")

        except Exception as e:
            bot.reply_to(message, f"❌ حصل خطأ: {e}")

    threading.Thread(target=process).start()  # تشغيل التحميل في Thread مستقل

bot.polling(none_stop=True)