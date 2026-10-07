# Как собирается итоговый промпт

1. system.txt           — базовый голос IRIS
2. 11_roles/<role>/     — prompt.md, style.md, rules.md активной роли
3. 10_projects/<...>/   — context.md активного проекта
4. 02_memory_fast\      — последние N сообщений
5. 05_chroma\           — топ-K семантических попаданий
6. 03_memory_working\   — активные факты
7. ---
8. текущий запрос пользователя
