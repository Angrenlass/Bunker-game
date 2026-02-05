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

def ensure_players_dir():
    os.makedirs(PLAYERS_DIR, exist_ok=True)

def sanitize_filename(name):
    # просте санітизування для імен файлів
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

# збереження стану
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

# Додайте ці функції після assign_job_with_experience
def parse_experience_text(years):
    """Перетворює роки досвіду в текст"""
    if years == 0:
        return "новачок"
    elif years == 1:
        return "дилетант"
    elif years == 2:
        return "практикуючий"
    elif years == 3:
        return "досвідчений"
    elif years == 4:
        return "професіонал"
    elif years == 5:
        return "експерт"
    else:
        return f"{years} років досвіду"

def parse_hobby_experience_text(years):
    """Перетворює роки досвіду хобі в текст"""
    if years == 0:
        return "початківець"
    elif years == 1:
        return "любитель"
    elif years == 2:
        return "обізнаний"
    elif years == 3:
        return "досвідчений"
    elif years == 4:
        return "майстер"
    elif years == 5:
        return "гуру"
    else:
        return f"{years} років досвіду"

def extract_job_parts(job_string):
    """Розбиває рядок професії на досвід та назву"""
    if not isinstance(job_string, str):
        return "безробітній", "Безробітній"
    
    parts = job_string.split()
    if len(parts) >= 2:
        exp = parts[0]
        name = " ".join(parts[1:])
        return exp, name
    return "новачок", job_string

def extract_hobby_parts(hobby_string):
    """Розбиває рядок хобі на назву та досвід"""
    if not isinstance(hobby_string, str):
        return "Ледащо", "без досвіду"
    
    if "(" in hobby_string and ")" in hobby_string:
        name = hobby_string.split("(")[0].strip()
        exp = hobby_string.split("(")[1].replace(")", "").strip()
        return name, exp
    return hobby_string, "без досвіду"

def assign_job_with_experience(jobs_pool, experience_years=None):
    """Генерація професії зі стажем (досвідом)"""
    if not jobs_pool:
        return "безробітній", "Безробітній"
    
    job = jobs_pool.pop()  # Щоб не повторювались
    
    if experience_years is None:
        experience_years = random.randint(0, 5)
    
    exp_text = parse_experience_text(experience_years)
    return exp_text, job

def assign_hobby_with_experience(hobies_pool, experience_years=None):
    """Генерація хобі зі стажем (досвідом)"""
    if not hobies_pool:
        return "Ледащо", "без досвіду"
    
    hobby = hobies_pool.pop()  # Щоб не повторювались
    
    if experience_years is None:
        experience_years = random.randint(0, 5)
    
    exp_text = parse_hobby_experience_text(experience_years)
    return hobby, exp_text

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

    if roll < 0.001:
        return "андроїд"

    gender = random.choice(["чоловіча", "жіноча"])
    details = []

    if random.random() < 0.10:
        details.append("безплідний" if gender == "чоловіча" else "безплідна")

    if random.random() < 0.05:
        if gender == "чоловіча":
            details.append("гей")
        else:
            details.append("лесбіянка")

    if random.random() < 0.01:
        details.append("транс")

    if details:
        return f"{gender} ({', '.join(details)})"
    else:
        return gender
    
