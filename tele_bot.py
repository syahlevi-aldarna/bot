import os
import asyncio
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.mcp_client import MCPClient

# Load environment variable buat ambil API token
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

# Initialize MCP Client
mcp_client = MCPClient(port=3000)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("Maaf, lo bukan owner dari bot ini. Akses ditolak.")
        return
    await update.message.reply_text("Alpha-Bot 2026 Ready. Ruflo Swarm menunggu perintah lo, bos!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != OWNER_ID:
        return
        
    user_message = update.message.text
    
    # Kirim status "typing..." biar kelihatan bot lagi mikir
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # ---------------------------------------------------------
    # CORE LOGIC: Spawn Ruflo agent via MCP
    # ---------------------------------------------------------
    try:
        print(f"[Telegram] User message: {user_message}")
        
        # Connect to MCP if not connected
        if not mcp_client.isConnected:
            await mcp_client.connect()
        
        # Spawn coder agent
        print(f"[MCP] Spawning coder agent...")
        agent_id = await mcp_client.spawnAgent({
            "type": "coder",
            "task": user_message,
            "namespace": "telegram-tasks"
        })
        
        await update.message.reply_text(f"🤖 Agent spawned: {agent_id}\n⏳ Working on your task...")
        
        # Poll agent status
        max_polls = 30  # 30 * 2 seconds = 60 seconds timeout
        poll_count = 0
        
        while poll_count < max_polls:
            await asyncio.sleep(2)
            poll_count += 1
            
            status = await mcp_client.getAgentStatus(agent_id)
            print(f"[MCP] Agent status: {status['status']}")
            
            if status['status'] == 'running':
                await update.message.reply_text(f"🔄 Agent working...\n{status.get('output', '')}")
            
            elif status['status'] == 'completed':
                result = status.get('output', 'Task completed')
                await update.message.reply_text(f"✅ Task completed!\n\n{result}")
                
                # Store result in memory
                await mcp_client.memoryStore({
                    "namespace": "telegram-tasks",
                    "key": f"task-{agent_id}",
                    "value": {
                        "task": user_message,
                        "result": result,
                        "timestamp": str(asyncio.get_event_loop().time())
                    }
                })
                break
            
            elif status['status'] == 'error':
                error_msg = status.get('error', 'Unknown error')
                await update.message.reply_text(f"❌ Agent error:\n{error_msg}")
                break
            
            elif status['status'] == 'killed':
                await update.message.reply_text(f"⚠️ Agent was killed")
                break
        
        if poll_count >= max_polls:
            await update.message.reply_text("⌛ Agent timeout (60 seconds)")
            await mcp_client.killAgent(agent_id)

    except Exception as e:
        print(f"[Error] {str(e)}")
        await update.message.reply_text(f"🚨 Error: {str(e)}")

def main() -> None:
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN belum di-set di file .env")
        return
        
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Telegram berjalan... Tekan Ctrl+C untuk berhenti.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
