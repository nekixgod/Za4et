import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импорт модулей обработчиков
from handlers import auth, common, knb, kub, book

# Загрузка переменных окружения
load_dotenv()

# Получение токена бота
BOT_TOKEN = getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError(
        "Токен не обнаружен! Убедитесь, что переменная BOT_TOKEN "
        "определена в файле .env"
    )

async def initialize_bot() -> None:
    """
    Основная функция инициализации и запуска бота.
    """
    # Создание экземпляра бота
    bot_instance = Bot(token=BOT_TOKEN)

    # Настройка хранилища состояний
    state_storage = MemoryStorage()

    # Инициализация диспетчера
    dispatcher = Dispatcher(storage=state_storage)

    # Регистрация всех роутеров
    dispatcher.include_router(auth.router)      # Авторизация и регистрация
    dispatcher.include_router(knb.router)       # Испытание элементов
    dispatcher.include_router(kub.router)       # Бросок кубика
    dispatcher.include_router(book.router)      # Энциклопедия фэнтези
    dispatcher.include_router(common.router)    # Общие команды

    # Очистка вебхуков и ожидающих обновлений
    await bot_instance.delete_webhook(drop_pending_updates=True)

    # Информационное сообщение о запуске
    logging.info("Bot Companion успешно активирован!")
    print("=" * 50)
    print("Система Bot Companion запущена и готова к работе")
    print("Для остановки используйте комбинацию Ctrl+C")
    print("=" * 50)

    # Запуск обработки входящих сообщений
    await dispatcher.start_polling(bot_instance)

if __name__ == "__main__":
    # Базовая настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

    try:
        # Запуск асинхронного приложения
        asyncio.run(initialize_bot())
    except KeyboardInterrupt:
        # Корректная обработка прерывания
        logging.info("Получен сигнал прерывания. Остановка системы...")
        print("\n" + "=" * 50)
        print("Система Bot Companion корректно остановлена")
        print("=" * 50)
    except Exception as unexpected_error:
        # Обработка неожиданных ошибок
        logging.error(f"Критическая ошибка: {unexpected_error}")
        print(f"\nПроизошла непредвиденная ошибка: {unexpected_error}")
        sys.exit(1)