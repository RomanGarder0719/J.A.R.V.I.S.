# ai/ai_handler.py
import os
import json
import openai
from rich import print

from ai.prompts import CLASSIFY_PROMPT, PLUGIN_TEMPLATE
from plugin_manager import PluginManager


class AIHandler:
    def __init__(self, player=None, plugins: PluginManager = None):
        self._player = player
        self._plugins = plugins

        # env API-ключ
        self._api_key = os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise RuntimeError("Не найден OPENAI_API_KEY в окружении")

        # Инициализируем клиент с API ключом
        self.client = openai.OpenAI(api_key=self._api_key)
        openai.api_key = self._api_key  # Для обратной совместимости

    def handle_phrase(self, phrase: str) -> bool:
        """
        Получает фразу и решает: ответить или создать плагин.
        Возвращает True если что-то обработано.
        """
        try:
            result = self._ask_gpt(phrase)
        except Exception as e:
            print(f"[red]Ошибка GPT: {e}[/red]")
            return False

        if result.get("type") == "answer":
            print(f"[yellow]GPT:[/yellow] {result['content']}")
            return True

        elif result.get("type") == "plugin":
            name = result.get("name", "new_plugin").strip().lower()
            keywords = result.get("keywords", [])
            code_body = result.get("code", "pass")

            code = PLUGIN_TEMPLATE.format(
                name=name,
                keywords=json.dumps(keywords, ensure_ascii=False),
                code=code_body,
            )

            filename = f"{name}.py"
            self._plugins.add_plugin(filename, code)
            print(f"[green]✅ Новый плагин добавлен:[/green] {filename}")
            return True

        return False

    # --- GPT вызов ---
    def _ask_gpt(self, phrase: str) -> dict:
        """Отправляет запрос в GPT и парсит JSON-ответ"""
        prompt = CLASSIFY_PROMPT + f"\n\nВход: {phrase}"

        resp = self.client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = resp.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[red]Ошибка парсинга JSON: {e}[/red]")
            print(f"[red]Полученный контент: {content}[/red]")
            raise ValueError(f"Некорректный JSON от GPT: {content}")