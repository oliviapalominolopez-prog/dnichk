from telegram import Update
from telegram.ext import ContextTypes

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐚𝐩𝐚𝐫𝐭𝐚𝐝𝐨 𝐝𝐞 𝐑𝐞𝐜𝐚𝐫𝐠𝐚 𝐩𝐚𝐫𝐚 𝐮𝐬𝐚𝐫 𝐞𝐥 𝐛𝐨𝐭:\n"
        "𝐑𝐞𝐜𝐚𝐫𝐠𝐚 𝐝𝐢𝐬𝐩𝐨𝐧𝐢𝐛𝐥𝐞𝐬:\n"
        "➤𝟏𝟎 𝐬𝐨𝐥𝐞𝐬 = 𝟏𝟎 𝐭𝐨𝐤𝐞𝐧𝐬\n"
        "➤𝟐𝟎 𝐬𝐨𝐥𝐞𝐬 = 𝟐𝟑 𝐭𝐨𝐤𝐞𝐧𝐬\n"
        "➤𝟑𝟎 𝐬𝐨𝐥𝐞𝐬 = 𝟑𝟓 𝐭𝐨𝐤𝐞𝐧𝐬\n\n"
        "➤𝐍𝐨𝐭𝐚: 𝐂𝐚𝐝𝐚 𝐭𝐨𝐤𝐞𝐧 𝐞𝐬 𝐜𝐨𝐧𝐬𝐮𝐦𝐢𝐝𝐨 𝐚𝐥 𝐫𝐞𝐚𝐥𝐢𝐳𝐚𝐫 𝐮𝐧 𝐜𝐚𝐦𝐛𝐢𝐨 𝐝𝐞 𝐜𝐨𝐧𝐭𝐫𝐚𝐬𝐞ñ𝐚.\n\n"
        "𝐒𝐞𝐥𝐥𝐞𝐫 𝐚𝐮𝐭𝐨𝐫𝐢𝐳𝐚𝐝𝐨𝐬:\n"
        "@Addux12\n"
    )
    await update.message.reply_text(texto)
