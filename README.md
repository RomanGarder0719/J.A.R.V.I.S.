Voice Assistant made as an experiment using [Vosk](https://pypi.org/project/vosk/) and [ChatGPT](https://chat.openai.com/) (DeepSeek).

`The code has NOT been polished and is provided "as is". There are a lot of code that are redundant and there are tons of improvements that can be made.`

# Installation
First, install the requirements, the `requirements.txt` file is just an output of `pip freeze` from my test venv 'k.<br>
Second, check `config.py` and set required values (api key, device index).<br>
Next, run the `main.py` script and Voilà, as simple as that.<br><br>

And don't forget to put models of Vosk to main folder.<br>
You can get the latest from the [official website.](https://alphacephei.com/vosk/models)
<br>The one I was using is `small`.
<br>p.s. If you don't understand how to install or where to put the Vosk model, I've made a [screenshot](https://i.imgur.com/N3bu2lC.png) for you.

# Python version
I was using Python `3.10.11`, but it should work on any newer version.

# Структура проекта\

```
project/
│── main.py                     # точка входа
│── plugin_manager.py           # загрузка/выполнение плагинов
│── commands.yaml               # фразы/команды (старый список)
│
├─ core/
│  ├── __init__.py
│  ├── audio.py                 # микрофон PvRecorder и перезапуск
│  ├── wake.py                  # обёртка над Porcupine (wake-word)
│  ├── stt.py                   # распознавание речи (Vosk)
│  ├── sounds.py                # кэш звуков и проигрывание
│  └── commands_registry.py     # поиск совпадений в commands.yaml
│
├─ ai/
│  ├── __init__.py
│  ├── prompts.py               # подсказки для GPT
│  └── ai_handler.py            # решает: ответить/создать плагин
│
└─ plugins/
   ├── __init__.py
   └── legacy_commands.py       # маппинг на .exe (перенесено из execute_cmd)
```

> Комментарии на русском только там, где действительно важно для понимания.

---
# TODO:
- Использовать дипсик апи(дешевле,лучше в случаи)
- СДелать функциональные диолиги(и память)
- СДлеать сокращение памяти чтобы оставались важные детали
- Сделать создание команд самим JARVIS'OM используя любые библиотеки(импорт перед запуском),и запуск без консоли
- СДелать Jarvisa косплеером Advanced Sysstem care но лучше
- Сделать возможность редактировать характер джарвиса
- Сделать возможность узнать погоду,число,новости, и прочее без возбуждения Api
- Добавить больше дейтвий/wakeword'ов чтобы сэкономить денег с апи
- Сделать джарвиса компактнее или наоборот(таскбар,окно,или на обои)
- Улучшить визуал джарвиса
- Процедуролизировать визуал джарвиса
- Портировать джарвиса на разные ОС
- Попробовать продать джарвиса
- Сделать код чище и позвать ещё контрибюторов в команду(Open Source - сила)
- Сделать джарвиса

## Мотивация проекта сделать много functionality и сэкономить money(я всё же школьник)

# Author
TODO:написать кто сделал то 