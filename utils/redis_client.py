import redis
import json
import logging
import os
from typing import Optional, Any, Dict, List

class RedisClient:
    def __init__(self, host=None, port=6379, db=0, password=None):
        """
        Инициализация клиента Redis
        """
        self.logger = logging.getLogger(__name__)

        # Параметры подключения
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = int(port or os.getenv('REDIS_PORT', 6379))
        self.db = db
        self.password = password or os.getenv('REDIS_PASSWORD', None)

        # Подключение к Redis
        self.connect()

    def connect(self):
        """Установка соединения с Redis"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # Автоматически декодировать ответы в строки
            )
            # Проверка соединения
            self.client.ping()
            self.logger.info(f"✅ Подключено к Redis на {self.host}:{self.port}")
        except redis.ConnectionError as e:
            self.logger.error(f"❌ Ошибка подключения к Redis: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Проверка соединения"""
        if not self.client:
            return False
        try:
            return self.client.ping()
        except:
            return False

    # ==== Базовые операции ====

    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Установить значение по ключу"""
        try:
            # Если значение не строка - конвертируем в JSON
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)

            self.client.set(key, value)

            # Устанавливаем время жизни, если указано
            if expire:
                self.client.expire(key, expire)

            return True
        except Exception as e:
            self.logger.error(f"Ошибка при set {key}: {e}")
            return False

    def get(self, key: str, default=None) -> Optional[str]:
        """Получить значение по ключу"""
        try:
            value = self.client.get(key)
            if value is None:
                return default
            return value
        except Exception as e:
            self.logger.error(f"Ошибка при get {key}: {e}")
            return default

    def delete(self, key: str) -> bool:
        """Удалить ключ"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            self.logger.error(f"Ошибка при delete {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            self.logger.error(f"Ошибка при exists {key}: {e}")
            return False

    # ==== Для книги/читалки ====

    def save_page(self, user_id: int, book_name: str, page_number: int, content: str) -> bool:
        """
        Сохранить страницу книги
        Формат: book:{user_id}:{book_name}:page:{page_number}
        """
        key = f"book:{user_id}:{book_name}:page:{page_number}"
        return self.set(key, content)

    def get_page(self, user_id: int, book_name: str, page_number: int) -> Optional[str]:
        """Получить страницу книги"""
        key = f"book:{user_id}:{book_name}:page:{page_number}"
        return self.get(key)

    def save_bookmark(self, user_id: int, book_name: str, page_number: int) -> bool:
        """Сохранить закладку (последняя прочитанная страница)"""
        key = f"bookmark:{user_id}:{book_name}"
        return self.set(key, page_number)

    def get_bookmark(self, user_id: int, book_name: str) -> Optional[int]:
        """Получить закладку"""
        key = f"bookmark:{user_id}:{book_name}"
        value = self.get(key)
        return int(value) if value else None

    def list_user_books(self, user_id: int) -> List[str]:
        """Получить список книг пользователя"""
        pattern = f"bookmark:{user_id}:*"
        keys = self.client.keys(pattern)
        return [key.split(':')[2] for key in keys]  # Извлекаем имена книг

    def save_book_metadata(self, book_name: str, metadata: dict) -> bool:
        """Сохранить метаданные книги (автор, жанр, всего страниц и т.д.)"""
        key = f"book_meta:{book_name}"
        return self.set(key, metadata)

    def get_book_metadata(self, book_name: str) -> Optional[dict]:
        """Получить метаданные книги"""
        key = f"book_meta:{book_name}"
        value = self.get(key)
        return json.loads(value) if value else None

    # ==== Для списков ====

    def add_to_list(self, list_name: str, value: Any) -> bool:
        """Добавить элемент в список"""
        try:
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            self.client.rpush(list_name, value)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении в список {list_name}: {e}")
            return False

    def get_list(self, list_name: str, start=0, end=-1) -> List[str]:
        """Получить элементы списка"""
        try:
            return self.client.lrange(list_name, start, end)
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка {list_name}: {e}")
            return []

    # ==== Для хеш-таблиц ====

    def hset(self, name: str, key: str, value: Any) -> bool:
        """Установить поле в хеше"""
        try:
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            self.client.hset(name, key, value)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при hset {name}:{key}: {e}")
            return False

    def hget(self, name: str, key: str, default=None) -> Optional[str]:
        """Получить поле из хеша"""
        try:
            value = self.client.hget(name, key)
            return value if value else default
        except Exception as e:
            self.logger.error(f"Ошибка при hget {name}:{key}: {e}")
            return default

    def hgetall(self, name: str) -> Dict[str, str]:
        """Получить все поля хеша"""
        try:
            return self.client.hgetall(name)
        except Exception as e:
            self.logger.error(f"Ошибка при hgetall {name}: {e}")
            return {}

    # ==== Для счетчиков ====

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Увеличить счетчик"""
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            self.logger.error(f"Ошибка при increment {key}: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Уменьшить счетчик"""
        try:
            return self.client.decr(key, amount)
        except Exception as e:
            self.logger.error(f"Ошибка при decrement {key}: {e}")
            return None

# Создаем глобальный экземпляр для использования во всем боте
redis_client = RedisClient()
