"""infer.py — генерация ответа. Принимает готовый llama-объект, возвращает текст + метрики."""
import time


def generate(llama, messages, max_tokens=512, temperature=0.7, top_p=0.9):
    """Запускает генерацию. messages — [{'role': 'user', 'content': '...'}, ...]"""
    t0 = time.time()
    out = llama.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    dt = time.time() - t0
    usage = out.get('usage', {})
    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)
    tps = completion_tokens / dt if dt > 0 else 0.0
    text = out['choices'][0]['message']['content']
    return {
        'text': text,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'seconds': round(dt, 2),
        'tps': round(tps, 2),
    }


def count_tokens(llama, text):
    """Считает токены в тексте через токенизатор модели."""
    return len(llama.tokenize(text.encode('utf-8')))


def count_messages_tokens(llama, messages):
    """Считает токены в списке сообщений (грубо, по контенту)."""
    total = 0
    for m in messages:
        total += count_tokens(llama, m.get('content', ''))
    return total


if __name__ == '__main__':
    print('infer.py — модуль генерации. Импортируй generate().')