def generate_age_and_gender(data):
    age = random.choice(data.get("ages"))
    gender = generate_gender()
    return age, gender

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
        
        # Генерація професії з досвідом
        exp_text, job = assign_job_with_experience(jobs_pool)
        
        # Генерація хобі з досвідом
        hobby, hobby_exp = assign_hobby_with_experience(hobies_pool)
        
        # Генерація фобії з відсотком
        if fobias_pool:
            fobia_name = fobias_pool.pop()
            fobia_percentage = random.randint(33, 100)
        else:
            fobia_name = "Немає"
            fobia_percentage = 50

        player = {
            "name": name,
            "health": assign_disease_with_stage(health_pool, data, used_health),
            "job": f"{exp_text} {job}",
            "age": age,
            "gender": gender,
            "body": body,
            "height": height,
            "fobias": f"{fobia_name} {fobia_percentage}%",
            "hobies": f"{hobby} ({hobby_exp})",
            "backpack": items,
            "extra_info": extra_info_pool.pop() if extra_info_pool else "Немає",
            "large_inventory": large_inventory,
            "trait": traits_pool.pop() if traits_pool else "Немає",
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

def save_single_player_file(player):
    """Зберігає файл для одного гравця"""
    ensure_players_dir()
    fname = os.path.join(PLAYERS_DIR, f"{sanitize_filename(player['name'])}.txt")
    
    # Перевіряємо формат фобії
    fobia_display = player["fobias"]
    if "%" not in player["fobias"]:
        fobia_display = f"{player['fobias']} {random.randint(33, 100)}%"
    
    with open(fname, "w", encoding="utf-8") as f:
        backpack_str = (
            "\n - " + "\n - ".join(player['backpack'])
            if player['backpack']
            else " —"
        )
        special_cards_str = (
            "\n - " + "\n - ".join(player.get('special_cards', []))
            if player.get('special_cards')
            else " —"
        )
        
        f.write(f"Гравець: {player['name']}\n")
        f.write(f"Стать: {player['gender']}, {player['age']} років\n")
        f.write(f"Статура: {player['body']}, {player['height']} см\n")
        f.write(f"Риса характеру: {player['trait']}\n")
        f.write(f"Професія: {player['job']}\n")
        f.write(f"Здоров'я: {player['health']}\n")
        f.write(f"Хобі: {player['hobies']}\n")
        f.write(f"Фобія: {fobia_display}\n")
        f.write(f"Додаткові відомості: {player['extra_info']}\n")
        f.write(f"Великий інвентар: {player['large_inventory']}\n")
        f.write(f"Рюкзак: {backpack_str}\n")
        if 'special_cards' in player:
            f.write(f"Спеціальні картки: {special_cards_str}\n")

def save_player_files(players):
    """Зберігає файли для всіх гравців"""
    for player in players.values():
        save_single_player_file(player)

def generate_bunker(data):
    ensure_players_dir()
    cataclysm = random.choice(data.get("cataclysms", ["Невідомий катаклізм"]))
    description = random.choice(data.get("descriptions", ["Опис відсутній"]))
    bunker_items = random.sample(data.get("bunker_items", []), min(3, len(data.get("bunker_items", []))))

    size = random.randint(20, 200)
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
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]
    pool = state.get(pool_name)

    if not pool:
        print(f"❌ Пул {pool_name} порожній або відсутній")
        return False

    if is_list:
        if not player.get(field):
            player[field] = []
        item = pool.pop()
        player[field].append(item)
    else:
        item = pool.pop()
        player[field] = item

    # Спеціальна обробка для фобій (додаємо відсоток)
    if field == "fobias":
        if "%" not in player[field]:
            percentage = random.randint(33, 100)
            player[field] = f"{player[field]} {percentage}%"
    
    # Спеціальна обробка для професій та хобі
    elif field == "job":
        if " " not in player[field]:
            # Додаємо досвід, якщо його немає
            exp_text = parse_experience_text(random.randint(0, 5))
            player[field] = f"{exp_text} {player[field]}"
    
    elif field == "hobies":
        if "(" not in player[field]:
            # Додаємо досвід, якщо його немає
            hobby_exp = parse_hobby_experience_text(random.randint(0, 5))
            player[field] = f"{player[field]} ({hobby_exp})"

    # Зберігаємо стан та оновлюємо файл
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ {field} для {name} оновлено")
    return True

def reroll_health(state, data, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]
    used = set()
    player["health"] = assign_disease_with_stage(state["health_pool"], data, used)
    
    # Зберігаємо стан та оновлюємо файл
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Здоров'я для {name} оновлено")
    return True

def reroll_body(state, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]

    if not state["body_pool"]:
        print(f"❌ Пул статури порожній")
        return False

    body = state["body_pool"].pop()
    height = random.randint(140, 200)
    player["body"] = body
    player["height"] = height
    
    # Зберігаємо стан та оновлюємо файл
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Статура та зріст для {name} оновлені")
    return True

def add_backpack_items(state, name, count=1):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]
    added = []

    for _ in range(count):
        if not state["backpack_pool"]:
            break
        item = state["backpack_pool"].pop()
        if "backpack" not in player or not player["backpack"]:
            player["backpack"] = []
        player["backpack"].append(item)
        added.append(item)

    save_state(state)
    save_single_player_file(player)

    if added:
        print(f"✅ Додано {len(added)} предметів у рюкзак для {name}")
    else:
        print(f"❌ Нічого не додано — пул порожній")
    return bool(added)

