import re
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply import main_menu

# Инициализируем роутер
router = Router()

# Определяем состояния процесса авторизации
class RegistrationStates(StatesGroup):
    awaiting_phone = State()
    awaiting_firstname = State()
    awaiting_lastname = State()
    awaiting_gender = State()
    awaiting_birth_year = State()
    awaiting_city = State()
    awaiting_hobby = State()
    awaiting_profile_pic = State()
    awaiting_geo = State()

# Центральное хранилище профилей
USER_PROFILES = {}

# Номера с правами администратора
ADMIN_NUMBERS = {"+79998887766", "+79995554433"}

# Доступные города
CITIES = ["Москва", "Санкт-Петербург", "Ижевск", "Краснодар", "Сочи", "Иной"]

# Список увлечений
HOBBIES = ["Фитнес", "Творчество", "Фильмы", "Туризм", "Гейминг", "Литература", "Наука"]

@router.message(F.text == "/start")
async def handle_start_cmd(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Сбрасывает состояние и предлагает начать взаимодействие.
    """
    # Очищаем текущее состояние
    await state.clear()

    # Формируем стартовую клавиатуру
    initial_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Приступить")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    # Отправляем приветственное сообщение
    await message.answer(
        "Здравствуйте! Начнем работу?",
        reply_markup=initial_keyboard
    )

@router.message(F.text == "Приступить")
async def request_phone_number(message: Message, state: FSMContext):
    """
    Начинает процесс регистрации, запрашивая контактный номер.
    """
    # Создаем клавиатуру для отправки контакта
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Передать номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "Для продолжения нам нужен ваш номер телефона:",
        reply_markup=phone_keyboard
    )

    # Активируем состояние ожидания номера
    await state.set_state(RegistrationStates.awaiting_phone)

@router.message(RegistrationStates.awaiting_phone, F.contact)
async def process_received_contact(message: Message, state: FSMContext):
    """
    Обрабатывает полученный контакт (номер телефона).
    Проверяет доступ и наличие профиля.
    """
    # Извлекаем и нормализуем номер
    user_phone = message.contact.phone_number

    # Приводим номер к стандартному формату
    if user_phone.startswith("8"):
        user_phone = "+7" + user_phone[1:]
    elif not user_phone.startswith("+"):
        user_phone = "+" + user_phone

    current_user = message.from_user.id

    # Сохраняем информацию в состоянии
    await state.update_data(
        phone_number=user_phone,
        telegram_id=current_user
    )

    # Проверка административных прав
    if user_phone in ADMIN_NUMBERS:
        await message.answer(
            "Вход выполнен с административными полномочиями.",
            reply_markup=main_menu
        )
        await state.clear()
        return

    # Проверка существующего профиля
    if current_user in USER_PROFILES:
        await message.answer(
            "С возвращением! Ваш профиль уже активен.",
            reply_markup=main_menu
        )
        await state.clear()
        return

    # Запрос имени для нового пользователя
    await message.answer(
        "Укажите ваше имя:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[],
            resize_keyboard=True
        )
    )
    await state.set_state(RegistrationStates.awaiting_firstname)

# --- Блок проверки и обработки персональной информации ---

def check_name_validity(input_string: str) -> bool:
    """
    Проверяет корректность введенного имени или фамилии.
    Разрешены только символы алфавита.
    """
    pattern = re.compile(r'^[а-яА-ЯёЁa-zA-Z]+$')
    return bool(pattern.fullmatch(input_string.strip()))

@router.message(RegistrationStates.awaiting_firstname)
async def collect_first_name(message: Message, state: FSMContext):
    """
    Принимает и верифицирует имя пользователя.
    """
    name_input = message.text.strip()

    if not check_name_validity(name_input):
        await message.answer("Имя должно содержать только буквы. Повторите ввод.")
        return

    await state.update_data(first_name=name_input)

    await message.answer("Теперь введите фамилию:")
    await state.set_state(RegistrationStates.awaiting_lastname)

@router.message(RegistrationStates.awaiting_lastname)
async def collect_last_name(message: Message, state: FSMContext):
    """
    Принимает и проверяет фамилию пользователя.
    """
    surname_input = message.text.strip()

    if not check_name_validity(surname_input):
        await message.answer("Фамилия должна содержать только буквы. Попробуйте снова.")
        return

    await state.update_data(last_name=surname_input)

    # Формируем клавиатуру для выбора пола
    gender_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужчина"), KeyboardButton(text="Женщина")],
            [KeyboardButton(text="Пропустить")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Выберите пол (можно пропустить):",
        reply_markup=gender_keyboard
    )
    await state.set_state(RegistrationStates.awaiting_gender)

@router.message(RegistrationStates.awaiting_gender)
async def handle_gender_choice(message: Message, state: FSMContext):
    """
    Обрабатывает выбор пола.
    """
    gender_choice = message.text

    if gender_choice in ("Мужчина", "Женщина"):
        gender_dict = {"Мужчина": "man", "Женщина": "woman"}
        await state.update_data(user_gender=gender_dict[gender_choice])
    elif gender_choice == "Пропустить":
        await state.update_data(user_gender=None)
    else:
        await message.answer("Пожалуйста, используйте кнопки для выбора.")
        return

    await message.answer(
        "Введите год рождения (формат: 1990):",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[],
            resize_keyboard=True
        )
    )
    await state.set_state(RegistrationStates.awaiting_birth_year)

@router.message(RegistrationStates.awaiting_birth_year)
async def validate_birth_year(message: Message, state: FSMContext):
    """
    Проверяет и сохраняет год рождения.
    """
    year_input = message.text

    if not year_input.isdigit():
        await message.answer("Год должен быть числом. Введите заново.")
        return

    year_value = int(year_input)
    current_year = 2024

    if year_value < current_year - 100 or year_value > current_year - 12:
        await message.answer("Год рождения должен быть в допустимых пределах.")
        return

    await state.update_data(birth_year=year_value)

    # Создаем клавиатуру для выбора города
    city_selection_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=city)] for city in CITIES],
        resize_keyboard=True
    )

    await message.answer(
        "Выберите город проживания:",
        reply_markup=city_selection_keyboard
    )
    await state.set_state(RegistrationStates.awaiting_city)

@router.message(RegistrationStates.awaiting_city)
async def process_city_selection(message: Message, state: FSMContext):
    """
    Обрабатывает выбор города.
    """
    selected_city = message.text

    if selected_city not in CITIES:
        await message.answer("Выберите город из представленного перечня.")
        return

    await state.update_data(city=selected_city)

    # Формируем клавиатуру для выбора увлечений
    hobby_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=hobby)] for hobby in HOBBIES] +
        [[KeyboardButton(text="Без увлечений")]],
        resize_keyboard=True
    )

    await message.answer(
        "Выберите основное увлечение:",
        reply_markup=hobby_keyboard
    )
    await state.set_state(RegistrationStates.awaiting_hobby)

@router.message(RegistrationStates.awaiting_hobby)
async def handle_hobby_choice(message: Message, state: FSMContext):
    """
    Обрабатывает выбор увлечения.
    """
    chosen_hobby = message.text

    if chosen_hobby in HOBBIES:
        await state.update_data(hobby=chosen_hobby)
    elif chosen_hobby == "Без увлечений":
        await state.update_data(hobby=None)
    else:
        await message.answer("Сделайте выбор из доступных опций.")
        return

    # Формируем клавиатуру для загрузки изображения
    photo_upload_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить фото")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Загрузите ваше фото (необязательно):",
        reply_markup=photo_upload_keyboard
    )
    await state.set_state(RegistrationStates.awaiting_profile_pic)

@router.message(RegistrationStates.awaiting_profile_pic, F.photo)
async def store_profile_image(message: Message, state: FSMContext):
    """
    Сохраняет загруженное фото профиля.
    """
    image_id = message.photo[-1].file_id
    await state.update_data(profile_image=image_id)

    # Переходим к запросу геоданных
    await ask_for_geodata(message, state)

@router.message(RegistrationStates.awaiting_profile_pic, F.text == "Пропустить фото")
async def skip_image_upload(message: Message, state: FSMContext):
    """
    Обрабатывает пропуск загрузки фото.
    """
    await state.update_data(profile_image=None)

    # Переходим к запросу геоданных
    await ask_for_geodata(message, state)

@router.message(RegistrationStates.awaiting_profile_pic)
async def handle_wrong_image_input(message: Message):
    """
    Обрабатывает некорректный ввод при загрузке фото.
    """
    await message.answer("Отправьте фотографию или нажмите 'Пропустить фото'.")

async def ask_for_geodata(message: Message, state: FSMContext):
    """
    Запрашивает информацию о местоположении.
    """
    # Создаем клавиатуру для запроса геолокации
    geo_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить местоположение", request_location=True)],
            [KeyboardButton(text="Не делиться")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Хотите указать ваше местоположение?",
        reply_markup=geo_keyboard
    )

    await state.set_state(RegistrationStates.awaiting_geo)

@router.message(RegistrationStates.awaiting_geo, F.location | (F.text == "Не делиться"))
async def complete_registration_process(message: Message, state: FSMContext):
    """
    Завершает регистрацию и сохраняет профиль.
    """
    # Извлекаем собранные данные
    collected_data = await state.get_data()
    user_id = collected_data["telegram_id"]

    # Формируем структуру профиля
    USER_PROFILES[user_id] = {
        "bio": {
            "first_name": collected_data["first_name"],
            "last_name": collected_data["last_name"],
            "gender": collected_data.get("user_gender"),
            "birth_year": collected_data.get("birth_year")
        },
        "geo_info": {
            "city": collected_data.get("city"),
            "coordinates": (
                f"{message.location.latitude},{message.location.longitude}"
                if message.location else None
            )
        },
        "preferences": {
            "hobby": collected_data.get("hobby")
        },
        "media_content": {
            "profile_image": collected_data.get("profile_image")
        },
        "contacts": {
            "phone_number": collected_data["phone_number"]
        }
    }

    # Отправляем подтверждение
    await message.answer(
        "Профиль успешно создан!",
        reply_markup=main_menu
    )

    # Очищаем состояние
    await state.clear()

@router.message(RegistrationStates.awaiting_geo)
async def handle_invalid_geo_input(message: Message):
    """
    Обрабатывает некорректный ввод при запросе геолокации.
    """
    await message.answer("Отправьте местоположение или нажмите 'Не делиться'.")