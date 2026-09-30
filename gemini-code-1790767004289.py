import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes
)
import database as db

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 7205109695  # ያንተ Admin ID
CHANNEL_ID = "@your_channel_username"  # የቻናሉ ሊንክ/username

# States for ConversationHandler
SET_NAME, SET_CITY, SET_BIO, SEND_CONFESSION = range(4)

# Initial DB setup
db.init_db()

# Main Menu Keyboard
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 My Profile", callback_data="my_profile")],
        [InlineKeyboardButton("📝 Confess / ሐሳብ ላክ", callback_data="confess")],
        [InlineKeyboardButton("⭐️ My Aura", callback_data="my_aura")],
        [InlineKeyboardButton("📜 Rules", callback_data="rules"), InlineKeyboardButton("🔒 Privacy", callback_data="privacy")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.add_user(user_id)
    
    welcome_text = (
        "👋 **እንኳን ወደ ነፃ የሐሳብ መግለጫ ፕላትፎርም በደህና መጡ!**\n\n"
        "• ሐሳብዎን በነፃነት ያካፍሉ፤ ማንነትዎ ለሌሎችም ሆነ ለAdmin አያውቅም።\n"
        "• ተቀባይነት ያገኙ ሐሳቦች ወደ ቻናላችን ይለቀቃሉ።\n\n"
        "ለመጀመር ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

# Handle inline menu buttons
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "main_menu":
        await start(update, context)

    elif data == "my_profile":
        name, sex, city, bio, aura = db.get_user(user_id)
        profile_text = (
            f"👤 **My Profile**\n\n"
            f"**Name:** {name}\n"
            f"**Sex:** {sex}\n"
            f"**City:** {city}\n"
            f"**Bio:** {bio}\n"
            f"⭐ **Aura:** {aura}"
        )
        profile_keyboard = [
            [InlineKeyboardButton("✏️ Change Name", callback_data="change_name")],
            [InlineKeyboardButton("👨 Male", callback_data="set_male"), InlineKeyboardButton("👩 Female", callback_data="set_female")],
            [InlineKeyboardButton("🏢 Change City", callback_data="change_city")],
            [InlineKeyboardButton("📝 Change Bio", callback_data="change_bio")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]
        await query.edit_message_text(profile_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(profile_keyboard))

    elif data in ["set_male", "set_female"]:
        sex = "Male" if data == "set_male" else "Female"
        db.update_user_field(user_id, "sex", sex)
        await query.answer("ጾታ ተስተካክሏል!")
        # Refresh profile
        await button_click(update, context)

    elif data == "my_aura":
        _, _, _, _, aura = db.get_user(user_id)
        aura_text = (
            f"⭐ **የእርስዎ Aura ነጥብ: {aura}**\n\n"
            "💡 **Aura እንዴት ያድጋል?**\n"
            "• ሐሳብ/Confession ሲልኩ +5 Aura ያገኛሉ!\n"
            "• መልዕክትዎ ቻናል ላይ ሲወጣ +10 Aura ይጨመራል!"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
        await query.edit_message_text(aura_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "rules":
        rules_text = (
            "📜 **የአጠቃቀም ህጎች፦**\n\n"
            "1. የስም ማጠልሸት እና የግል ጥቃቶች የተከለከሉ ናቸው።\n"
            "2. የጥላቻ ንግግር እና አላስፈላጊ ማስታወቂያ መላክ አይቻልም።\n"
            "3. ህግ የጣሱ ተጠቃሚዎች ከቦቱ ይታገዳሉ።"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
        await query.edit_message_text(rules_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Profile inputs handling
async def prompt_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✏️ እባክዎን አዲሱን **የብዕር ስምዎን** ይጻፉ፦", parse_mode="Markdown")
    return SET_NAME

async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db.update_user_field(user_id, "name", update.message.text)
    await update.message.reply_text("✅ ስምዎ ተስተካክሏል!", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def prompt_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🏢 እባክዎን **ከተማዎን/አካባቢዎን** ይጻፉ፦", parse_mode="Markdown")
    return SET_CITY

async def save_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db.update_user_field(user_id, "city", update.message.text)
    await update.message.reply_text("✅ ከተማዎ ተስተካክሏል!", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def prompt_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📝 እባክዎን አጭር **Bio (ስለእርስዎ)** ይጻፉ፦", parse_mode="Markdown")
    return SET_BIO

async def save_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db.update_user_field(user_id, "bio", update.message.text)
    await update.message.reply_text("✅ Bio ተስተካክሏል!", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# Confession submission flow
async def prompt_confession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✍️ እባክዎን ለማስተላለፍ የሚፈልጉትን **ሐሳብ/Confession** አሁን ይጻፉ፦", parse_mode="Markdown")
    return SEND_CONFESSION

async def handle_confession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    confession_text = update.message.text
    
    # Give 5 Aura for submitting
    db.add_aura(user_id, 5)
    
    # Send to admin for review
    admin_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve & Post", callback_data=f"app_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
        ]
    ])
    
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 **አዲስ Confession ደርሷል፦**\n\n\"{confession_text}\"",
        parse_mode="Markdown",
        reply_markup=admin_keyboard
    )
    
    # Save the text in bot_data temporarily
    context.bot_data[f"msg_{user_id}"] = confession_text
    
    await update.message.reply_text("✅ ሐሳብዎ ለአድሚን ተልኳል! ስለተሳተፉ +5 ⭐ Aura አግኝተዋል።", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# Admin review action
async def admin_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("app_"):
        sender_id = int(data.split("_")[1])
        conf_text = context.bot_data.get(f"msg_{sender_id}", query.message.text)
        
        # Post to Channel
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"💬 **Anonymous Thought:**\n\n\"{conf_text}\"\n\n🤖 @YourBotUsername"
        )
        db.add_aura(sender_id, 10) # Bonus Aura
        await query.edit_message_text(f"✅ Approved and Posted to Channel!\n\n{conf_text}")
        
    elif data.startswith("rej_"):
        await query.edit_message_text("❌ Rejected.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    
    profile_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(prompt_name, pattern="^change_name$"),
            CallbackQueryHandler(prompt_city, pattern="^change_city$"),
            CallbackQueryHandler(prompt_bio, pattern="^change_bio$"),
            CallbackQueryHandler(prompt_confession, pattern="^confess$")
        ],
        states={
            SET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)],
            SET_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_city)],
            SET_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_bio)],
            SEND_CONFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confession)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(profile_handler)
    app.add_handler(CallbackQueryHandler(admin_review, pattern="^(app_|rej_)"))
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_polling()

if __name__ == "__main__":
    main()