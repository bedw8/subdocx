from dataclasses import dataclass
from pydantic import BaseModel
from typing import Self, Callable, Any

formatType = dict[str, Callable[[Any], Any]]


# @dataclass
class SubConfig(BaseModel):
    format: formatType = {}
    exclude: list[str] = []
    exclude_n: list[str] = []
    only: list[str] = []
    only_n: list[str] = []

    def _load_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.__dict__:
                setattr(self, k, v)
            else:
                print(f"'{k}' no a valid option. ignoring")

        # if not self.is_norm:
        #    Template._normalized_templates[self.id].custom_options(**kwargs)

    def _value(self, key: str):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            raise Exception(f"attribute '{key}' does not exist")

    def get(self: Self, key: str, fallback: Self | None):
        if fallback is None:
            # return self._value(key)
            return getattr(self, key)
        else:
            # val = self._value(key)
            val = getattr(self, key)
            if val == self.model_fields[key].default:
                return fallback.get(key=key, fallback=None)
            else:
                return val
