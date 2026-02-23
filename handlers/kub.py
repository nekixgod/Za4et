import logging
import random
from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import dice_game_menu, activities_menu, main_menu

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "🎲 Бросок кубика")
async def initiate_dice_game(message: Message):
    """
    Запускает игру с предсказанием результата броска.
    """
    user_id = message.from_user.id
    logger.info(f"Инициализация игры в кубик пользователем {user_id}")

    await message.answer(
        "Предположите результат броска (от 1 до 6):",
        reply_markup=dice_game_menu
    )

@router.message(F.text.in_(["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]))
async def evaluate_dice_prediction(message: Message):
    """
    Обрабатывает предположение пользователя и сравнивает с реальным броском.
    """
    user_id = message.from_user.id
    logger.info(f"Получен выбор: '{message.text}' от пользователя {user_id}")

    # Сопоставление эмодзи с числовыми значениями
    emoji_mapping = {
        "1️⃣": 1, "2️⃣": 2, "3️⃣": 3,
        "4️⃣": 4, "5️⃣": 5, "6️⃣": 6
    }

    player_prediction = emoji_mapping[message.text]
    actual_result = random.randint(1, 6)

    logger.info(f"Предположение: {player_prediction}, Реальный бросок: {actual_result}")

    # Определение исхода
    if player_prediction == actual_result:
        outcome_message = "<b>🎉 Браво! Ваше предсказание сбылось!</b>"
        outcome_emoji = "🎉"
    else:
        outcome_message = f"<b>🔮 Неверное предположение.</b> Выпавшее значение: <code>{actual_result}</code>"
        outcome_emoji = "🔮"

    # Эмодзи для отображения результата
    result_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"][actual_result - 1]

    # Формирование игрового отчета
    game_summary = (
        f"<b>Ваш вариант:</b> {message.text}\n"
        f"<b>Результат броска:</b> {result_emoji}\n\n"
        f"{outcome_message}\n"
        f"Итог: {outcome_emoji}"
    )

    await message.answer(
        game_summary,
        reply_markup=dice_game_menu,
        parse_mode="HTML"
    )
@router.message(F.text == "◀️ К активности")  # ИЗМЕНЕНО
async def return_to_games_catalog(message: Message):
    """
    Возвращает пользователя к каталогу мини-игр.
    """
    await message.answer(
        "Доступные мини-игры:",
        reply_markup=activities_menu
    )

@router.message(F.text == "◀️ Основное меню")  # ИЗМЕНЕНО
async def navigate_to_main_screen(message: Message):
    """
    Перенаправляет пользователя на главный экран.
    """
    await message.answer(
        "Основная панель управления:",
        reply_markup=main_menu
    )
