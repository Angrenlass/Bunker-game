import json
import random
import os
import sys
import shutil
import pathlib

PLAYERS_DIR = "players"
STATE_FILE = os.path.join(PLAYERS_DIR, "state.json")
DATA_FILE = "data.json"

# ---- допоміжні ----
def sanitize_filename(name):
    # просте санітизування для імен файлів
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

def ensure_players_dir():
    os.makedirs(PLAYERS_DIR, exist_ok=True)

# ---- збереження / завантаження стану ----
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    ensure_players_dir()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# ---- генерація гравців та бункера ----
def generate_players(player_names, data, items_per_player=2):
    # pool копія з data["backpack_items"]
    pool = data["backpack"].copy()
    random.shuffle(pool)

    players = {}
    for name in player_names:
        name = name.strip()
        # призначаємо items_per_player унікальних предметів (якщо вистачає)
        items = []
        for _ in range(items_per_player):
            if pool:
                items.append(pool.pop())
            else:
                break
        player = {
            "name": name,
            "health": random.choice(data.get("health", ["Здоровий"])),
            "profession": (data.get("professions", []) or ["Без професії"]).pop() if data.get("professions") else "Без професії",
            "age": random.choice(data.get("ages", ["Невідомий"])),
            "backpack": items
        }
        players[name] = player

    return players, pool

