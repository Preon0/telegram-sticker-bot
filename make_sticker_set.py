from telegram import Bot, InputFile
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ConversationHandler
import aiohttp
import os

sticker_files = []
name = []
link = []
u_id = []

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("سلام زیبا! خوش اومدی.\nبا این ربات می‌تونی اسم پکای استیکری رو که می‌خوای، عوض کنی!")

async def send_sticker(update, context):
    await update.message.reply_text("تو این مرحله فقط باید استیکر بفرستی خوشگل.")

async def get_sticker(update, context):
    my_sticker = update.message.sticker
    
    if not my_sticker.set_name:
        await update.message.reply_text("این استیکر که متعلق به هیچ پکی نیستش که. یه استیکر بفرست که متعلق به پک باشه!")
        return ask_sticker
    
    set_name = my_sticker.set_name
    sticker_set = await context.bot.get_sticker_set(set_name)
    
    session = aiohttp.ClientSession()
    for s in sticker_set.stickers:
        file = await context.bot.get_file(s.file_id)

        file_data = await session.get(file.file_path)
        filename = f"{s.file_unique_id}.webp"
        
        with open(filename, 'wb') as f:
            f.write(await file_data.read())
        
        emoji = s.emoji
        sticker_files.append((filename, emoji))

    await session.close()
    await update.message.reply_text("خب حالا یه اسم خوشگل عین خودت برای پکت بفرست برام.")
    return ask_name

async def get_name(update, cotext):
    the_name = update.message.text
    the_id = update.message.from_user.id
    u_id.append(the_id)
    name.append(the_name)
    await update.message.reply_text("مرسییی از  تووو.\nحالا یه لینک براش بنویس. یه متن انگلیسی به‌هم‌چسبیده باید باشه!")
    return ask_link

async def get_link(update, context):
    the_link = update.message.text
    link.append(the_link)
    make_pack(update, context, sticker_files, u_id[0], link[0], name[0])

async def make_pack(update, context, packlist, users_id, user_link, user_title):
    sticker, emoji = packlist[0]
    sticker_name = f"{user_link}_by_StickerSetEditorBot"
    sticker_link = f"https://t.me/addstickers/{sticker_name}"
    with open(sticker, "rb") as s:
        await context.bot.create_new_sticker_set(
            user_id = users_id,
            name = sticker_name,
            title = user_title,
            png_sticker = InputFile(s),
            emojis = emoji
    )

    for i in range(1, len(packlist)):
        sticker, emoji = packlist[i]
        with open(sticker, "rb") as s:
            await context.bot.add_sticker_to_set(
                user_id = users_id,
                link_name = sticker_name,
                png_sticker = InputFile(s),
                emojis = emoji
            )
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"استیکرت آماده‌س زیبا!\n{sticker_link}")

async def change_name(update, context):
    await update.message.reply_text("می‌بینم که می‌خوای اسم یه پکو عوض کنی.\nیکی از استیکرای پکو بفرست برام.")
    return ask_sticker

async def cancel_change(update, context):
    await update.message.reply_text("مکالمه لغو شد ❌")
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("چیزی برای کنسل‌کردن نیستش که.")

ask_sticker, ask_name, ask_link = range(3)

def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # app.add_handler(CommandHandler("cancel", cancel))
    
    change_handler = ConversationHandler(
        entry_points=[CommandHandler("change_name", change_name)],
        states={
            ask_sticker: [
                MessageHandler(filters.Sticker.ALL, get_sticker),
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_sticker)
            ],
            ask_name: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ask_link: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)]
        },
        fallbacks=[CommandHandler("cancel", cancel_change)],
    )
    app.add_handler(change_handler)
    app.run_polling()

if __name__ == "__main__":
    start_bot()