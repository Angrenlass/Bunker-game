import json
import random
import os
import sys
import re
import shutil
import pathlib

PLAYERS_DIR = "players"
STATE_FILE = os.path.join(PLAYERS_DIR, "state.json")
DATA_FILE = "data.json"

# допоміжні
def ensure_players_dir():
    os.makedirs(PLAYERS_DIR, exist_ok=True)

def sanitize_filename(name):
    # просте санітизування для імен файлів
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

def write_player_action(name: str, action: str, lines: list[str]):
    ensure_players_dir()
    filename = f"{sanitize_filename(name)}_{action}.txt"
    path = os.path.join(PLAYERS_DIR, filename)

    with open(path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

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
def assign_hobby_with_experience(hobies_pool):
    if not hobies_pool:
        return "Ледащо"
    hobby = hobies_pool.pop()  # Щоб не повторювались
    experience_years = random.randint(0, 5)
    if experience_years == 0:
        exp_text = "початківець"
    elif experience_years == 1:
        exp_text = "любитель"
    elif experience_years == 2:
        exp_text = "обізнаний"
    elif experience_years == 3:
        exp_text = "досвідчений"
    elif experience_years == 4:
        exp_text = "майстер"
    elif experience_years == 5:
        exp_text = "гуру"
    else:
        exp_text = f"{experience_years} років досвіду"
    return f"{hobby} ({exp_text})"

# Генерація професії зі стажем
def assign_job_with_experience(jobs_pool):
    if not jobs_pool:
        return "Безробітній"
    job = jobs_pool.pop()  # Щоб не повторювались
    experience_years = random.randint(0, 5)
    if experience_years == 0:
        exp_text = "новачок"
    elif experience_years == 1:
        exp_text = "дилетант"
    elif experience_years == 2:
        exp_text = "практикуючий"
    elif experience_years == 3:
        exp_text = "досвідчений"
    elif experience_years == 4:
        exp_text = "професіонал"
    elif experience_years == 5:
        exp_text = "експерт"
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
    

def generate_gender():
    roll = random.random()  # 0.0 - 1.0

    # 0.1% шанс на андроїда
    if roll < 0.001:
        return "андроїд"

    # базова стать
    gender = random.choice(["чоловіча", "жіноча"])
    details = []

    # 10% шанс на безплідність
    if random.random() < 0.10:
        details.append("безплідний" if gender == "чоловіча" else "безплідна")

    # 5% шанс на сексуальну орієнтацію
    if random.random() < 0.05:
        if gender == "чоловіча":
            details.append("гей")
        else:
            details.append("лесбіянка")

    # 1% шанс на транс
    if random.random() < 0.01:
        details.append("транс")

    # збираємо результат
    if details:
        return f"{gender} ({', '.join(details)})"
    else:
        return gender
    
def generate_age_and_gender(data):
    age = random.choice(data.get("ages"))
    gender = generate_gender()
    return age, gender

# генерація гравців та бункера
def generate_players(player_names, data, items_per_player=2, cards_per_player=2):
    # backpack_pool копія з data["backpack_items"]
    backpack_pool = data["backpack"].copy()
    random.shuffle(backpack_pool)

    body_pool = data.get("body_types", []).copy()
    random.shuffle(body_pool)

    traits_pool = data.get("traits", []).copy()
    random.shuffle(traits_pool)

    extra_info_pool = data.get("extra_info", []).copy()
    random.shuffle(extra_info_pool)

    large_inventory_pool = data.get("large_inventory", []).copy()
    random.shuffle(large_inventory_pool)

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

        height = random.randint(140, 200)
        age, gender = generate_age_and_gender(data)

        if body_pool:
            body = body_pool.pop()
        else:
            body = "Невідомо"

        if large_inventory_pool:
            large_inventory = large_inventory_pool.pop()
        else:
            large_inventory = "Відсутній"

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
            "age": age,
            "gender": gender,
            "body": body,
            "height": height,
            "fobias": fobias_pool.pop(),
            "hobies": assign_hobby_with_experience(hobies_pool),
            "backpack": items,
            "extra_info": extra_info_pool.pop(),
            "large_inventory": large_inventory,
            "trait": traits_pool.pop(),
            "special_cards": cards
        }
        players[name] = player

    return players, body_pool, traits_pool, jobs_pool, health_pool, hobies_pool, fobias_pool, extra_info_pool, large_inventory_pool, backpack_pool, cards_pool