def regen_backpack(state, name):
    """Очищає та перегенерує рюкзак"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]

    # очищаємо рюкзак
    player["backpack"] = []

    # генеруємо нові предмети
    new_items = []
    for _ in range(state.get("items_per_player", 2)):
        if state["backpack_pool"]:
            item = state["backpack_pool"].pop()
            player["backpack"].append(item)
            new_items.append(item)

    save_state(state)
    save_single_player_file(player)

    if not new_items:
        print(f"❌ Нічого не додано — пул порожній")
        return False
    else:
        print(f"✅ Рюкзак для {name} очищено та перегенеровано ({len(new_items)} предметів)")
        return True

def reroll_large_inventory(state, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]

    if not state["large_inventory_pool"]:
        print(f"❌ Пул великого інвентаря порожній")
        return False

    item = state["large_inventory_pool"].pop()
    player["large_inventory"] = item
    
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Великий інвентар для {name} оновлено")
    return True

def reroll_age_and_gender(state, data, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]

    # генеруємо нові значення
    age = random.choice(data.get("ages", [18]))
    gender = generate_gender()

    # оновлюємо стан
    player["age"] = age
    player["gender"] = gender
    
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Вік та стать для {name} оновлені")
    return True

def reroll_age(state, data, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]
    age = random.choice(data.get("ages", [18]))
    player["age"] = age
    
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Вік для {name} оновлено")
    return True

def reroll_gender(state, name):
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False

    player = state["players"][player_key]
    gender = generate_gender()
    player["gender"] = gender
    
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Стать для {name} оновлено")
    return True

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

def regen_all_players(state, data, field):
    """Перегенеровує обрану характеристику всім гравцям"""
    updated_count = 0
    
    for player_name, player in state["players"].items():
        if field == "fobia":
            # Генерація фобії з відсотком
            if state["fobias_pool"]:
                new_fobia = state["fobias_pool"].pop()
                percentage = random.randint(33, 100)
                player["fobias"] = f"{new_fobia} {percentage}%"
                updated_count += 1
        
        elif field == "hobby":
            # Генерація хобі з досвідом
            if state["hobies_pool"]:
                hobby, exp = assign_hobby_with_experience(state["hobies_pool"])
                player["hobies"] = f"{hobby} ({exp})"
                updated_count += 1
        
        elif field == "health":
            # Генерація здоров'я
            if state["health_pool"]:
                used = set()
                player["health"] = assign_disease_with_stage(state["health_pool"], data, used)
                updated_count += 1
        
        elif field == "age":
            # Генерація віку
            player["age"] = random.choice(data.get("ages", [25]))
            updated_count += 1
        
        elif field == "gender":
            # Генерація статі
            player["gender"] = generate_gender()
            updated_count += 1
        
        elif field == "body":
            # Генерація статури та зросту
            if state["body_pool"]:
                player["body"] = state["body_pool"].pop()
                player["height"] = random.randint(140, 200)
                updated_count += 1
        
        elif field == "height":
            # Генерація тільки зросту
            player["height"] = random.randint(140, 200)
            updated_count += 1
        
        elif field == "backpack":
            # Перегенерація рюкзака
            player["backpack"] = []
            items_added = 0
            for _ in range(state.get("items_per_player", 2)):
                if state["backpack_pool"]:
                    player["backpack"].append(state["backpack_pool"].pop())
                    items_added += 1
            if items_added > 0:
                updated_count += 1
        
        elif field == "extra_info":
            # Генерація додаткової інформації
            if state["extra_info_pool"]:
                player["extra_info"] = state["extra_info_pool"].pop()
                updated_count += 1
        
        elif field == "large_inventory":
            # Генерація великого інвентаря
            if state["large_inventory_pool"]:
                player["large_inventory"] = state["large_inventory_pool"].pop()
                updated_count += 1
        
        elif field == "trait":
            # Генерація риси характеру
            if state["traits_pool"]:
                player["trait"] = state["traits_pool"].pop()
                updated_count += 1
        
        elif field == "job":
            # Генерація професії з досвідом
            if state["jobs_pool"]:
                exp, job = assign_job_with_experience(state["jobs_pool"])
                player["job"] = f"{exp} {job}"
                updated_count += 1
    
    # Зберігаємо стан та оновлюємо файли для всіх гравців
    save_state(state)
    for player in state["players"].values():
        save_single_player_file(player)
    
    # Повертаємо тільки кількість оновлених гравців, без деталей
    print(f"✅ {field} перегенеровано для {updated_count} гравців")
    return updated_count

def regen_player_completely(state, data, name):
    """Повністю перегенеровує картку гравця"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return None
    
    # Отримуємо пули зі стану
    backpack_pool = state.get("backpack_pool", []).copy()
    body_pool = state.get("body_pool", []).copy()
    traits_pool = state.get("traits_pool", []).copy()
    extra_info_pool = state.get("extra_info_pool", []).copy()
    large_inventory_pool = state.get("large_inventory_pool", []).copy()
    health_pool = state.get("health_pool", []).copy()
    jobs_pool = state.get("jobs_pool", []).copy()
    fobias_pool = state.get("fobias_pool", []).copy()
    hobies_pool = state.get("hobies_pool", []).copy()
    
    # Перемішуємо пули
    random.shuffle(backpack_pool)
    random.shuffle(body_pool)
    random.shuffle(traits_pool)
    random.shuffle(extra_info_pool)
    random.shuffle(large_inventory_pool)
    random.shuffle(health_pool)
    random.shuffle(jobs_pool)
    random.shuffle(fobias_pool)
    random.shuffle(hobies_pool)
    
    used_health = set()
    
    # Генеруємо нові характеристики
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
    
    # Рюкзак
    items = []
    for _ in range(state["items_per_player"]):
        if backpack_pool:
            items.append(backpack_pool.pop())
    
    # Оновлюємо гравця
    player = state["players"][player_key]
    player.update({
        "health": assign_disease_with_stage(health_pool, data, used_health),
        "job": f"{assign_job_with_experience(jobs_pool)[0]} {assign_job_with_experience(jobs_pool)[1]}",
        "age": age,
        "gender": gender,
        "body": body,
        "height": height,
        "fobias": f"{fobias_pool.pop() if fobias_pool else 'Немає'} {random.randint(33, 100)}%",
        "hobies": f"{assign_hobby_with_experience(hobies_pool)[0]} ({assign_hobby_with_experience(hobies_pool)[1]})",
        "backpack": items,
        "extra_info": extra_info_pool.pop() if extra_info_pool else "Немає",
        "large_inventory": large_inventory,
        "trait": traits_pool.pop() if traits_pool else "Немає"
    })
    
    # Оновлюємо пули в стані
    state["backpack_pool"] = backpack_pool
    state["body_pool"] = body_pool
    state["traits_pool"] = traits_pool
    state["extra_info_pool"] = extra_info_pool
    state["large_inventory_pool"] = large_inventory_pool
    state["health_pool"] = health_pool
    state["jobs_pool"] = jobs_pool
    state["fobias_pool"] = fobias_pool
    state["hobies_pool"] = hobies_pool
    
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Гравець {name} повністю перегенерований")
    return player

