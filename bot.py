from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random

# -----------------------------------------
#   DEVOÇÕES
# -----------------------------------------
devocionais = {
    "fé": [
        "“A fé é o firme fundamento das coisas que se esperam...” (Hebreus 11:1)",
        "“Porque andamos por fé e não pelo que vemos.” (2 Coríntios 5:7)"
    ],
    "esperança": [
        "“Alegrai-vos na esperança...” (Romanos 12:12)",
        "“Os que esperam no Senhor renovam as suas forças.” (Isaías 40:31)"
    ],
    "gratidão": [
        "“Em tudo dai graças...” (1 Tessalonicenses 5:18)"
    ]
}

# -----------------------------------------
#   COMANDOS
# -----------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Bem-vindo ao Devocional Diário!*\n\n"
        "Use /temas para ver a lista de temas.\n"
        "Use /devocional <tema> para receber uma mensagem.\n\n"
        "Exemplo:\n/devocional fé\n",
        parse_mode="Markdown"
    )

async def temas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista = "\n".join(f"• {t}" for t in devocionais.keys())
    await update.message.reply_text(f"📚 *Temas disponíveis:*\n\n{lista}", parse_mode="Markdown")

async def devocional(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim:\n/devocional <tema>")
        return
    
    tema = context.args[0].lower()

    if tema not in devocionais:
        await update.message.reply_text("Tema não encontrado. Use /temas.")
        return
    
    mensagem = random.choice(devocionais[tema])
    await update.message.reply_text(
        f"📖 *Devocional sobre {tema.title()}*\n\n{mensagem}",
        parse_mode="Markdown"
    )

# -----------------------------------------
#   MAIN
# -----------------------------------------
def main():
    TOKEN = "8478210121:AAHXe_z_waj8gP040_xESMOXQRJmZ74TwKo"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("temas", temas))
    app.add_handler(CommandHandler("devocional", devocional))

    print("BOT RODANDO...")
    app.run_polling()


if __name__ == "__main__":
    main()
