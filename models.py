"""Модели предметной области. Все сущности наследуются от абстрактного Entity."""
from abc import ABC, abstractmethod
from datetime import datetime
from functools import total_ordering

from custom_map import CustomMap

TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
ALL_KINDS = "Все"
SORT_MODES = ("По названию", "По рейтингу", "По году")


class Entity(ABC):
    """Абстрактный класс всех сущностей приложения."""

    @abstractmethod
    def kind(self) -> str:
        """Название типа сущности."""

    @abstractmethod
    def to_row(self) -> list:
        """Представление сущности строкой для файла."""

    @abstractmethod
    def summary(self) -> str:
        """Краткое текстовое описание."""


@total_ordering
class MediaItem(Entity):
    """Базовый элемент медиатеки (сравнивается по названию, затем по году)."""

    MIN_YEAR = 1800

    def __init__(self, title, author, year, rating, extra):
        self.title = title
        self.author = author
        self.year = year
        self.rating = rating
        self.extra = extra

    # --- геттеры / сеттеры с валидацией ---
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Название не может быть пустым")
        self._title = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Автор не может быть пустым")
        self._author = value

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        value = int(value)
        if not self.MIN_YEAR <= value <= datetime.now().year + 1:
            raise ValueError("Некорректный год")
        self._year = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        value = int(value)
        if not 0 <= value <= 10:
            raise ValueError("Рейтинг должен быть от 0 до 10")
        self._rating = value

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, value):
        value = int(value)
        if value < 1:
            raise ValueError("Параметр должен быть положительным")
        self._extra = value

    # --- абстрактное поведение подтипов ---
    @abstractmethod
    def extra_text(self) -> str:
        """Человекочитаемое значение дополнительного параметра."""

    # --- реализация Entity ---
    def to_row(self):
        return [self.kind(), self._title, self._author,
                str(self._year), str(self._rating), str(self._extra)]

    def summary(self):
        return (f"{self.kind()}: «{self._title}»\n"
                f"Автор: {self._author}\n"
                f"Год: {self._year}\n"
                f"{self.extra_text()}")

    # --- специальные методы ---
    def _identity(self):
        return (self.kind(), self._title.lower(), self._author.lower(), self._year)

    def __eq__(self, other):
        if not isinstance(other, MediaItem):
            return NotImplemented
        return self._identity() == other._identity()

    def __hash__(self):
        return hash(self._identity())

    def __lt__(self, other):
        if not isinstance(other, MediaItem):
            return NotImplemented
        return (self._title.lower(), self._year) < (other._title.lower(), other._year)

    def __repr__(self):
        return (f"{type(self).__name__}(title={self._title!r}, author={self._author!r}, "
                f"year={self._year}, rating={self._rating}, extra={self._extra})")

    def __str__(self):
        return f"{self._title} — {self._author} ({self._year})"


class Book(MediaItem):
    def kind(self):
        return "Книга"

    def extra_text(self):
        return f"{self.extra} стр."


class Movie(MediaItem):
    def kind(self):
        return "Фильм"

    def extra_text(self):
        return f"{self.extra} мин."


class Album(MediaItem):
    def kind(self):
        return "Альбом"

    def extra_text(self):
        return f"{self.extra} треков"


class KindRegistry:
    """Фабрика и справочник типов (вместо dict используется CustomMap)."""

    NAMES = ("Книга", "Фильм", "Альбом")

    @staticmethod
    def labels() -> CustomMap:
        labels = CustomMap()
        labels["Книга"] = "Страниц"
        labels["Фильм"] = "Минут"
        labels["Альбом"] = "Треков"
        return labels

    @staticmethod
    def create(kind, title, author, year, rating, extra) -> MediaItem:
        if kind == "Книга":
            return Book(title, author, year, rating, extra)
        if kind == "Фильм":
            return Movie(title, author, year, rating, extra)
        if kind == "Альбом":
            return Album(title, author, year, rating, extra)
        raise ValueError(f"Неизвестный тип: {kind}")

    @staticmethod
    def from_row(row) -> MediaItem:
        return KindRegistry.create(row[0], row[1], row[2], row[3], row[4], row[5])