def save_player_files(players):
    ensure_players_dir()
    for player in players.values():
        fname = os.path.join(PLAYERS_DIR, f"{sanitize_filename(player['name'])}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            backpack_str = (
                "\n - " + "\n - ".join(player['backpack'])
                if player['backpack']
                else " —"
            )
            special_cards_str = (
                "\n - " + "\n - ".join(player['special_cards'])
                if player['special_cards']
                else " —"
                )
            fobia_level = random.randint(33, 100)
            
            f.write(f"Гравець: {player['name']}\n")
            f.write(f"Стать: {player['gender']}, {player['age']} років\n")
            f.write(f"Статура: {player['body']}, {player['height']} см\n")
            f.write(f"Риса характеру: {player['trait']}\n")
            f.write(f"Професія: {player['job']}\n")
            f.write(f"Здоров'я: {player['health']}\n")
            f.write(f"Хобі: {player['hobies']}\n")
            f.write(f"Фобія: {player['fobias']} {fobia_level}% \n")
            f.write(f"Додаткові відомості: {player['extra_info']}\n")
            f.write(f"Великий інвентар: {player['large_inventory']}\n")
            f.write(f"Рюкзак: {backpack_str}\n")
            f.write(f"Спеціальні картки: {special_cards_str}\n")

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

def reroll_player_field(state, name, field, pool_name, *, is_list=False):
    # робимо іменя регістр-незалежним
    player_key = None
    for k in state["players"].keys():
        if k.lower() == name.lower():
            player_key = k
            break

    if not player_key:
        write_player_action(name, field, ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]
    pool = state.get(pool_name)

    if not pool:
        write_player_action(player_key, field, [f"❌ Пул {pool_name} порожній або відсутній"])
        return

    if is_list:
        player[field] = []
        item = pool.pop()
        player[field].append(item)
        lines = [f"{field} оновлено:", f" - {item}"]
    else:
        item = pool.pop()
        player[field] = item
        lines = [f"{field} оновлено:", f" - {item}"]

    save_state(state)
    write_player_action(player_key, field, lines)

def reroll_health(state, data, name):
    # регістр-незалежне ім'я
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        write_player_action(name, "health", ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]
    used = set()
    player["health"] = assign_disease_with_stage(state["health_pool"], data, used)
    save_state(state)
    write_player_action(player_key, "health", [f"Нове здоровʼя: {player['health']}"])

