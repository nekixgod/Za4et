from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основное меню навигации
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Моя анкета")],
        [KeyboardButton(text="🎮 Развлечения")],
        [KeyboardButton(text="📚 Читалка")],
        [KeyboardButton(text="📘 Справка")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

# Меню выбора активностей
activities_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✂️ Камень-ножницы-бумага")],
        [KeyboardButton(text="🎲 Бросок кубика")],
        [KeyboardButton(text="◀️ Основное меню")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите активность"
)

# Меню для игры "Камень-Ножницы-Бумага"
elemental_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗿 Камень"),
            KeyboardButton(text="✂️ Ножницы"),
            KeyboardButton(text="📄 Бумага")
        ],
        [KeyboardButton(text="◀️ К активности")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Сделайте выбор"
)

# Меню для игры с кубиком
dice_game_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="1️⃣"),
            KeyboardButton(text="2️⃣"),
            KeyboardButton(text="3️⃣")
        ],
        [
            KeyboardButton(text="4️⃣"),
            KeyboardButton(text="5️⃣"),
            KeyboardButton(text="6️⃣")
        ],
        [KeyboardButton(text="◀️ К активности")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Предположите результат"
)

# Экспорт всех клавиатур для использования в других модулях
__all__ = [
    'main_menu',
    'activities_menu',
    'elemental_menu',
    'dice_game_menu'
]