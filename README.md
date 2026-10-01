# Эмулятор языка оболочки ОС

**Дисциплина:** Конфигурационное управление
**Группа:** ИКБО-32-25
**Вариант:** 26
**Выполнено:** Этап 1 (REPL), Этап 2 (Конфигурация), Этап 3 (VFS)

## 1. Общее описание

Эмулятор языка оболочки ОС — приложение с графическим
интерфейсом, которое имитирует работу командной строки
UNIX-подобной операционной системы.

На **этапе 1** создан минимальный прототип (REPL): диалог с
пользователем, парсер, команды-заглушки и обработка ошибок.

На **этапе 2** эмулятор стал настраиваемым: параметры
командной строки (`--vfs`, `--script`), отладочный вывод всех
заданных параметров при запуске, стартовый скрипт с
остановкой при первой ошибке.

На **этапе 3** подключена виртуальная файловая система
(VFS): директория с диска загружается **в память** при
старте, ничего на диске не изменяется. Заглушки `ls` и `cd`
замещены реальными командами, добавлены `pwd` и `cat`.

Приложение реализовано на **Python**, графический
интерфейс — **Tkinter** (входит в стандартную поставку
Python, внешних зависимостей нет).

### Что умеет прототип

- Окно-терминал: тёмная область вывода и строка ввода,
  команда выполняется по клавише `Enter`, введенная строка
  эхо-выводится, как в настоящем терминале.
- Заголовок окна формируется из **реальных данных ОС**, в
  которой исполняется эмулятор, например
  `Эмулятор - [ivanov@MIREA-PC]`.
- Простой парсер: ввод разделяется на команду и аргументы по
  пробелам (и табуляциям).
- **VFS в памяти** (этап 3): источник — директория на диске
  (`--vfs`), при запуске дерево и содержимое файлов
  копируются в память; работа с диском после загрузки не
  ведётся, данные VFS не модифицируются.
- Команды (этап 3): `ls`, `cd` — работают с VFS (заглушки
  этапа 1 заменены), `pwd` — текущая директория VFS,
  `cat` — содержимое файлов VFS.
- Приглашение ввода показывает **текущую директорию VFS**:
  `user@host:/home/user$ `.
- `exit` завершает сеанс и закрывает окно.
- Обработка ошибок (красным): неизвестная команда, неверные
  аргументы, пути VFS, которые не существуют или неверного
  типа; ошибки параметров командной строки — в консоли с
  кодом возврата 1 (этап 2).
- Конфигурация командной строки: `--vfs`, `--script`,
  `--demo` (этап 2).
- Отладочный вывод при запуске: строки `[debug] ...` со
  всеми параметрами и размером загруженной VFS (этап 2).
- Стартовый скрипт: ввод и вывод отображаются как диалог,
  исполнение **останавливается при первой ошибке** (этап 2).
- Скрипты реальной ОС: `scripts\test_config`,
  `scripts\test_errors`, `scripts\test_vfs` (`.bat` / `.sh`)
  — проверка всех параметров и вариантов VFS.

### Структура проекта