def reroll_body(state, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        write_player_action(name, "body", ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]

    if not state["body_pool"]:
        write_player_action(player_key, "body", ["❌ body_pool порожній"])
        return

    body = state["body_pool"].pop()
    height = random.randint(140, 200)
    player["body"] = body
    player["height"] = height
    save_state(state)
    write_player_action(player_key, "body", [f"Статура: {body}", f"Зріст: {height} см"])

def add_backpack_items(state, name, count=1):
    player = state["players"].get(name)
    if not player:
        write_player_action(name, "backpack_add", ["❌ Гравця не знайдено"])
        return

    added = []

    for _ in range(count):
        if not state["backpack_pool"]:
            break
        item = state["backpack_pool"].pop()
        player["backpack"].append(item)
        added.append(item)

    save_state(state)

    if added:
        write_player_action(
            name,
            "backpack_add",
            [f"Додано предмети: {', '.join(added)}"]
        )
    else:
        write_player_action(
            name,
            "backpack_add",
            ["❌ Нічого не додано — пул порожній"]
        )

def regen_backpack(state, name):
    """Очищає та перегенерує рюкзак, записує один файл із усіма предметами"""
    # знайти гравця регістр-незалежно
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        write_player_action(name, "backpack_regen", ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]

    # очищаємо рюкзак
    player["backpack"] = []

    # генеруємо нові предмети
    new_items = []
    for _ in range(state["items_per_player"]):
        if state["backpack_pool"]:
            item = state["backpack_pool"].pop()
            player["backpack"].append(item)
            new_items.append(item)

    save_state(state)

    # формуємо один лог
    if not new_items:
        lines = ["❌ Нічого не додано — пул порожній"]
    else:
        lines = ["🎒 Рюкзак очищено та перегенеровано:"]
        for item in new_items:
            lines.append(f" - {item}")

    write_player_action(player_key, "backpack_regen", lines)


def reroll_large_inventory(state, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        write_player_action(name, "large_inventory", ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]

    if not state["large_inventory_pool"]:
        write_player_action(player_key, "large_inventory", ["❌ Пул порожній"])
        return

    item = state["large_inventory_pool"].pop()
    player["large_inventory"] = item
    save_state(state)
    write_player_action(player_key, "large_inventory", [f"Великий інвентар: {item}"])

def reroll_age_and_gender(state, data, name):
    # знайти гравця регістр-незалежно
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        write_player_action(name, "rand_age_gender", ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]

    # генеруємо нові значення
    age = random.choice(data.get("ages", [18]))
    gender = generate_gender()

    # оновлюємо стан
    player["age"] = age
    player["gender"] = gender
    save_state(state)

    # записуємо лог
    write_player_action(player_key, "rand_age_gender", [
        f"🎲 Новий вік: {age} років",
        f"🎲 Нова стать: {gender}"
    ])

def reroll_age(state, data, name):
    # знайти гравця регістр-незалежно
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        write_player_action(name, "rand_age", ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]
    age = random.choice(data.get("ages", [18]))
    player["age"] = age
    save_state(state)
    write_player_action(player_key, "rand_age", [f"🎲 Новий вік: {age} років"])


def reroll_gender(state, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        write_player_action(name, "rand_gender", ["❌ Гравця не знайдено"])
        return

    player = state["players"][player_key]
    gender = generate_gender()
    player["gender"] = gender
    save_state(state)
    write_player_action(player_key, "rand_gender", [f"🎲 Нова стать: {gender}"])

def read_bunker():
    path = os.path.join(PLAYERS_DIR, "bunker.txt")
    if not os.path.exists(path):
        return None

    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
    return data

def regen_bunker(data):
    b = read_bunker()
    if not b:
        print("❌ Бункер не знайдено")
        return

    b["Опис бункера"] = random.choice(data.get("descriptions", ["Опис відсутній"]))
    b["Інвентар бункера"] = ", ".join(
        random.sample(
            data.get("bunker_items", []),
            min(3, len(data.get("bunker_items", [])))
        )
    )
    b["Розмір"] = f"{random.randint(50, 500)} м²"
    b["Час перебування"] = f"{random.randint(6, 36)} місяців"
    b["Їжа"] = f"вистачить на {random.randint(3, 24)} місяців"
    b["Вода"] = f"вистачить на {random.randint(3, 24)} місяців"

    write_bunker(b)

def regen_cataclysm(data):
    b = read_bunker()
    if not b:
        print("❌ Бункер не знайдено")
        return

    b["Катаклізм"] = random.choice(
        data.get("cataclysms", ["Невідомий катаклізм"])
    )

    write_bunker(b)

def write_bunker(b):
    path = os.path.join(PLAYERS_DIR, "bunker.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Катаклізм: {b['Катаклізм']}\n")
        f.write(f"Опис бункера: {b['Опис бункера']}\n")
        f.write(f"Інвентар бункера: {b['Інвентар бункера']}\n")
        f.write(f"Розмір: {b['Розмір']}\n")
        f.write(f"Час перебування: {b['Час перебування']}\n")
        f.write(f"Їжа: {b['Їжа']}\n")
        f.write(f"Вода: {b['Вода']}\n")

def write_player_log(name, lines):
    ensure_players_dir()
    path = os.path.join(PLAYERS_DIR, f"{sanitize_filename(name)}_log.txt")
    with open(path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def interactive_loop(state, data):
    print("\n🛠 Адмін панель (help — список команд)\n")

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            save_state(state)
            break

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        if action in ("exit", "quit"):
            save_state(state)
            break

        if action == "help":
            print("""
health <name>
body <name>
trait <name>
hobby <name>
fobia <name>
extra <name>
job <name>
large <name>

add backpack <name> [N]
regen backpack <name>

bunker
exit
""")
            continue

        # --- гравець ---
        if len(parts) >= 2:
            name = parts[-1]

        if action == "health":
            reroll_health(state, data, name)

        elif action == "body":
            reroll_body(state, name)

        elif action == "trait":
            reroll_player_field(state, name, "trait", "traits_pool")

        elif action == "hobby":
            reroll_player_field(state, name, "hobies", "hobies_pool")

        elif action == "fobia":
            reroll_player_field(state, name, "fobias", "fobias_pool")

        elif action == "extra":
            reroll_player_field(state, name, "extra_info", "extra_info_pool")

        elif action == "job":
            reroll_player_field(state, name, "job", "jobs_pool")

        elif action == "large":
            reroll_large_inventory(state, name)

        elif action == "add" and parts[1] == "backpack":
            name = parts[2]
            count = int(parts[3]) if len(parts) > 3 else 1
            add_backpack_items(state, name, count)

        elif action == "regen" and parts[1] == "backpack":
            regen_backpack(state, name)

        elif action == "agegender":
            reroll_age_and_gender(state, data, name)

        elif action == "age":
            reroll_age(state, data, name)

        elif action == "gender":
            reroll_gender(state, name)

        elif action == "regen" and parts[1] == "bunker":
            regen_bunker(data)

        elif action == "regen" and parts[1] == "cataclysm":
            regen_cataclysm(data)

        else:
            print("❓ Невідома команда")

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
    players, body_pool, traits_pool, jobs_pool, health_pool, hobies_pool, fobias_pool, extra_info_pool, large_inventory_pool, backpack_pool, cards_pool = generate_players(player_names, data, items_per_player=items_per_player, cards_per_player=cards_per_player)

    # записуємо початкові файли
    save_player_files(players)
    generate_bunker(data)

    # state зберігаємо на диск
    state = {
        "players": players,   # dict name -> player
        "body_pool": body_pool,
        "traits_pool": traits_pool,
        "jobs_pool": jobs_pool,
        "health_pool": health_pool,
        "hobies_pool": hobies_pool,         # list доступних айтемів (використовуємо pop() з кінця)
        "fobias_pool": fobias_pool,
        "large_inventory_pool": large_inventory_pool,
        "backpack_pool": backpack_pool,
        "extra_info_pool": extra_info_pool,
        "cards_pool": cards_pool,
        "items_per_player": items_per_player,
        "cards_per_player": cards_per_player
    }
    save_state(state)
    print("Генерація завершена.")
    interactive_loop(state, data)

if __name__ == "__main__":
    main()
