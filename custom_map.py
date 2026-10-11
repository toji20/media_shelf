"""Собственный класс для маппинга «ключ -> значение» (dict использовать нельзя)."""


class CustomMap:
    def __init__(self):
        self._keys = []
        self._values = []

    # --- геттеры / сеттеры ---
    @property
    def keys(self):
        return list(self._keys)

    @keys.setter
    def keys(self, value):
        if len(value) != len(self._values):
            raise ValueError("Количество ключей должно совпадать с количеством значений")
        self._keys = list(value)

    @property
    def values(self):
        return list(self._values)

    @values.setter
    def values(self, value):
        if len(value) != len(self._keys):
            raise ValueError("Количество значений должно совпадать с количеством ключей")
        self._values = list(value)

    # --- поведение отображения ---
    def __setitem__(self, key, value):
        if key in self._keys:
            self._values[self._keys.index(key)] = value
        else:
            self._keys.append(key)
            self._values.append(value)

    def __getitem__(self, key):
        if key not in self._keys:
            raise KeyError(key)
        return self._values[self._keys.index(key)]

    def __contains__(self, key):
        return key in self._keys

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(self._keys)

    def get(self, key, default=None):
        return self[key] if key in self._keys else default

    def items(self):
        return list(zip(self._keys, self._values))

    def increment(self, key, step=1):
        self[key] = self.get(key, 0) + step

    def __eq__(self, other):
        if not isinstance(other, CustomMap):
            return NotImplemented
        return len(self) == len(other) and all(
            k in other and other[k] == v for k, v in self.items()
        )

    __hash__ = None  # изменяемый объект

    def __repr__(self):
        return f"CustomMap({self.items()!r})"

    def __str__(self):
        return ", ".join(f"{k}: {v}" for k, v in self.items())
