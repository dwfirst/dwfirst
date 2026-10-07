# Список команд оркестратора. UI дёргает их по имени.

COMMANDS = [
    # сервисные
    "ping", "state", "module_info", "modules_status",
    # модель
    "switch_model", "set_threads", "reload_model",
    # роль / проект
    "set_role", "set_project",
    # память
    "clear_session", "clear_working", "clear_long", "rebuild_chroma",
    # рефлексия
    "run_reflection",
]

COMMAND_DESCRIPTIONS = {
    "ping":            "Проверка живости оркестратора",
    "state":           "Текущее состояние (модель, роль, проект)",
    "module_info":     "Информация о модуле по имени",
    "modules_status":  "Есть ли файл module.py у каждого слоя",
    "switch_model":    "Сменить активную GGUF-модель",
    "set_threads":     "Задать число потоков CPU",
    "reload_model":    "Перезагрузить модель с новыми параметрами",
    "set_role":        "Активировать роль (writer, coder...)",
    "set_project":     "Активировать проект (book_iris, agi_iris...)",
    "clear_session":   "Стереть текущую сессию (02_memory_fast)",
    "clear_working":   "Стереть факты дня (03_memory_working)",
    "clear_long":      "Стереть долгую память (04_memory_long)",
    "rebuild_chroma":  "Пересобрать векторную базу (05_chroma)",
    "run_reflection":  "Запустить сон вручную (06_reflection)",
}
