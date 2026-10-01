# Эмулятор языка оболочки ОС

**Дисциплина:** Конфигурационное управление
**Группа:** ИКБО-32-25
**Вариант:** 26
**Выполнено:** Этап 1 (REPL), Этап 2 (Конфигурация), Этап 3 (VFS), Этап 4 (Основные команды), Этап 5 (Дополнительные команды)

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

На **этапе 4** команды `ls` и `cd` доведены до вида UNIX
`ls`/`cd`: у `ls` появились опции `-a` (скрытые файлы) и
`-l` (развёрнутый вид: права, размер), у `cd` — режим `cd -`
(возврат в предыдущую директорию). Добавлены команды `cal`
(календарь месяца) и `date` (текущие дата и время, формат
после `+`).

На **этапе 5** VFS стала изменяемой (только в памяти):
добавлены команды `touch` (создание пустых файлов), `chmod`
(смена бита выполнения, `+x`/`-x`) и `vfs-load` (загрузка
новой VFS с диска во время сеанса).

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
- Команды (этапы 3–5): `ls` — со списком директории,
  опциями `-a` (скрытые файлы) и `-l` (права, размер),
  `cd` — переходы и `cd -` (предыдущая директория), `pwd` —
  текущая директория VFS, `cat` — содержимое файлов VFS,
  `cal` — календарь месяца (0/1/2 аргумента), `date` — дата
  и время, формат после `+`, `touch` — создание пустых
  файлов, `chmod` — смена бита выполнения (`+x`/`-x`),
  `vfs-load` — загрузка новой VFS с диска во время сеанса.
- **Изменение VFS только в памяти** (этап 5): `touch`/
  `chmod` изменяют дерево и права в памяти, на диск данные
  не записываются; `vfs-load` заменяет VFS другой,
  загруженной с диска.
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
│   ├── commands.py        # команды cal и date (этап 4)
│   ├── config.py          # параметры командной строки (этап 2)
│   ├── result.py          # результат выполнения команды (этап 4)
│   ├── script.py          # движок стартового скрипта (этап 2)
│   ├── vfs.py             # VFS в памяти (этап 3)
│   └── main.py            # графический интерфейс (Tkinter)
├── tests/
│   ├── __init__.py
│   ├── test_parser.py     # тесты парсера
│   ├── test_core.py       # тесты команд и VFS-операций
│   ├── test_commands.py   # тесты cal и date (этап 4)
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
│   ├── test_stage4.bat    # команды этапа 4, Windows
│   ├── test_stage4.sh     # команды этапа 4, Linux/macOS
│   ├── startup_basic.txt  # стартовый скрипт: без ошибок
│   ├── startup_error.txt  # стартовый скрипт: стоп на ошибке
│   ├── startup_full.txt   # все команды этапов 1-3 (этап 3)
│   ├── startup_stage4.txt # все режимы команд этапа 4
│   ├── test_stage5.bat    # команды этапа 5, Windows
│   ├── test_stage5.sh     # команды этапа 5, Linux/macOS
│   └── startup_stage5.txt # все режимы команд этапа 5
├── vfs/                   # VFS по умолчанию (3 уровня вложенности)
│   ├── .profile           # скрытый файл (для ls -a, этап 4)
│   ├── etc/hostname
│   ├── home/user/notes.txt
│   ├── home/user/.bashrc  # скрытый файл (для ls -a, этап 4)
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
    ├── etc/hostname       # + layout, совпадающий с vfs/ (этап 4)
    ├── home/user/notes.txt
    ├── home/user/.bashrc
    ├── level1.txt
    ├── l1/l2/l3/l4/deep.txt
    └── tmp/scratch.txt
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
| `ls` | `[-a] [-l] [путь]` | список текущей (или указанной) директории VFS: поддиректории помечаются `/`, например `etc/ home/ tmp/`. Опции комбинируются (`-la`, `-al`). `-a` — показать скрытые (dot-)файлы; `-l` — развёрнутый вид: строка на запись `drwxr-xr-x     -  etc` / `-rw-r--r--     9  hostname` (права, размер в байтах, имя) |
| `cd` | `[путь \| -]` | переход в директории VFS: абсолютные и относительные пути, `..`, `.`; без аргументов — корень VFS; `cd -` — предыдущая директория (печатает новый путь) |
| `pwd` | — | текущая директория VFS |
| `cat` | `файл [файл ...]` | содержимое одного или нескольких файлов VFS |
| `cal` | `[месяц] [год]` | календарь месяца: без аргументов — текущий месяц, 1 аргумент — месяц текущего года, 2 — месяц и год; сетка недель по 7 дней, воскресенье — первый день |
| `date` | `["+ФОРМАТ"]` | текущие дата и время в формате UNIX (`Thu Oct 01 12:00:00 2026`); после `+` — формат `strftime` (например `date +%Y-%m-%d`) |
| `touch` | `файл [файл ...]` | создать пустой файл в VFS (только в памяти); существующие файлы и директории не меняются (как в UNIX); путь — относительно текущей директории |
| `chmod` | `+x\|-x файл [...]` | выставить/снять бит выполнения у файла или директории VFS (упрощённые символьные режимы); результат виден в `ls -l` |
| `vfs-load` | `путь` | загрузить новую VFS с диска (путь к физической директории) и заменить текущую; текущая директория сбрасывается в корень; вывод `vfs loaded: N files, M dirs from <путь>` |
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
| `ls` с неизвестной опцией | `ls: invalid option -- 'x'` |
| `cd -` без предыдущей директории | `cd: no previous directory` |
| `cal`: месяц не число или вне 1–12 | `cal: invalid month: 13` |
| `cal`: год не число или 0 | `cal: invalid year: 0` |
| `cal` / `date` с лишними аргументами | `<cmd>: too many arguments` |
| `date` с аргументом без `+` | `date: invalid format: Y` |
| `touch` без аргументов | `touch: missing file operand` |
| `touch`: родительской директории нет | `touch: <путь>: no such file or directory` |
| `chmod` без режима или без файлов | `chmod: missing operand` |
| `chmod`: неподдерживаемый режим | `chmod: invalid mode: '7z'` |
| `chmod`: нет такого пути | `chmod: <путь>: no such file or directory` |
| `vfs-load` без аргументов / с лишними | `vfs-load: missing operand` / `vfs-load: too many arguments` |
| `vfs-load`: нет такого пути | `vfs-load: <путь>: no such file or directory` |
| `vfs-load`: путь — файл | `vfs-load: <путь>: not a directory` |
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
- Изменения VFS (этап 5) происходят **только в памяти**:
  `touch` создаёт пустые файлы, `chmod` меняет строку прав
  (её показывает `ls -l`), `vfs-load` заменяет VFS другой,
  загруженной с диска; файлы на диске ни при загрузке, ни
  при изменениях не затрагиваются.

