#!/usr/bin/env python3
"""
Bot Telegram - Devocionais e Plano Bíblico usando Groq (OpenAI-compatible)
"""

import os
import traceback
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -----------------------------
# Config / Model selection
# -----------------------------
GROQ_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not GROQ_KEY:
    raise RuntimeError("Variável de ambiente GROQ_API_KEY não encontrada.")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Variável de ambiente TELEGRAM_TOKEN não encontrada.")

client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)

MODELOS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b"
]

temas_base = [
    "fé", "esperança", "gratidão", "perdão", "amor", "coragem", "sabedoria",
    "paciência", "confiança", "obediência", "adoração", "humildade",
    "justiça", "salvação", "família", "oração", "libertação", "propósito"
]

# -----------------------------
# Funções de geração (devocional e plano)
# -----------------------------
def chamar_modelo(prompt: str, modelo: str) -> tuple:
    """Função de chamada central ao modelo."""
    try:
        response = client.responses.create(
            model=modelo,
            input=prompt,
            max_output_tokens=500,
            temperature=0.7
        )
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text.strip(), None

        # Fallback
        try:
            out = response.output
            if isinstance(out, list) and len(out) > 0:
                first = out[0]
                if isinstance(first, dict) and "content" in first:
                    content = first["content"]
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "output_text":
                                return item.get("text", "").strip(), None
                return str(first).strip(), None
        except:
            pass

        return "", "Sem conteúdo textual identificável."

    except Exception as e:
        print(traceback.format_exc())
        return "", str(e)


def gerar_devocional(tema: str) -> str:
    prompt = (
        f"Escreva um devocional cristão curto e inspirador sobre o tema '{tema}'.\n\n"
        "- Inclua UM versículo bíblico (com referência correta).\n"
        "- Inclua uma reflexão.\n"
        "- Termine com UMA aplicação prática.\n"
        "- Texto acolhedor com ~130-220 palavras."
    )

    for m in MODELOS:
        texto, erro = chamar_modelo(prompt, m)
        if erro is None:
            return texto

    return "⚠️ Ocorreu um erro ao gerar o devocional."


def gerar_plano_biblico(total_dias: int) -> str:
    """
    Gera um plano bíblico estruturado para X dias.
    A IA organiza os capítulos por dia.
    """
    prompt = f"""
Crie um PLANO BÍBLICO completo para {total_dias} dias.

Regras:
- Divida os livros e capítulos da Bíblia de maneira equilibrada.
- Evite leituras extremamente longas em um único dia.
- Varie entre Antigo e Novo Testamento para manter consistência espiritual.
- Apresente o plano em formato organizado:
  Dia 1: ...
  Dia 2: ...
  etc.
- No final, inclua uma mensagem de motivação espiritual.
- Não ultrapasse 450-600 palavras.
"""

    for m in MODELOS:
        texto, erro = chamar_modelo(prompt, m)
        if erro is None:
            return texto

    return "⚠️ Ocorreu um erro ao gerar o plano bíblico."

# -----------------------------
# Handlers Telegram
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Bem-vindo ao Devocional Diário!*\n\n"
        "Comandos disponíveis:\n"
        "• /temas – ver lista de temas\n"
        "• /devocional <tema>\n"
        "• /plano <dias/meses> – Ex: /plano 30 dias, /plano 3 meses\n",
        parse_mode="Markdown"
    )

async def temas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista = "\n".join(f"• {t}" for t in temas_base)
    await update.message.reply_text(
        f"📚 *Temas disponíveis:*\n\n{lista}",
        parse_mode="Markdown"
    )

async def devocional(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim:\n/devocional <tema>")
        return

    tema = " ".join(context.args).lower().strip()
    temas_baixos = [t.lower() for t in temas_base]

    if tema not in temas_baixos:
        match = None
        for t in temas_baixos:
            if tema in t:
                match = t
                break

        if match is None:
            await update.message.reply_text("❌ Tema inválido!\nUse /temas para ver a lista.")
            return

        tema = match

    await update.message.reply_text("⏳ Gerando devocional...")
    mensagem = gerar_devocional(tema)

    await update.message.reply_text(
        f"📖 *Devocional sobre {tema.title()}*\n\n{mensagem}",
        parse_mode="Markdown"
    )

async def plano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim:\n/plano 30 dias\n/plano 3 meses")
        return

    entrada = " ".join(context.args).lower().strip()

    # Interpretar input (dias ou meses)
    num = None
    dias = None

    try:
        partes = entrada.split()
        num = int(partes[0])

        if "mes" in entrada or "mês" in entrada:
            dias = num * 30
        elif "dia" in entrada:
            dias = num
        else:
            await update.message.reply_text("❌ Especifique se é dias ou meses.\nEx: /plano 30 dias")
            return

    except:
        await update.message.reply_text("❌ Formato inválido.\nEx: /plano 30 dias, /plano 3 meses")
        return

    await update.message.reply_text(f"⏳ Montando plano bíblico para {dias} dias...")

    plano_texto = gerar_plano_biblico(dias)

    await update.message.reply_text(
        f"📘 *Plano Bíblico – {dias} dias*\n\n{plano_texto}",
        parse_mode="Markdown"
    )

# -----------------------------
# Main
# -----------------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("temas", temas))
    app.add_handler(CommandHandler("devocional", devocional))
    app.add_handler(CommandHandler("plano", plano))

    print("BOT RODANDO...")
    app.run_polling()

if __name__ == "__main__":
    main()