```
Conf_Atrey/
├── README.md              # этот файл
├── .gitignore
├── .gitattributes
├── Makefile               # цели run, demo, test, test-os
├── run.sh                 # запуск на Linux/macOS
├── run.bat                # запуск на Windows
├── src/
│   ├── __init__.py
│   ├── core.py            # парсер и диспетчер команд (без GUI)
│   ├── config.py          # параметры командной строки (этап 2)
│   ├── script.py          # движок стартового скрипта (этап 2)
│   ├── vfs.py             # VFS в памяти (этап 3)
│   └── main.py            # графический интерфейс (Tkinter)
├── tests/
│   ├── __init__.py
│   ├── test_parser.py     # тесты парсера
│   ├── test_core.py       # тесты команд и VFS-операций
│   ├── test_config.py     # тесты параметров командной строки
│   ├── test_script.py     # тесты стартового скрипта
│   ├── test_vfs.py        # тесты VFS в памяти (этап 3)
│   └── test_main.py       # тесты точки входа приложения
├── demo/
│   └── demo_script.txt    # стандартная демо-сессия (--demo)
├── scripts/
│   ├── test_config.bat    # все параметры, Windows (этап 2)
│   ├── test_config.sh     # все параметры, Linux/macOS (этап 2)
│   ├── test_errors.bat    # ошибки параметров, Windows (этап 2)
│   ├── test_errors.sh     # ошибки параметров, Linux/macOS
│   ├── test_vfs.bat       # варианты VFS, Windows (этап 3)
│   ├── test_vfs.sh        # варианты VFS, Linux/macOS (этап 3)
│   ├── startup_basic.txt  # стартовый скрипт: без ошибок
│   ├── startup_error.txt  # стартовый скрипт: стоп на ошибке
│   └── startup_full.txt   # все команды этапов 1-3 (этап 3)
├── vfs/                   # VFS по умолчанию (3 уровня вложенности)
│   ├── etc/hostname
│   ├── home/user/notes.txt
│   └── tmp/scratch.txt
├── vfs_sample/            # второй VFS для проверки --vfs (этап 2)
│   ├── data/readme.txt
│   └── tmp/hello.txt
├── vfs_minimal/           # минимальный VFS: один файл (этап 3)
│   └── hello.txt
├── vfs_multi/             # VFS «несколько файлов» (этап 3)
│   ├── alpha.txt
│   ├── beta.txt
│   ├── gamma.txt
│   └── logs/app.log
└── vfs_deep/              # VFS «не менее 3 уровней» (этап 3)
    ├── level1.txt
    └── l1/l2/l3/l4/deep.txt
```

Логика (парсер, команды, конфигурация, стартовый скрипт,
VFS) вынесена в `src/core.py`, `src/config.py`,
`src/script.py` и `src/vfs.py` и не зависит от Tkinter —
поэтому её полностью покрывают юнит-тесты, а графический
слой остаётся тонким.

## 2. Описание всех функций и настроек

### Команды

| Команда | Аргументы | Поведение |
| --- | --- | --- |
| `ls` | `[путь]` | список текущей (или указанной) директории VFS: поддиректории помечаются `/`, например `etc/ home/ tmp/` |
| `cd` | `[путь]` | переход в директории VFS: абсолютные и относительные пути, `..`, `.`; без аргументов — корень VFS |
| `pwd` | — | текущая директория VFS |
| `cat` | `файл [файл ...]` | содержимое одного или нескольких файлов VFS |
| `exit` | — | завершает сеанс, окно закрывается |

### Обработка ошибок

Внутри сеанса (красным в окне):

| Ситуация | Сообщение |
| --- | --- |
| неизвестная команда | `sh: foobar: command not found` |
| `exit` с аргументами | `exit: too many arguments` |
| `ls` / `cd` / `cat`: нет такого пути | `<cmd>: <путь>: no such file or directory` |
| `ls`: путь — файл | `ls: <путь>: not a directory` |
| `cd`: путь — файл | `cd: <путь>: not a directory` |
| `cat`: путь — директория | `cat: <путь>: is a directory` |
| `cat` без аргументов | `cat: missing file operand` |
| `ls` / `cd` / `pwd` с лишними аргументами | `<cmd>: too many arguments` |
| пустая строка | игнорируется, повторяется приглашение ввода |

При запуске (в консоли, код возврата 1):

| Ситуация | Сообщение |
| --- | --- |
| `--vfs` указывает на несуществующий путь | `error: VFS path does not exist: <путь>` |
| `--vfs` указывает на файл | `error: VFS path is not a directory: <путь>` |
| `--script` указывает на несуществующий файл | `error: startup script not found: <путь>` |
| `--script` указывает на директорию | `error: startup script is not a file: <путь>` |