def regen_job_only(state, name):
    """Регенерує тільки професію, зберігаючи досвід"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    # Отримуємо поточний досвід
    current_exp, _ = extract_job_parts(player["job"])
    
    # Генеруємо нову професію з тим же досвідом
    if state["jobs_pool"]:
        job = state["jobs_pool"].pop()
        player["job"] = f"{current_exp} {job}"
        save_state(state)
        save_single_player_file(player)
        return True
    
    return False

def regen_job_experience(state, name):
    """Регенерує тільки досвід професії"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    # Отримуємо поточну професію
    _, current_job = extract_job_parts(player["job"])
    
    # Генеруємо новий досвід
    new_experience_years = random.randint(0, 5)
    new_exp_text = parse_experience_text(new_experience_years)
    
    player["job"] = f"{new_exp_text} {current_job}"
    save_state(state)
    save_single_player_file(player)
    return True

def regen_job_and_experience(state, name):
    """Регенерує професію та досвід разом"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    if state["jobs_pool"]:
        exp, job = assign_job_with_experience(state["jobs_pool"])
        player["job"] = f"{exp} {job}"
        save_state(state)
        save_single_player_file(player)
        return True
    
    return False

def regen_hobby_only(state, name):
    """Регенерує тільки хобі, зберігаючи досвід"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    # Отримуємо поточний досвід
    _, current_exp = extract_hobby_parts(player["hobies"])
    
    # Генеруємо нове хобі з тим же досвідом
    if state["hobies_pool"]:
        hobby = state["hobies_pool"].pop()
        player["hobies"] = f"{hobby} ({current_exp})"
        save_state(state)
        save_single_player_file(player)
        return True
    
    return False