Сэмплы VFS для проверки разных вариантов:

| Директория | Вариант |
| --- | --- |
| `vfs_minimal/` | минимальный: один файл |
| `vfs_multi/` | несколько файлов (+ поддиректория) |
| `vfs_deep/` | не менее 3 уровней вложенности (до 4) + `etc`/`home`/`tmp` как в `vfs/` (этап 4) |
| `vfs/` | VFS по умолчанию (3 уровня, со скрытыми файлами для `ls -a`) |
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
[debug] vfs loaded: 5 files, 5 dirs
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
`scripts/startup_error.txt` (стоп на ошибке),
`scripts/startup_full.txt` — все команды этапов 1–3
(VFS-переходы, `cat`, и завершающая строка-ошибка, на
которой скрипт останавливается),
`scripts/startup_stage4.txt` — все режимы команд этапа 4
(`cal` 0/1/2 аргумента, `date` + формат, `ls`/`ls -a`/
`ls -l`/`ls -la`, `cd /`, `cd -`, и завершающая
строка-ошибка `cal 13`),
`scripts/startup_stage5.txt` — все режимы команд этапа 5
(`touch` нового/существующего файла и директории,
`chmod +x`/`-x` с выводом `ls -l`, `vfs-load` на
`vfs_multi` и обратно, и завершающая строка-ошибка
`touch /no_such_dir/file`).

### Скрипты реальной ОС (тестирование)