def save_player_files(players):
    ensure_players_dir()
    for player in players.values():
        fname = os.path.join(PLAYERS_DIR, f"{sanitize_filename(player['name'])}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"Гравець: {player['name']}\n")
            f.write(f"Вік: {player['age']}\n")
            f.write(f"Здоров'я: {player['health']}\n")
            f.write(f"Професія: {player['profession']}\n")
            f.write("Рюкзак:\n")
            if player["backpack"]:
                for it in player["backpack"]:
                    f.write(f" - {it}\n")
            else:
                f.write(" - (порожньо)\n")

def generate_bunker(data):
    ensure_players_dir()
    cataclysm = random.choice(data.get("cataclysms", ["Невідомий катаклізм"]))
    description = random.choice(data.get("descriptions", ["Опис відсутній"]))
    bunker_items = random.sample(data.get("bunker_items", []), min(3, len(data.get("bunker_items", []))))
    size = random.randint(50, 500)
    time = random.randint(6, 36)
    food = random.randint(3, 24)
    water = random.randint(3, 24)
    bunker_file = os.path.join(PLAYERS_DIR, "bunker.txt")
    with open(bunker_file, "w", encoding="utf-8") as f:
        f.write(f"Катаклізм: {cataclysm}\n")
        f.write(f"Опис бункера: {description}\n")
        f.write(f"Інвентар бункера: {', '.join(bunker_items)}\n")
        f.write(f"Розмір: {size} м²\n")
        f.write(f"Час перебування: {time} місяців\n")
        f.write(f"Їжа: вистачить на {food} місяців\n")
        f.write(f"Вода: вистачить на {water} місяців\n")

# ---- інтерактивні команди ----
def interactive_loop(state, data):
    """
    state structure:
    {
      "players": { name: player_dict, ... },
      "pool": [items...]
    }
    """
    print("\nІнтерактивний режим. Введи 'help' для списку команд.\n")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            save_state(state)
            break

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        if action in ("exit", "quit"):
            save_state(state)
            print("Збережено стан. Пока!")
            break

        if action == "help":
            print("""
Доступні команди:
  help                     — показати цю підказку
  list                     — показати всіх гравців і кількість предметів у рюкзаку
  show <name>              — показати вміст рюкзака конкретного гравця
  add <name>               — додати 1 випадковий айтем у рюкзак гравця (бракує — мисливість)
  addmulti <name> N       — додати N айтемів (N число)
  pool                     — показати кількість доступних айтемів у пулі
  save                     — вручну зберегти state
  regen <name>             — перегенерувати рюкзак гравця (витрачає айтеми з пулу)
  help-commands            — показати короткий опис команд з прикладами
  exit / quit              — зберегти та вийти
""")
            continue

        if action == "help-commands":
            print("""
Приклади:
  add Лєра
  addmulti "Микола" 2
  show "Іван Петренко"
  regen "Лєра"      # очистити рюкзак Лєри і заново роздати items_per_player предметів
""")
            continue

        if action == "list":
            for name, p in state["players"].items():
                print(f"- {name}: {len(p.get('backpack', []))} предметів")
            continue

        if action == "show":
            if len(parts) < 2:
                print("Вкажи ім'я: show <name>")
                continue
            name = cmd[len("show "):].strip()
            player = state["players"].get(name)
            if not player:
                print("Гравець не знайдений.")
            else:
                print(f"Гравець: {name}")
                print("Рюкзак:")
                if player["backpack"]:
                    for it in player["backpack"]:
                        print(" -", it)
                else:
                    print(" - (порожньо)")
            continue

        if action == "pool":
            print(f"У пулі залишилось {len(state['pool'])} предметів.")
            continue

        if action == "save":
            save_state(state)
            print("Saved.")
            continue

        if action == "add" or action == "addmulti":
            if len(parts) < 2:
                print("Вкажи ім'я: add <name> або addmulti <name> N")
                continue
            # витягуємо імя з повного рядка
            rest = cmd[len(action):].strip()
            # support quotes
            if rest.startswith('"') or rest.startswith("'"):
                # знайти закриваючу кавичку
                quote = rest[0]
                end_idx = rest.find(quote, 1)
                if end_idx == -1:
                    print("Невірний формат імені.")
                    continue
                name = rest[1:end_idx]
                after = rest[end_idx+1:].strip()
            else:
                tokens = rest.split()
                name = tokens[0]
                after = " ".join(tokens[1:]).strip()

            player = state["players"].get(name)
            if not player:
                print("Гравця з таким іменем немає.")
                continue

            if action == "add":
                count = 1
            else:
                # addmulti
                try:
                    count = int(after.split()[0])
                except Exception:
                    print("Вкажи кількість для addmulti: addmulti <name> N")
                    continue

            added = []
            for _ in range(count):
                if not state["pool"]:
                    print("Пул вичерпано — немає більше предметів для видачі.")
                    break
                item = state["pool"].pop()
                player["backpack"].append(item)
                added.append(item)

            if added:
                print(f"Додано до {name}:")
                for it in added:
                    print(" -", it)
                # оновити файл гравця
                fname = os.path.join(PLAYERS_DIR, f"{sanitize_filename(name)}.txt")
                with open(fname, "a", encoding="utf-8") as f:
                    for it in added:
                        f.write(f" - {it}\n")
                save_state(state)
            continue

        if action == "regen":
            if len(parts) < 2:
                print("Вкажи ім'я: regen <name>")
                continue
            name = cmd[len("regen "):].strip()
            player = state["players"].get(name)
            if not player:
                print("Гравця з таким іменем немає.")
                continue
            # повернемо старі предмети в pool? НІ — ми їх просто знищуємо (щоб уникнути дублювання логіки).
            # Якщо хочеш — можна змінити, щоб вони повертались.
            player["backpack"] = []
            # беремо items_per_player з поточного state або default 3
            items_per_player = state.get("items_per_player", 2)
            added = []
            for _ in range(items_per_player):
                if not state["pool"]:
                    break
                item = state["pool"].pop()
                player["backpack"].append(item)
                added.append(item)
            # перезапис файлу
            fname = os.path.join(PLAYERS_DIR, f"{sanitize_filename(name)}.txt")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(f"Гравець: {player['name']}\n")
                f.write(f"Вік: {player['age']}\n")
                f.write(f"Здоров'я: {player['health']}\n")
                f.write(f"Професія: {player['profession']}\n")
                f.write("Рюкзак:\n")
                if player["backpack"]:
                    for it in player["backpack"]:
                        f.write(f" - {it}\n")
                else:
                    f.write(" - (порожньо)\n")
            save_state(state)
            print(f"Рюкзак {name} перегенерований, додано {len(added)} предметів.")
            continue

        print("Невідома команда. Введи 'help' для підказки.")
    # кінець loop

# ---- стартова логіка ----
def main():
    if not os.path.exists(DATA_FILE):
        print(f"Не знайдено {DATA_FILE}. Створи файл з даними (backpack_items тощо).")
        sys.exit(1)

    data = load_data()

    # якщо є збережений state — пропонуємо відновити
    state = load_state()
    if state:
        print("Знайдено попередній стан гри.")
        answer = input("Завантажити попередній стан? (Y/n) > ").strip().lower()
        if answer in ("", "y", "yes"):
            print("Завантажую стан...")
            interactive_loop(state, data)
            return

    # інакше — нова генерація
    print("Нова сесія. Введіть імена гравців через кому (наприклад: Лєра, Макс, Нікіта):")
    names_input = input("> ")
    player_names = [name.strip() for name in names_input.split(",") if name.strip()]

    items_per_player = 2
    # можна дати можливість ввести іншу кількість, але поки default
    players, pool = generate_players(player_names, data, items_per_player=items_per_player)

    # записуємо початкові файли
    save_player_files(players)
    generate_bunker(data)

    # state зберігаємо на диск
    state = {
        "players": players,   # dict name -> player
        "pool": pool,         # list доступних айтемів (використовуємо pop() з кінця)
        "items_per_player": items_per_player
    }
    save_state(state)
    print("Генерація завершена. Файли у папці 'players'. Сесія починається.")
    interactive_loop(state, data)

if __name__ == "__main__":
    main()