class Library:
    """Коллекция элементов медиатеки."""

    def __init__(self, items=None):
        self._items = list(items) if items else []

    @property
    def items(self):
        return list(self._items)

    @items.setter
    def items(self, value):
        self._items = list(value)

    def add(self, item: MediaItem):
        if item in self._items:
            raise ValueError("Такой элемент уже есть в медиатеке")
        self._items.append(item)

    def remove(self, item: MediaItem):
        self._items.remove(item)

    def find(self, kind=ALL_KINDS, query="", sort_mode=SORT_MODES[0]):
        query = query.strip().lower()
        result = [
            i for i in self._items
            if (kind == ALL_KINDS or i.kind() == kind)
            and (query in i.title.lower() or query in i.author.lower())
        ]
        if sort_mode == "По рейтингу":
            return sorted(result, key=lambda i: i.rating, reverse=True)
        if sort_mode == "По году":
            return sorted(result, key=lambda i: i.year)
        return sorted(result)  # использует __lt__

    def stats(self) -> CustomMap:
        stats = CustomMap()
        for name in KindRegistry.NAMES:
            stats[name] = 0
        for item in self._items:
            stats.increment(item.kind())
        return stats

    def average_rating(self):
        if not self._items:
            return 0.0
        return sum(i.rating for i in self._items) / len(self._items)

    @staticmethod
    def seed():
        return [
            Book("Мастер и Маргарита", "М. Булгаков", 1967, 10, 480),
            Book("1984", "Дж. Оруэлл", 1949, 9, 328),
            Book("Преступление и наказание", "Ф. Достоевский", 1866, 10, 672),
            Book("Война и мир", "Л. Толстой", 1869, 10, 1225),

            Movie("Начало", "К. Нолан", 2010, 9, 148),
            Movie("Интерстеллар", "К. Нолан", 2014, 10, 169),
            Movie("Зелёная миля", "Ф. Дарабонт", 1999, 10, 189),
            Movie("Побег из Шоушенка", "Ф. Дарабонт", 1994, 10, 142),

            Album("OK Computer", "Radiohead", 1997, 9, 12),
            Album("The Dark Side of the Moon", "Pink Floyd", 1973, 10, 10),
            Album("Nevermind", "Nirvana", 1991, 9, 12),
            Album("Abbey Road", "The Beatles", 1969, 10, 17),
        ]

@total_ordering
class SessionRecord(Entity):
    """Запись отчёта о работе приложения: login | time_in | time_out."""

    def __init__(self, login, time_in, time_out):
        self.login = login
        self.time_in = time_in
        self.time_out = time_out

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Логин не может быть пустым")
        self._login = value

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        self._time_out = value

    def kind(self):
        return "Сессия"

    def to_row(self):
        return [self._login,
                self._time_in.strftime(TIME_FORMAT),
                self._time_out.strftime(TIME_FORMAT)]

    def summary(self):
        return f"{self._login}: {self.to_row()[1]} — {self.to_row()[2]}"

    @staticmethod
    def from_row(row):
        return SessionRecord(row[0],
                             datetime.strptime(row[1], TIME_FORMAT),
                             datetime.strptime(row[2], TIME_FORMAT))

    def __eq__(self, other):
        if not isinstance(other, SessionRecord):
            return NotImplemented
        return (self._login, self._time_in, self._time_out) == \
               (other._login, other._time_in, other._time_out)

    def __hash__(self):
        return hash((self._login, self._time_in, self._time_out))

    def __lt__(self, other):
        if not isinstance(other, SessionRecord):
            return NotImplemented
        return self._time_in < other._time_in

    def __repr__(self):
        return (f"SessionRecord(login={self._login!r}, "
                f"time_in={self._time_in!r}, time_out={self._time_out!r})")

    def __str__(self):
        return self.summary()