def regen_hobby_experience(state, name):
    """Регенерує тільки досвід хобі"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    # Отримуємо поточне хобі
    current_hobby, _ = extract_hobby_parts(player["hobies"])
    
    # Генеруємо новий досвід
    new_experience_years = random.randint(0, 5)
    new_exp_text = parse_hobby_experience_text(new_experience_years)
    
    player["hobies"] = f"{current_hobby} ({new_exp_text})"
    save_state(state)
    save_single_player_file(player)
    return True

def regen_hobby_and_experience(state, name):
    """Регенерує хобі та досвід разом"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    if state["hobies_pool"]:
        hobby, exp = assign_hobby_with_experience(state["hobies_pool"])
        player["hobies"] = f"{hobby} ({exp})"
        save_state(state)
        save_single_player_file(player)
        return True
    
    return False

def regen_fobia_only(state, name):
    """Регенерує тільки фобію, зберігаючи відсоток"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    # Отримуємо поточний відсоток
    current_percentage = player["fobias"].split()[-1] if "%" in player["fobias"] else "50%"
    
    # Генеруємо нову фобію з тим же відсотком
    if state["fobias_pool"]:
        fobia = state["fobias_pool"].pop()
        player["fobias"] = f"{fobia} {current_percentage}"
        save_state(state)
        save_single_player_file(player)
        return True
    
    return False

def regen_fobia_percentage(state, name):
    """Регенерує тільки відсоток фобії"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    # Отримуємо поточну фобію
    fobia_name = " ".join(player["fobias"].split()[:-1]) if "%" in player["fobias"] else player["fobias"]
    
    # Генеруємо новий відсоток
    new_percentage = random.randint(33, 100)
    
    player["fobias"] = f"{fobia_name} {new_percentage}%"
    save_state(state)
    save_single_player_file(player)
    return True

def regen_fobia_and_percentage(state, name):
    """Регенерує фобію та відсоток разом"""
    player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
    if not player_key:
        return False
    
    player = state["players"][player_key]
    
    if state["fobias_pool"]:
        fobia = state["fobias_pool"].pop()
        percentage = random.randint(33, 100)
        player["fobias"] = f"{fobia} {percentage}%"
        save_state(state)
        save_single_player_file(player)
        return True
    
    return False

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

def interactive_loop(state, data):
    print("\nАдмін панель (help — список команд)\n")

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
Стандартні команди:
health <name> - перегенерувати здоров'я
body <name> - перегенерувати статуру та зріст
trait <name> - перегенерувати рису характеру
hobby <name> - перегенерувати хобі (з досвідом)
fobia <name> - перегенерувати фобію (з відсотком)
extra <name> - перегенерувати додаткові відомості
job <name> - перегенерувати професію (з досвідом)
large <name> - перегенерувати великий інвентар
agegender <name> - перегенерувати вік та стать
age <name> - перегенерувати вік
gender <name> - перегенерувати стать
add backpack <name> [N] - додати N предметів у рюкзак
regen backpack <name> - перегенерувати рюкзак
regen bunker - перегенерувати бункер
regen cataclysm - перегенерувати катаклізм

Нові команди:
regen_all <field> - перегенерувати поле всім гравцям
  Поля: fobia, hobby, health, age, gender, body, height, backpack, extra_info, large_inventory, trait, job
regen <name> all - повністю перегенерувати гравця

Команди для професії:
job_only <name> - тільки професія (досвід залишається)
job_exp <name> - тільки досвід професії
job_full <name> - професія та досвід

Команди для хобі:
hobby_only <name> - тільки хобі (досвід залишається)
hobby_exp <name> - тільки досвід хобі
hobby_full <name> - хобі та досвід

Команди для фобії:
fobia_only <name> - тільки фобія (відсоток залишається)
fobia_percent <name> - тільки відсоток фобії
fobia_full <name> - фобія та відсоток

