import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)

# Bot configuration
TOKEN = "7676062189:AAH8F3GDnB24WVkImaKFb-F3nU1ZlrpuGLU"
DATABASE_GROUP = "@social-profile-database"
ADMIN_IDS = []  # Add admin user IDs here
ADVERTISEMENT_IMAGE = "https://t.me/c/2799653632/2"
DONATION_QR = "https://t.me/c/2799653632/3"

# Advertisement text
ADVERTISEMENT_TEXT = """
Discover art, learning, and more! 🎨 

🖼 Sketch Website: https://bit.ly/aniartxxx

📦 Dropshipping Course by Anirudh Karamungikar: https://superprofile.bio/course/Indian-Dropshipping-Mastery

📷 Instagram Personal: https://instagram.com/anirudh_karamungikar

🎨 Art Account: https://instagram.com/anirudhartx

📲 Buy/Sell Telegram Groups: 
https://aearnigame.github.io/buy-or-sell-telegram-old-groups/
https://spf.bio/FIRnB
"""

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# User states for conversation
(
    NAME,
    AGE,
    GENDER,
    LOCATION,
    BIO,
    PHOTO,
    CONFIRMATION
) = range(7)

# Temporary storage for user data
user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        f"Hi {user.first_name}! Welcome to Social-Profile!\n"
        "Let's create your profile. First, send me your name:"
    )
    return NAME

def get_name(update: Update, context: CallbackContext) -> None:
    """Store the name and ask for age."""
    user_data[update.effective_user.id] = {'name': update.message.text}
    update.message.reply_text("Great! Now send me your age:")
    return AGE

def get_age(update: Update, context: CallbackContext) -> None:
    """Store the age and ask for gender."""
    try:
        age = int(update.message.text)
        if age < 13 or age > 100:
            update.message.reply_text("Please enter a valid age between 13 and 100:")
            return AGE
        user_data[update.effective_user.id]['age'] = age
        
        keyboard = [
            [InlineKeyboardButton("Male", callback_data='male')],
            [InlineKeyboardButton("Female", callback_data='female')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Select your gender:", reply_markup=reply_markup)
        return GENDER
    except ValueError:
        update.message.reply_text("Please enter a valid number for age:")
        return AGE

def get_gender(update: Update, context: CallbackContext) -> None:
    """Store the gender and ask for location."""
    query = update.callback_query
    query.answer()
    user_data[query.from_user.id]['gender'] = query.data
    query.edit_message_text(text=f"Gender set to {query.data}.\nNow send me your location:")
    return LOCATION

def get_location(update: Update, context: CallbackContext) -> None:
    """Store the location and ask for bio."""
    user_data[update.effective_user.id]['location'] = update.message.text
    update.message.reply_text("Almost done! Send me a short bio about yourself:")
    return BIO

def get_bio(update: Update, context: CallbackContext) -> None:
    """Store the bio and ask for photo."""
    user_data[update.effective_user.id]['bio'] = update.message.text
    update.message.reply_text("Perfect! Now send me one photo for your profile:")
    return PHOTO

def get_photo(update: Update, context: CallbackContext) -> None:
    """Store the photo and ask for confirmation."""
    photo_file = update.message.photo[-1].get_file()
    user_data[update.effective_user.id]['photo_id'] = photo_file.file_id
    
    user_info = user_data[update.effective_user.id]
    confirmation_message = (
        "Please confirm your profile details:\n\n"
        f"Name: {user_info['name']}\n"
        f"Age: {user_info['age']}\n"
        f"Gender: {user_info['gender']}\n"
        f"Location: {user_info['location']}\n"
        f"Bio: {user_info['bio']}\n\n"
        "Is this information correct?"
    )
    
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='confirm_yes')],
        [InlineKeyboardButton("No, start over", callback_data='confirm_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=user_info['photo_id'],
        caption=confirmation_message,
        reply_markup=reply_markup
    )
    return CONFIRMATION

def confirm_profile(update: Update, context: CallbackContext) -> None:
    """Handle profile confirmation."""
    query = update.callback_query
    query.answer()
    
    if query.data == 'confirm_yes':
        user_info = user_data[query.from_user.id]
        username = f"@{query.from_user.username}" if query.from_user.username else "No username"
        
        # Format profile for database
        profile_message = (
            f"New Profile Submission:\n\n"
            f"Name: {user_info['name']}\n"
            f"Age: {user_info['age']}\n"
            f"Gender: {user_info['gender']}\n"
            f"Location: {user_info['location']}\n"
            f"Bio: {user_info['bio']}\n"
            f"Telegram: {username}\n\n"
            f"Owned by Anirudh Karamungikar (Artist) © 2025 @anirudhsq"
        )
        
        # Send to database group
        context.bot.send_photo(
            chat_id=DATABASE_GROUP,
            photo=user_info['photo_id'],
            caption=profile_message
        )
        
        query.edit_message_caption(caption="Thank you! Your profile has been submitted.")
        
        # Send welcome message with advertisement
        keyboard = [
            [InlineKeyboardButton("🌟 Donate", callback_data='donate')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_photo(
            chat_id=query.from_user.id,
            photo=ADVERTISEMENT_IMAGE,
            caption=ADVERTISEMENT_TEXT,
            reply_markup=reply_markup
        )
        
        # Clear user data
        del user_data[query.from_user.id]
    else:
        query.edit_message_caption(caption="Okay, let's start over. Send me your name:")
        del user_data[query.from_user.id]
        return NAME
    
    return ConversationHandler.END

def donate(update: Update, context: CallbackContext) -> None:
    """Show donation QR code."""
    query = update.callback_query
    query.answer()
    
    context.bot.send_photo(
        chat_id=query.from_user.id,
        photo=DONATION_QR,
        caption="Thank you for considering a donation! ❤️"
    )

def cancel(update: Update, context: CallbackContext) -> None:
    """Cancel the conversation."""
    if update.effective_user.id in user_data:
        del user_data[update.effective_user.id]
    update.message.reply_text("Profile creation cancelled.")
    return ConversationHandler.END

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main() -> None:
    """Start the bot."""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Conversation handler for profile creation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, get_age)],
            GENDER: [CallbackQueryHandler(get_gender)],
            LOCATION: [MessageHandler(Filters.text & ~Filters.command, get_location)],
            BIO: [MessageHandler(Filters.text & ~Filters.command, get_bio)],
            PHOTO: [MessageHandler(Filters.photo & ~Filters.command, get_photo)],
            CONFIRMATION: [CallbackQueryHandler(confirm_profile)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(donate, pattern='^donate$'))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
