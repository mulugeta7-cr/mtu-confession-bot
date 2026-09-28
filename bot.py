import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Logging ማስተካከያ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8866534606:AAHl8CbSOzeSZ4SJAAkjZ8isahFBZIRjaWc"
# ትክክለኛው የቻናል Username (@ ምልክት ጨምረህ)
CHANNEL_ID = "@mtugcconfsionchanale"  
# -------------------------------------------------

# የፖስት ቁጥር መቆጠሪያ (Counter)
post_counter = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎓 **እንኳን ወደ MTU GC Senior Confession Bot በሰላም መጣችሁ!**\n\n"
        "4 ዓመት ሙሉ ሳትናገሩት በልባችሁ የያዛችሁትን አድናቆት, Rost,ፍቅር ወይም የስንብት መልእክት ይላኩ።\n\n"
        "🔒 **ማንነታችሁ 100% የተጠበቀ ነው (Anonymous)።** መልእክትዎ ወዲያውኑ ቻናል ላይ ይለቀቃል!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global post_counter
    
    user_text = update.message.text
    if not user_text:
        await update.message.reply_text("እባክዎን የጽሁፍ መልእክት ብቻ ይላኩ።")
        return

    # ቻናል ላይ የሚለቀቀው የጽሁፍ ፎርማት
    formatted_post = (
        f"📝 **#GC_Crush_{post_counter:03d}**\n\n"
        f"\"{user_text}\"\n\n"
        f"🎓 **Target:** GC Batch 2026\n"
        f"🏷️ **Category:** ❤️ Unspoken Love\n\n"
        f"📩 እርስዎስ አድናቆትዎን አልላኩም? 👉 @MTUGCConfusion_bot"
    )

    try:
        # ወደ ቻናሉ መልእክት መላክ
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_post,
            parse_mode="Markdown"
        )
        
        # የፖስቱን ቁጥር በ 1 መጨመር
        post_counter += 1
        
        # ለተማሪው ማረጋገጫ መስጠት
        await update.message.reply_text("✅ መልእክትዎ በተሳካ ሁኔታ ቻናል ላይ ተለቋል!")
        
    except Exception as e:
        await update.message.reply_text("❌ መልእክቱን መላክ አልተቻለም። እባክዎ ቆይተው እንደገና ይሞክሩ።")
        print(f"Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running...")
    app.run_polling()