| Скрипт | Windows | Linux/macOS | Содержимое |
| --- | --- | --- | --- |
| все параметры (этап 2) | `scripts\test_config.bat` | `scripts/test_config.sh` | запуски: без параметров, `--vfs`, `--script`, всё вместе, `--demo` |
| ошибки параметров (этап 2) | `scripts\test_errors.bat` | `scripts/test_errors.sh` | некорректные `--vfs`/`--script`, код возврата 1 |
| варианты VFS (этап 3) | `scripts\test_vfs.bat` | `scripts/test_vfs.sh` | `vfs_minimal`, `vfs_multi`, `vfs_deep`, VFS по умолчанию + `startup_full.txt`, `--vfs` + `--script` вместе, несуществующий `--vfs` |
| команды этапа 4 | `scripts\test_stage4.bat` | `scripts/test_stage4.sh` | интерактивный запуск, `startup_stage4.txt` на VFS по умолчанию и на `vfs_deep` |
| команды этапа 5 | `scripts\test_stage5.bat` | `scripts/test_stage5.sh` | интерактивный запуск, `startup_stage5.txt` на VFS по умолчанию и на `vfs_deep` |

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
| тесты команд этапа 4 | `scripts\test_stage4.bat` / `bash scripts/test_stage4.sh` |
| тесты команд этапа 5 | `scripts\test_stage5.bat` / `bash scripts/test_stage5.sh` |

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
script stopped at line 19 (error)
user@PC:/$
```

### Основные команды этапа 4 (стартовый скрипт)

```
python -m src.main --script scripts\startup_stage4.txt
```

Скрипт последовательно выполняет `cal` (без аргументов,
месяц, месяц + год), `date` (по умолчанию и `+%Y-%m-%d`),
`ls`, `ls -a`, `ls -l`, `ls -la /etc`, `cd /home/user`,
`cd -`, `pwd`, `cd /etc`, `ls -l` и завершается строкой
`cal 13` — первой ошибкой, на которой останавливается:

```
user@PC:/$ cal
    October 2026
Su Mo Tu We Th Fr Sa
 4           1  2  3
11  5  6  7  8  9 10
18 12 13 14 15 16 17
25 19 20 21 22 23 24
   26 27 28 29 30 31
user@PC:/$ date
Thu Oct 01 11:06:22 2026
user@PC:/$ ls -la /etc
-rw-r--r--     9  hostname
user@PC:/$ cd /home/user
user@PC:/home/user$ cd -
/
user@PC:/$ cal 13
cal: invalid month: 13
script stopped at line 19 (error)
user@PC:/$
```

`ls -a` дополнительно показывает скрытые файлы
(`.profile`, `.bashrc`), а `ls -l` — права и размер файла в
байтах.

### Дополнительные команды этапа 5 (стартовый скрипт)

```
python -m src.main --script scripts\startup_stage5.txt
```

Скрипт создаёт файл `touch` (и повторяет `touch` для
существующего файла и директории), переключает бит
выполнения через `chmod +x`/`-x` (промежуточный вывод
`ls -l`), загружает `vfs_multi` и `vfs/` через `vfs-load` и
заканчивается строкой `touch /no_such_dir/file` — первой
ошибкой, на которой останавливается:

```
user@PC:/$ touch newfile.txt
user@PC:/$ ls
etc/ home/ newfile.txt tmp/
user@PC:/$ chmod +x newfile.txt
user@PC:/$ ls -l
drwxr-xr-x     -  etc
-rwxr--r--     0  newfile.txt
...
user@PC:/$ vfs-load vfs_multi
vfs loaded: 4 files, 2 dirs from vfs_multi
user@PC:/$ ls
alpha.txt beta.txt gamma.txt logs/
user@PC:/$ vfs-load vfs
vfs loaded: 5 files, 5 dirs from vfs
user@PC:/$ touch /no_such_dir/file
touch: /no_such_dir/file: no such file or directory
script stopped at line 18 (error)
user@PC:/$
```

Все изменения (`touch`, `chmod`) сохраняются **только в
памяти**; `chmod +x` меняет строку прав на `-rwxr--r--`, что
видно в `ls -l`.

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
переходы по VFS, `cat`, `ls -a`/`ls -l`, `cal`, `date`
с форматом, `touch`, `chmod +x` (с выводом `ls -l`),
`vfs-load vfs_sample`, неизвестную команду и `exit 1`
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

### Этап 4 (Основные команды)

- `feat(commands): add cal and date commands`
- `feat(vfs): add ls -a/-l flags, hidden files and cd - mode`
- `feat(os-scripts): add stage 4 startup and test scripts`
- `docs: update README with stage 4 commands`

### Этап 5 (Дополнительные команды)

- `feat(vfs): add touch, chmod and vfs-load commands`
- `feat(os-scripts): add stage 5 startup and test scripts`
- `docs: update README with stage 5 commands`