### VFS в памяти (этап 3)

- Источник VFS — директория на диске (параметр `--vfs`,
  по умолчанию `vfs/` в корне репозитория).
- При старте дерево (директории + содержимое файлов)
  копируется **в память** (`VfsSystem`); после загрузки
  диск не читается и не изменяется: все операции выполняются
  в памяти, данные VFS не модифицируются.
- В окне при запуске выводится строка
  `[debug] vfs loaded: N files, M dirs` — размер
  загруженной VFS.
- Путь `..` выше корня оставляет в корне, как в настоящем
  shell.

Сэмплы VFS для проверки разных вариантов:

| Директория | Вариант |
| --- | --- |
| `vfs_minimal/` | минимальный: один файл |
| `vfs_multi/` | несколько файлов (+ поддиректория) |
| `vfs_deep/` | не менее 3 уровней вложенности (до 4) |
| `vfs/` | VFS по умолчанию (3 уровня) |
| `vfs_sample/` | второй VFS для проверки `--vfs` |

### Настройки (аргументы командной строки)

| Аргумент | Назначение | По умолчанию |
| --- | --- | --- |
| `--vfs PATH` | путь к физической директории VFS на диске | `vfs/` в корне репозитория |
| `--script PATH` | путь к стартовому скрипту команд эмулятора | не задан (интерактивный режим) |
| `--demo` | выполнить стандартный стартовый скрипт `demo/demo_script.txt` (демо-режим: ошибки не останавливают сессию) | не задан |

### Отладочный вывод при запуске

Непосредственно после старта все заданные параметры и
размер VFS печатаются в консоль и выводятся в окно:

```
[debug] vfs: D:\repos\Conf_Atrey\vfs
[debug] script: D:\repos\Conf_Atrey\scripts\startup_full.txt
[debug] demo: no
[debug] vfs loaded: 3 files, 5 dirs
```

Незаданный параметр отображается как `not set`.

### Стартовый скрипт

Текстовый файл, одна команда эмулятора на строку:

- пустые строки и строки, начинающиеся с `#`, пропускаются;
- на экране отображаются и ввод, и вывод — имитация диалога;
- скрипт **останавливается при первой ошибке**:
  `script stopped at line N (error)`, после чего эмулятор
  остаётся в интерактивном режиме;
- `exit` в скрипте завершает сеанс;
- нормальный завершён: `script finished: N command(s)`.

Примеры: `scripts/startup_basic.txt` (без ошибок),
`scripts/startup_error.txt` (стоп на ошибке) и
`scripts/startup_full.txt` — все команды этапов 1–3
(VFS-переходы, `cat`, и завершающая строка-ошибка, на
которой скрипт останавливается).

### Скрипты реальной ОС (тестирование)

| Скрипт | Windows | Linux/macOS | Содержимое |
| --- | --- | --- | --- |
| все параметры (этап 2) | `scripts\test_config.bat` | `scripts/test_config.sh` | запуски: без параметров, `--vfs`, `--script`, всё вместе, `--demo` |
| ошибки параметров (этап 2) | `scripts\test_errors.bat` | `scripts/test_errors.sh` | некорректные `--vfs`/`--script`, код возврата 1 |
| варианты VFS (этап 3) | `scripts\test_vfs.bat` | `scripts/test_vfs.sh` | `vfs_minimal`, `vfs_multi`, `vfs_deep`, VFS по умолчанию + `startup_full.txt`, `--vfs` + `--script` вместе, несуществующий `--vfs` |

Каждый запуск открывает окно эмулятора; закройте его
командой `exit`, чтобы скрипт перешёл к следующему
сценарию.

## 3. Команды сборки и запуска тестов

Требования: Python 3.9+ (на Linux при отсутствии Tkinter —
`sudo apt install python3-tk`); для тестов — `pytest`.
Сборка не требуется: проект интерпретируемый, артефактов
нет.

