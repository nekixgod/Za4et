from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    """
    Группа состояний для процесса регистрации пользователя.
    Каждое состояние соответствует определенному этапу сбора информации.
    """
    awaiting_phone = State()           # Ожидание номера телефона
    awaiting_firstname = State()       # Ожидание имени пользователя
    awaiting_lastname = State()        # Ожидание фамилии пользователя
    awaiting_gender = State()          # Ожидание информации о поле
    awaiting_birth_year = State()      # Ожидание года рождения
    awaiting_city = State()            # Ожидание выбора города
    awaiting_hobby = State()           # Ожидание выбора увлечения
    awaiting_profile_pic = State()     # Ожидание загрузки фотографии
    awaiting_geo = State()             # Ожидание геолокационных данных