exit - вийти
""")
            continue
        # --- універсальна команда для всіх гравців ---
        if action == "regen_all" and len(parts) >= 2:
            field = parts[1].lower()
            valid_fields = ["fobia", "hobby", "health", "age", "gender", "body", "height", 
                          "backpack", "extra_info", "large_inventory", "trait", "job"]
            
            if field in valid_fields:
                regen_all_players(state, data, field)  # Більше не виводимо деталі
            else:
                print(f"❌ Невірне поле. Доступні: {', '.join(valid_fields)}")
            continue

        # --- повна перегенерація гравця ---
        if action == "regen" and len(parts) >= 3 and parts[2].lower() == "all":
            name = parts[1]
            player = regen_player_completely(state, data, name)
            # Повідомлення вже виводиться в самій функції
            continue

        # --- команди для професії ---
        if action == "job_only" and len(parts) >= 2:
            name = parts[1]
            if regen_job_only(state, name):
                print(f"✅ Професія для {name} перегенерована (досвід залишений)")
            else:
                print(f"❌ Помилка при регенерації професії для {name}")
            continue

        if action == "job_exp" and len(parts) >= 2:
            name = parts[1]
            if regen_job_experience(state, name):
                print(f"✅ Досвід професії для {name} перегенерований")
            else:
                print(f"❌ Помилка при регенерації досвіду для {name}")
            continue

        if action == "job_full" and len(parts) >= 2:
            name = parts[1]
            if regen_job_and_experience(state, name):
                print(f"✅ Професія та досвід для {name} перегенеровані")
            else:
                print(f"❌ Помилка при регенерації професії та досвіду для {name}")
            continue

        # --- команди для хобі ---
        if action == "hobby_only" and len(parts) >= 2:
            name = parts[1]
            if regen_hobby_only(state, name):
                print(f"✅ Хобі для {name} перегенероване (досвід залишений)")
            else:
                print(f"❌ Помилка при регенерації хобі для {name}")
            continue

        if action == "hobby_exp" and len(parts) >= 2:
            name = parts[1]
            if regen_hobby_experience(state, name):
                print(f"✅ Досвід хобі для {name} перегенерований")
            else:
                print(f"❌ Помилка при регенерації досвіду хобі для {name}")
            continue

        if action == "hobby_full" and len(parts) >= 2:
            name = parts[1]
            if regen_hobby_and_experience(state, name):
                print(f"✅ Хобі та досвід для {name} перегенеровані")
            else:
                print(f"❌ Помилка при регенерації хобі та досвіду для {name}")
            continue

        # --- команди для фобії ---
        if action == "fobia_only" and len(parts) >= 2:
            name = parts[1]
            if regen_fobia_only(state, name):
                print(f"✅ Фобія для {name} перегенерована (відсоток залишений)")
            else:
                print(f"❌ Помилка при регенерації фобії для {name}")
            continue

        if action == "fobia_percent" and len(parts) >= 2:
            name = parts[1]
            if regen_fobia_percentage(state, name):
                print(f"✅ Відсоток фобії для {name} перегенерований")
            else:
                print(f"❌ Помилка при регенерації відсотка фобії для {name}")
            continue

        if action == "fobia_full" and len(parts) >= 2:
            name = parts[1]
            if regen_fobia_and_percentage(state, name):
                print(f"✅ Фобія та відсоток для {name} перегенеровані")
            else:
                print(f"❌ Помилка при регенерації фобії та відсотка для {name}")
            continue

        # --- стандартні команди (ПОТРІБНО ВИПРАВИТИ!) ---
        
        # Перевіряємо, чи команда потребує імені гравця
        commands_requiring_name = ["health", "body", "trait", "hobby", "fobia", "extra", 
                                 "job", "large", "agegender", "age", "gender", 
                                 "add", "regen"]
        
        if action in commands_requiring_name:
            if len(parts) < 2:
                print(f"❌ Потрібно вказати ім'я гравця. Наприклад: {action} <ім'я>")
                continue
            
            name = parts[1]  # Тепер ця змінна доступна в цій області
        
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

        elif action == "agegender":
            reroll_age_and_gender(state, data, name)

        elif action == "age":
            reroll_age(state, data, name)

        elif action == "gender":
            reroll_gender(state, name)

        elif action == "add" and len(parts) >= 3 and parts[1] == "backpack":
            name = parts[2]
            count = int(parts[3]) if len(parts) > 3 else 1
            add_backpack_items(state, name, count)

        elif action == "regen" and len(parts) >= 3 and parts[1] == "backpack":
            name = parts[2]
            regen_backpack(state, name)

        elif action == "regen" and parts[1] == "bunker":
            regen_bunker(data)

        elif action == "regen" and parts[1] == "cataclysm":
            regen_cataclysm(data)

        else:
            print("❓ Невідома команда")

def main():
    if not os.path.exists(DATA_FILE):
        print(f"Не знайдено {DATA_FILE}. Створи data.json")
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
