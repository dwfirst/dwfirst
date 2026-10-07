"""
Модуль: core
Слой: ядро: GGUF-модель, промпты, загрузчик

Единый интерфейс: info(), get_state(), set_state(**kwargs), clear()
"""
import os

X = "X:" + os.sep
HOME = os.path.join(X, "01_core")


def info():
    return "[core] заглушка. Папка: " + HOME


def get_state():
    return {
        "name": "core",
        "folder": HOME,
        "exists": os.path.isdir(HOME),
        "files": sorted(os.listdir(HOME)) if os.path.isdir(HOME) else [],
    }


def set_state(**kwargs):
    return {"todo": "set_state", "args": kwargs}


def clear():
    return {"todo": "clear"}