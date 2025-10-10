import json
import random
import os
import sys
import shutil
import pathlib

PLAYERS_DIR = "players"
STATE_FILE = os.path.join(PLAYERS_DIR, "state.json")
DATA_FILE = "data.json"

# допоміжні
def sanitize_filename(name):
    # просте санітизування для імен файлів
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

def ensure_players_dir():
    os.makedirs(PLAYERS_DIR, exist_ok=True)

# збереження / завантаження стану
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

# Генерація професії зі стажем
def assign_job_with_experience(jobs_pool):
    if not jobs_pool:
        return "Безробітній"
    job = jobs_pool.pop()  # Щоб не повторювались
    experience_years = random.randint(0, 5)
    if experience_years == 0:
        exp_text = "Новачок"
    elif experience_years == 1:
        exp_text = "Дилетант"
    elif experience_years == 2:
        exp_text = "Практикуючий"
    elif experience_years == 3:
        exp_text = "Досвідчений"
    elif experience_years == 4:
        exp_text = "Професіонал"
    elif experience_years == 5:
        exp_text = "Експерт"
    else:
        exp_text = f"{experience_years} років досвіду"
    return f"{exp_text} {job}"

def assign_disease_with_stage(health_pool, data, used_health):
    health_pool = data.get("health", [])
    health_with_stages = data.get("health_with_stages", {})

    # Об'єнуємо декілька словників
    all_health = (
        [h for h in health_pool if h not in used_health] +
        [d for d in health_with_stages.keys() if d not in used_health]
    )

    if not all_health:
        return "-" 

    health = random.choice(all_health)

    if health in health_with_stages:
        used_health.add(health)
        stage = random.choice(health_with_stages[health])
        return f"{health} ({stage})"
    else:
        used_health.add(health)
        return health

# генерація гравців та бункера
def generate_players(player_names, data, items_per_player=2, cards_per_player=2):
    # backpack_pool копія з data["backpack_items"]
    backpack_pool = data["backpack"].copy()
    random.shuffle(backpack_pool)

    health_pool = data.get("health").copy()
    random.shuffle(health_pool)

    jobs_pool = data.get("jobs", []).copy()
    random.shuffle(jobs_pool)

    fobias_pool = data.get("fobias", []).copy()
    random.shuffle(fobias_pool)

    hobies_pool = data.get("hobies", []).copy()
    random.shuffle(hobies_pool)

    used_health = set()
    
    cards_pool = data.get("special_cards").copy()
    random.shuffle(cards_pool)

    players = {}
    for name in player_names:
        name = name.strip()
        # призначаємо items_per_player унікальних предметів (якщо вистачає)
        items = []
        cards = []

        for _ in range(items_per_player):
            if backpack_pool:
                items.append(backpack_pool.pop())
            else:
                break

        for _ in range(cards_per_player):
            if cards_pool:
                cards.append(cards_pool.pop())
            else:
                break
        player = {
            "name": name,
            "health": assign_disease_with_stage(health_pool, data, used_health),
            "job": assign_job_with_experience(jobs_pool),
            "age": random.choice(data.get("ages", ["Невідомий"])),
            "fobias": fobias_pool.pop(),
            "hobies": hobies_pool.pop(),
            "backpack": items,
            "special_cards": cards
        }
        players[name] = player

    return players, backpack_pool, health_pool, jobs_pool, fobias_pool, hobies_pool, cards_pool

