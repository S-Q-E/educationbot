from aiogram.types import BotCommand

async def set_bot_commands(bot):
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="pdf", description="Создать PDF-урок"),
        BotCommand(command="plan", description="Создать PDF-план обучения"),
        BotCommand(command="lesson", description="Сгенерировать урок"),
        BotCommand(command="quiz", description="Пройти викторину"),
    ]
    await bot.set_my_commands(commands)