| Действие | Команда |
| --- | --- |
| запуск (интерактивно) | `./run.sh` (Linux/macOS) или `run.bat` (Windows), `make run` |
| запуск с параметрами | `python -m src.main --vfs vfs_deep --script scripts\startup_full.txt` |
| запуск (демо-режим) | `./run.sh --demo` или `make demo` |
| запуск напрямую | `python -m src.main` |
| запуск тестов | `make test` или `python -m pytest -q` |
| тесты параметров (скрипты ОС) | `scripts\test_config.bat` / `bash scripts/test_config.sh` (`make test-os`) |
| тесты вариантов VFS | `scripts\test_vfs.bat` / `bash scripts/test_vfs.sh` |

## 4. Примеры использования

### Интерактивная VFS-сессия

```
python -m src.main
```

```
[debug] vfs: D:\repos\Conf_Atrey\vfs
[debug] script: not set
[debug] demo: no
[debug] vfs loaded: 3 files, 5 dirs
user@PC:/$ ls
etc/ home/ tmp/
user@PC:/$ cd /home/user
user@PC:/home/user$ ls
notes.txt
user@PC:/home/user$ pwd
/home/user
user@PC:/home/user$ cat notes.txt
Заметки
-------
Пример файла, который эмулятор увидит в VFS на этапе 3.
user@PC:/home/user$ cd ..
user@PC:/home$ ls
user/
user@PC:/home$ cd /no_such_dir
cd: /no_such_dir: no such file or directory
user@PC:/home$
```

Промпт показывает текущую директорию VFS; ошибки — красным.

### Полный стартовый скрипт (этап 3)

```
python -m src.main --script scripts\startup_full.txt
```

Скрипт по очереди выполняет `pwd`, `ls`, `cd`, `cat` по
всем уровням VFS и заканчивается строкой `cd
/no_such_dir` — первой ошибкой, на которой останавливается:

```
user@PC:/$ pwd
/
user@PC:/$ ls
etc/ home/ tmp/
...
user@PC:/$ cd /no_such_dir
cd: /no_such_dir: no such file or directory
script stopped at line 16 (error)
user@PC:/$
```

### Варианты VFS (скрипты ОС)

```
scripts\test_vfs.bat
```

Шесть сценариев: минимальный VFS, «несколько файлов», «3+
уровней», полный стартовый скрипт на VFS по умолчанию,
комбинация `--vfs vfs_deep --script ...` и ошибка
несуществующего пути (код возврата 1).

### Ошибки параметров командной строки

```
$ python -m src.main --vfs no_such_dir
error: VFS path does not exist: no_such_dir
```

Код возврата — 1 (проверяется в `scripts\test_errors.bat` и
`scripts\test_vfs.bat`).

### Демо-режим (показ на семинаре)

```
./run.sh --demo
```

Эмулятор сам «вводит» команды из `demo/demo_script.txt`:
переходы по VFS, `cat`, неизвестную команду и `exit 1`
(красным, демо-режим не останавливается), затем `exit`
закрывает окно. Режим рассчитан на запись экрана.

## 5. Коммиты этапов

История оформлена по Conventional Commits.

### Этап 1 (REPL)

- `chore: add .gitattributes`
- `docs: add project README and launch scripts`
- `feat(repl): add GUI shell emulator prototype`
- `test: add unit tests for parser, core and CLI`

### Этап 2 (Конфигурация)

- `feat(script): add startup script engine with stop-on-error`
- `feat(config): add vfs path and startup script parameters`
- `feat(os-scripts): add real-OS scripts for testing all CLI parameters`
- `test: add unit tests for config and CLI entry point`
- `docs: update README with stage 2 configuration`

### Этап 3 (VFS)

- `feat(vfs): add in-memory virtual file system`
- `feat(vfs): implement ls, cd, pwd and cat on the VFS`
- `feat(os-scripts): add VFS variant tests and the full startup script`
- `docs: update README with stage 3 (VFS)`