def save_player_files(players):
    ensure_players_dir()
    for player in players.values():
        fname = os.path.join(PLAYERS_DIR, f"{sanitize_filename(player['name'])}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            backpack_str = ", ".join(player['backpack']) if player['backpack'] else "—"
            special_cards_str = ", ".join(player['special_cards']) if player['special_cards'] else "—"
            fobia_level = random.randint(33, 100)
            
            f.write(f"Гравець: {player['name']}\n")
            f.write(f"Вік: {player['age']}\n")
            f.write(f"Здоров'я: {player['health']}\n")
            f.write(f"Професія: {player['job']}\n")
            f.write(f"Хобі: {player['hobies']}\n")
            f.write(f"Фобія: {player['fobias']} {fobia_level}% \n")
            f.write(f"Рюкзак: {backpack_str}\n")
            f.write(f"Спеціальні картки: {special_cards_str}\n")
            #Fix formating:


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

#інтерактивні команди
def interactive_loop(state, data):
    print("\nАдмін панель:\n")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВихід...")
            save_state(state)
            break

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        if action in ("exit", "quit"):
            save_state(state)
            print("Завершую сесію...")
            break

        if action == "help":
            print("""
Доступні команди:
  help                     — показати цю підказку
  list                     — показати всіх гравців і кількість предметів у рюкзаку
  add <name>               — додати 1 випадковий айтем у рюкзак гравця (бракує — мисливість)
  addmulti <name> N       — додати N айтемів (N число)
  regen <name>             — перегенерувати рюкзак гравця (витрачає айтеми з пулу)
  exit / quit              — зберегти та вийти
""")
            continue

        if action == "add_backpack" or action == "addmulti_backpack":
            if len(parts) < 2:
                print("Ім'я: add <name> або addmulti <name> N")
                continue
            rest = cmd[len(action):].strip()

            # підтримка імен у лапках
            if rest.startswith('"') or rest.startswith("'"):
                quote = rest[0]
                end_idx = rest.find(quote, 1)
                if end_idx == -1:
                    print("Неправильний формат імені.")
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

            if action == "add_backpack":
                count = 1
            else:
                try:
                    count = int(after.split()[0])
                except Exception:
                    print("Вкажи кількість для addmulti: addmulti <name> N")
                    continue

            added = []
            for _ in range(count):
                if not state["backpack_pool"]:
                    print("Пул вичерпано — немає більше предметів для видачі.")
                    break
                item = state["backpack_pool"].pop()
                player["backpack"].append(item)
                added.append(item)

            if added:
                if action == "add_backpack":
                    filename = f"{sanitize_filename(name)}_Предмет.txt"
                else:
                    filename = f"{sanitize_filename(name)}_{len(added)}_Предметів.txt"

                item_path = os.path.join(PLAYERS_DIR, filename)
                with open(item_path, "w", encoding="utf-8") as item_file:
                    item_file.write(f"Гравець: {name}\n")
                    item_file.write("Отримано предмети:\n")
                    for it in added:
                        item_file.write(f" - {it}\n")

                print(f"Створено файл: {filename}")
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

            player["backpack"] = []
            items_per_player = 2  # 🔹 фіксуємо 2 предмети
            added = []
            for _ in range(items_per_player):
                if not state["backpack_pool"]:
                    break
                item = state["backpack_pool"].pop()
                player["backpack"].append(item)
                added.append(item)

            # створюємо окремий файл для регенерації
            regen_filename = f"{sanitize_filename(name)}_backpack_regen.txt"
            regen_path = os.path.join(PLAYERS_DIR, regen_filename)
            with open(regen_path, "w", encoding="utf-8") as f:
                f.write(f"Гравець: {name}\n")
                f.write("Новий рюкзак:\n")
                if added:
                    for it in added:
                        f.write(f" - {it}\n")
                else:
                    f.write(" - (порожньо)\n")

            save_state(state)
            print(f"Рюкзак {name} перегенерований, створено файл {regen_filename}")
            continue

        # if action == "list":
        #     for name, p in state["players"].items():
        #         print(f"- {name}: {len(p.get('backpack', []))} предметів")
        #     continue

        # if action == "show":
        #     if len(parts) < 2:
        #         print("Вкажи ім'я: show <name>")
        #         continue
        #     name = cmd[len("show "):].strip()
        #     player = state["players"].get(name)
        #     if not player:
        #         print("Гравець не знайдений.")
        #     else:
        #         print(f"Гравець: {name}")
        #         print("Рюкзак:")
        #         if player["backpack"]:
        #             for it in player["backpack"]:
        #                 print(" -", it)
        #         else:
        #             print(" - (порожньо)")
        #     continue

        # if action == "backpack_pool":
        #     print(f"У пулі залишилось {len(state['backpack_pool'])} предметів.")
        #     continue

        # if action == "save":
        #     save_state(state)
        #     print("Saved.")
        #     continue

        print("Невідома команда. Введи 'help' для підказки.")

# стартова логіка
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
    print("Нова сесія. Введіть імена гравців через кому")
    names_input = input("> ")
    player_names = [name.strip() for name in names_input.split(",") if name.strip()]

    items_per_player = 2
    cards_per_player = 2
    # можна дати можливість ввести іншу кількість, але поки default
    players, backpack_pool, health_pool, jobs_pool, fobias_pool, hobies_pool, cards_pool = generate_players(player_names, data, items_per_player=items_per_player, cards_per_player=cards_per_player)

    # записуємо початкові файли
    save_player_files(players)
    generate_bunker(data)

    # state зберігаємо на диск
    state = {
        "players": players,   # dict name -> player
        "backpack_pool": backpack_pool,         # list доступних айтемів (використовуємо pop() з кінця)
        "health_pool": health_pool,
        "jobs_pool": jobs_pool,
        "fobias_pool": fobias_pool,
        "hobies_pool": hobies_pool,
        "cards_pool": cards_pool,
        "items_per_player": items_per_player,
        "cards_per_player": cards_per_player
    }
    save_state(state)
    print("Генерація завершена.")
    interactive_loop(state, data)

if __name__ == "__main__":
    main()
