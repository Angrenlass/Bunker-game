import json
import random
import os
import sys
from typing import Dict, List, Tuple, Optional, Set

PLAYERS_DIR = "players"
STATE_FILE = os.path.join(PLAYERS_DIR, "state.json")
DATA_FILE = "data.json"

# ================ УТИЛІТИ ================

def ensure_players_dir() -> None:
    """Створює директорію для гравців якщо не існує."""
    os.makedirs(PLAYERS_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    """Очищає рядок для використання як ім'я файлу."""
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

def load_json_file(filepath: str) -> dict:
    """Завантажує JSON файл."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_file(filepath: str, data: dict) -> None:
    """Зберігає дані у JSON файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data() -> dict:
    """Завантажує основні дані з data.json."""
    return load_json_file(DATA_FILE)

def save_state(state: dict) -> None:
    """Зберігає стан гри."""
    ensure_players_dir()
    save_json_file(STATE_FILE, state)

def load_state() -> Optional[dict]:
    """Завантажує збережений стан гри."""
    if os.path.exists(STATE_FILE):
        return load_json_file(STATE_FILE)
    return None

# ================ ФОРМАТУВАННЯ ================

EXPERIENCE_MAPPING = {
    0: "новачок",
    1: "дилетант",
    2: "практикуючий",
    3: "досвідчений",
    4: "професіонал",
    5: "експерт"
}

HOBBY_EXPERIENCE_MAPPING = {
    0: "початківець",
    1: "любитель",
    2: "обізнаний",
    3: "досвідчений",
    4: "майстер",
    5: "гуру"
}

def parse_experience_text(years: int) -> str:
    """Перетворює роки досвіду в текст."""
    return EXPERIENCE_MAPPING.get(years, f"{years} років досвіду")

def parse_hobby_experience_text(years: int) -> str:
    """Перетворює роки досвіду хобі в текст."""
    return HOBBY_EXPERIENCE_MAPPING.get(years, f"{years} років досвіду")

def extract_job_parts(job_string: str) -> Tuple[str, str]:
    """Розбиває рядок професії на досвід та назву."""
    if not isinstance(job_string, str):
        return "безробітній", "Безробітній"
    
    parts = job_string.split()
    if len(parts) >= 2:
        exp = parts[0]
        name = " ".join(parts[1:])
        return exp, name
    return "новачок", job_string

def extract_hobby_parts(hobby_string: str) -> Tuple[str, str]:
    """Розбиває рядок хобі на назву та досвід."""
    if not isinstance(hobby_string, str):
        return "Ледащо", "без досвіду"
    
    if "(" in hobby_string and ")" in hobby_string:
        name = hobby_string.split("(")[0].strip()
        exp = hobby_string.split("(")[1].replace(")", "").strip()
        return name, exp
    return hobby_string, "без досвіду"

def extract_fobia_parts(fobia_string: str) -> Tuple[str, str]:
    """Розбиває рядок фобії на назву та відсоток."""
    if not isinstance(fobia_string, str):
        return "Немає", "50%"
    
    if "%" in fobia_string:
        parts = fobia_string.rsplit(" ", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
    return fobia_string, "50%"

# ================ ГЕНЕРАЦІЯ ================

class PoolManager:
    """Менеджер для роботи з пулами даних."""
    
    def __init__(self, data: dict):
        self.pools = {}
        self._initialize_pools(data)
    
    def _initialize_pools(self, data: dict) -> None:
        """Ініціалізує пули даних."""
        pool_names = [
            "backpack", "body", "traits", "extra_info",
            "large_inventory", "health", "jobs", "fobias",
            "hobies", "special_cards"
        ]
        
        for name in pool_names:
            pool_data = data.get(name, [])
            if isinstance(pool_data, list):
                self.pools[name] = pool_data.copy()
                random.shuffle(self.pools[name])
            elif isinstance(pool_data, dict):
                self.pools[name] = list(pool_data.keys())
                random.shuffle(self.pools[name])
            else:
                self.pools[name] = []
        
        # Спеціальний пул для здоров'я зі стадіями
        self.health_with_stages = data.get("health_with_stages", {})
    
    def get_pool(self, name: str) -> List:
        """Повертає копію пулу."""
        return self.pools.get(name, []).copy()
    
    def pop_from_pool(self, pool_name: str, default=None):
        """Бере елемент з пулу."""
        pool = self.pools.get(pool_name, [])
        if pool:
            return pool.pop()
        return default
    
    def add_to_pool(self, pool_name: str, item) -> None:
        """Додає елемент до пулу."""
        if pool_name not in self.pools:
            self.pools[pool_name] = []
        self.pools[pool_name].append(item)
    
    def shuffle_pool(self, pool_name: str) -> None:
        """Перемішує пул."""
        if pool_name in self.pools:
            random.shuffle(self.pools[pool_name])

def generate_gender() -> str:
    """Генерує стать з додатковими характеристиками."""
    roll = random.random()
    
    if roll < 0.001:
        return "андроїд"
    
    gender = random.choice(["чоловіча", "жіноча"])
    details = []
    
    if random.random() < 0.10:
        details.append("безплідний" if gender == "чоловіча" else "безплідна")
    
    if random.random() < 0.05:
        details.append("гей" if gender == "чоловіча" else "лесбіянка")
    
    if random.random() < 0.01:
        details.append("транс")
    
    if details:
        return f"{gender} ({', '.join(details)})"
    return gender

def assign_job_with_experience(jobs_pool: List[str], experience_years: Optional[int] = None) -> Tuple[str, str]:
    """Генерує професію зі стажем."""
    if not jobs_pool:
        return "безробітній", "Безробітній"
    
    job = jobs_pool.pop()
    if experience_years is None:
        experience_years = random.randint(0, 5)
    
    exp_text = parse_experience_text(experience_years)
    return exp_text, job

def assign_hobby_with_experience(hobbies_pool: List[str], experience_years: Optional[int] = None) -> Tuple[str, str]:
    """Генерує хобі зі стажем."""
    if not hobbies_pool:
        return "Ледащо", "без досвіду"
    
    hobby = hobbies_pool.pop()
    if experience_years is None:
        experience_years = random.randint(0, 5)
    
    exp_text = parse_hobby_experience_text(experience_years)
    return hobby, exp_text

def assign_disease_with_stage(pool_manager: PoolManager, used_health: Set[str]) -> str:
    """Призначає захворювання зі стадією."""
    # Отримуємо всі доступні захворювання
    health_pool = pool_manager.get_pool("health")
    health_with_stages = pool_manager.health_with_stages
    
    all_health = (
        [h for h in health_pool if h not in used_health] +
        [d for d in health_with_stages.keys() if d not in used_health]
    )
    
    if not all_health:
        return "-"
    
    health = random.choice(all_health)
    used_health.add(health)
    
    if health in health_with_stages:
        stage = random.choice(health_with_stages[health])
        return f"{health} ({stage})"
    
    return health

def generate_player(name: str, pool_manager: PoolManager, items_per_player: int = 2, cards_per_player: int = 2) -> dict:
    """Генерує дані одного гравця."""
    used_health = set()
    
    # Основні характеристики
    height = random.randint(140, 200)
    age = random.choice(pool_manager.pools.get("ages", [25]))
    gender = generate_gender()
    
    # Генерація спискових даних
    items = [pool_manager.pop_from_pool("backpack") for _ in range(items_per_player)]
    items = [item for item in items if item is not None]
    
    cards = [pool_manager.pop_from_pool("special_cards") for _ in range(cards_per_player)]
    cards = [card for card in cards if card is not None]
    
    # Професія та хобі
    exp_text, job = assign_job_with_experience(pool_manager.pools.get("jobs", []))
    hobby, hobby_exp = assign_hobby_with_experience(pool_manager.pools.get("hobies", []))
    
    # Фобія з відсотком
    fobia_name = pool_manager.pop_from_pool("fobias", "Немає")
    fobia_percentage = random.randint(33, 100)
    
    player = {
        "name": name,
        "health": assign_disease_with_stage(pool_manager, used_health),
        "job": f"{exp_text} {job}",
        "age": age,
        "gender": gender,
        "body": pool_manager.pop_from_pool("body", "Невідомо"),
        "height": height,
        "fobias": f"{fobia_name} {fobia_percentage}%",
        "hobies": f"{hobby} ({hobby_exp})",
        "backpack": items,
        "extra_info": pool_manager.pop_from_pool("extra_info", "Немає"),
        "large_inventory": pool_manager.pop_from_pool("large_inventory", "Відсутній"),
        "trait": pool_manager.pop_from_pool("traits", "Немає"),
        "special_cards": cards
    }
    
    return player

def generate_players(player_names: List[str], data: dict, items_per_player: int = 2, cards_per_player: int = 2) -> Tuple[dict, PoolManager]:
    """Генерує дані всіх гравців."""
    pool_manager = PoolManager(data)
    pool_manager.pools["ages"] = data.get("ages", [25]).copy()
    
    players = {}
    for name in player_names:
        name = name.strip()
        player = generate_player(name, pool_manager, items_per_player, cards_per_player)
        players[name] = player
    
    return players, pool_manager

# ================ ЗБЕРЕЖЕННЯ ФАЙЛІВ ================

def save_player_files(players: Dict[str, dict]) -> None:
    """Зберігає файли для всіх гравців."""
    ensure_players_dir()
    for player in players.values():
        save_single_player_file(player)

def save_single_player_file(player: dict) -> None:
    """Зберігає файл для одного гравця."""
    ensure_players_dir()
    fname = os.path.join(PLAYERS_DIR, f"{sanitize_filename(player['name'])}.txt")
    
    # Форматування фобії
    fobia_display = player["fobias"]
    if "%" not in player["fobias"]:
        fobia_display = f"{player['fobias']} {random.randint(33, 100)}%"
    
    # Форматування списків
    backpack_str = format_list(player.get('backpack', []))
    special_cards_str = format_list(player.get('special_cards', []))
    
    with open(fname, "w", encoding="utf-8") as f:
        lines = [
            f"Гравець: {player['name']}",
            f"Стать: {player['gender']}, {player['age']} років",
            f"Статура: {player['body']}, {player['height']} см",
            f"Риса характеру: {player['trait']}",
            f"Професія: {player['job']}",
            f"Здоров'я: {player['health']}",
            f"Хобі: {player['hobies']}",
            f"Фобія: {fobia_display}",
            f"Додаткові відомості: {player['extra_info']}",
            f"Великий інвентар: {player['large_inventory']}",
            f"Рюкзак: {backpack_str}",
        ]
        
        if player.get('special_cards'):
            lines.append(f"Спеціальні картки: {special_cards_str}")
        
        f.write("\n".join(lines))

def format_list(items: List[str]) -> str:
    """Форматує список для виводу."""
    if not items:
        return " —"
    return "\n - " + "\n - ".join(items)

# ================ БУНКЕР ================

def generate_bunker(data: dict) -> None:
    """Генерує файл бункера."""
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

def read_bunker() -> Optional[Dict[str, str]]:
    """Читає дані бункера."""
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

def write_bunker(bunker_data: Dict[str, str]) -> None:
    """Записує дані бункера."""
    path = os.path.join(PLAYERS_DIR, "bunker.txt")
    with open(path, "w", encoding="utf-8") as f:
        for key, value in bunker_data.items():
            f.write(f"{key}: {value}\n")

def regen_bunker(data: dict) -> None:
    """Перегенерує бункер."""
    bunker = read_bunker()
    if not bunker:
        print("❌ Бункер не знайдено")
        return
    
    bunker["Опис бункера"] = random.choice(data.get("descriptions", ["Опис відсутній"]))
    bunker["Інвентар бункера"] = ", ".join(
        random.sample(
            data.get("bunker_items", []),
            min(3, len(data.get("bunker_items", [])))
        )
    )
    bunker["Розмір"] = f"{random.randint(50, 500)} м²"
    bunker["Час перебування"] = f"{random.randint(6, 36)} місяців"
    bunker["Їжа"] = f"вистачить на {random.randint(3, 24)} місяців"
    bunker["Вода"] = f"вистачить на {random.randint(3, 24)} місяців"
    
    write_bunker(bunker)
    print("✅ Бункер перегенеровано")

def regen_cataclysm(data: dict) -> None:
    """Перегенерує катаклізм."""
    bunker = read_bunker()
    if not bunker:
        print("❌ Бункер не знайдено")
        return
    
    bunker["Катаклізм"] = random.choice(data.get("cataclysms", ["Невідомий катаклізм"]))
    write_bunker(bunker)
    print("✅ Катаклізм перегенеровано")

# ================ ОПЕРАЦІЇ З ГРАВЦЯМИ ================

class PlayerOperations:
    """Клас для операцій з гравцями."""
    
    @staticmethod
    def find_player(state: dict, name: str) -> Tuple[Optional[str], Optional[dict]]:
        """Знаходить гравця за ім'ям (регістронезалежно)."""
        player_key = next((k for k in state["players"] if k.lower() == name.lower()), None)
        if player_key:
            return player_key, state["players"][player_key]
        return None, None
    
    @staticmethod
    def update_and_save(state: dict, player: dict, name: str) -> None:
        """Зберігає стан та файл гравця."""
        save_state(state)
        save_single_player_file(player)
        print(f"✅ {name} оновлено")
    
    @staticmethod
    def reroll_field(state: dict, name: str, field: str, pool_name: str, is_list: bool = False, 
                    format_func: Optional[callable] = None) -> bool:
        """Універсальна функція для перегенерації поля."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        pool = state.get(pool_name, [])
        if not pool:
            print(f"❌ Пул {pool_name} порожній")
            return False
        
        if is_list:
            if field not in player or not isinstance(player[field], list):
                player[field] = []
            player[field].append(pool.pop())
        else:
            player[field] = pool.pop()
            
            # Спеціальне форматування для деяких полів
            if field == "fobias" and "%" not in player[field]:
                player[field] = f"{player[field]} {random.randint(33, 100)}%"
            elif field == "job" and " " not in player[field]:
                exp_text = parse_experience_text(random.randint(0, 5))
                player[field] = f"{exp_text} {player[field]}"
            elif field == "hobies" and "(" not in player[field]:
                hobby_exp = parse_hobby_experience_text(random.randint(0, 5))
                player[field] = f"{player[field]} ({hobby_exp})"
        
        if format_func:
            format_func(player, field)
        
        PlayerOperations.update_and_save(state, player, f"{field} для {name}")
        return True
    
    @staticmethod
    def reroll_health(state: dict, data: dict, name: str) -> bool:
        """Перегенерує здоров'я."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        # Імітуємо PoolManager для цієї операції
        used_health = set()
        health_pool = state.get("health_pool", []).copy()
        health_with_stages = data.get("health_with_stages", {})
        
        all_health = (
            [h for h in health_pool if h not in used_health] +
            [d for d in health_with_stages.keys() if d not in used_health]
        )
        
        if not all_health:
            player["health"] = "-"
        else:
            health = random.choice(all_health)
            if health in health_with_stages:
                stage = random.choice(health_with_stages[health])
                player["health"] = f"{health} ({stage})"
            else:
                player["health"] = health
        
        PlayerOperations.update_and_save(state, player, f"Здоров'я для {name}")
        return True
    
    @staticmethod
    def reroll_body(state: dict, name: str) -> bool:
        """Перегенерує статуру та зріст."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        body_pool = state.get("body_pool", [])
        if not body_pool:
            print("❌ Пул статури порожній")
            return False
        
        player["body"] = random.choice(body_pool)
        player["height"] = random.randint(140, 200)
        
        PlayerOperations.update_and_save(state, player, f"Статуру та зріст для {name}")
        return True
    
    @staticmethod
    def reroll_age_and_gender(state: dict, data: dict, name: str) -> bool:
        """Перегенерує вік та стать."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        player["age"] = random.choice(data.get("ages", [18]))
        player["gender"] = generate_gender()
        
        PlayerOperations.update_and_save(state, player, f"Вік та стать для {name}")
        return True
    
    @staticmethod
    def reroll_age(state: dict, data: dict, name: str) -> bool:
        """Перегенерує вік."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        player["age"] = random.choice(data.get("ages", [18]))
        
        PlayerOperations.update_and_save(state, player, f"Вік для {name}")
        return True
    
    @staticmethod
    def reroll_gender(state: dict, name: str) -> bool:
        """Перегенерує стать."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        player["gender"] = generate_gender()
        
        PlayerOperations.update_and_save(state, player, f"Стать для {name}")
        return True
    
    @staticmethod
    def add_backpack_items(state: dict, name: str, count: int = 1) -> bool:
        """Додає предмети у рюкзак."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        backpack_pool = state.get("backpack_pool", [])
        added = []
        
        for _ in range(count):
            if not backpack_pool:
                break
            item = backpack_pool.pop()
            if "backpack" not in player or not player["backpack"]:
                player["backpack"] = []
            player["backpack"].append(item)
            added.append(item)
        
        if added:
            state["backpack_pool"] = backpack_pool
            PlayerOperations.update_and_save(state, player, f"Рюкзак для {name} (додано {len(added)} предметів)")
            return True
        
        print(f"❌ Нічого не додано — пул порожній")
        return False
    
    @staticmethod
    def backpack(state: dict, name: str) -> bool:
        """Очищає та перегенерує рюкзак."""
        player_key, player = PlayerOperations.find_player(state, name)
        if not player_key:
            print(f"❌ Гравця {name} не знайдено")
            return False
        
        backpack_pool = state.get("backpack_pool", [])
        items_per_player = state.get("items_per_player", 2)
        
        # Очищаємо рюкзак
        player["backpack"] = []
        
        # Генеруємо нові предмети
        new_items = []
        for _ in range(items_per_player):
            if backpack_pool:
                item = backpack_pool.pop()
                player["backpack"].append(item)
                new_items.append(item)
        
        if new_items:
            state["backpack_pool"] = backpack_pool
            PlayerOperations.update_and_save(state, player, f"Рюкзак для {name} (перегенеровано)")
            return True
        
        print(f"❌ Нічого не додано — пул порожній")
        return False

# ================ РЕГЕНЕРАЦІЯ ЧАСТКОВА ================

def regen_job_only(state: dict, name: str) -> bool:
    """Регенерує тільки професію, зберігаючи досвід."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    current_exp, _ = extract_job_parts(player["job"])
    jobs_pool = state.get("jobs_pool", [])
    
    if jobs_pool:
        job = jobs_pool.pop()
        player["job"] = f"{current_exp} {job}"
        state["jobs_pool"] = jobs_pool
        PlayerOperations.update_and_save(state, player, f"Професію для {name}")
        return True
    
    return False

def regen_job_experience(state: dict, name: str) -> bool:
    """Регенерує тільки досвід професії."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    _, current_job = extract_job_parts(player["job"])
    new_experience_years = random.randint(0, 5)
    new_exp_text = parse_experience_text(new_experience_years)
    
    player["job"] = f"{new_exp_text} {current_job}"
    PlayerOperations.update_and_save(state, player, f"Досвід професії для {name}")
    return True

def regen_job_and_experience(state: dict, name: str) -> bool:
    """Регенерує професію та досвід разом."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    jobs_pool = state.get("jobs_pool", [])
    if jobs_pool:
        exp, job = assign_job_with_experience(jobs_pool)
        player["job"] = f"{exp} {job}"
        state["jobs_pool"] = jobs_pool
        PlayerOperations.update_and_save(state, player, f"Професію та досвід для {name}")
        return True
    
    return False

def regen_hobby_only(state: dict, name: str) -> bool:
    """Регенерує тільки хобі, зберігаючи досвід."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    _, current_exp = extract_hobby_parts(player["hobies"])
    hobbies_pool = state.get("hobies_pool", [])
    
    if hobbies_pool:
        hobby = hobbies_pool.pop()
        player["hobies"] = f"{hobby} ({current_exp})"
        state["hobies_pool"] = hobbies_pool
        PlayerOperations.update_and_save(state, player, f"Хобі для {name}")
        return True
    
    return False

def regen_hobby_experience(state: dict, name: str) -> bool:
    """Регенерує тільки досвід хобі."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    current_hobby, _ = extract_hobby_parts(player["hobies"])
    new_experience_years = random.randint(0, 5)
    new_exp_text = parse_hobby_experience_text(new_experience_years)
    
    player["hobies"] = f"{current_hobby} ({new_exp_text})"
    PlayerOperations.update_and_save(state, player, f"Досвід хобі для {name}")
    return True

def regen_hobby_and_experience(state: dict, name: str) -> bool:
    """Регенерує хобі та досвід разом."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    hobbies_pool = state.get("hobies_pool", [])
    if hobbies_pool:
        hobby, exp = assign_hobby_with_experience(hobbies_pool)
        player["hobies"] = f"{hobby} ({exp})"
        state["hobies_pool"] = hobbies_pool
        PlayerOperations.update_and_save(state, player, f"Хобі та досвід для {name}")
        return True
    
    return False

def regen_fobia_only(state: dict, name: str) -> bool:
    """Регенерує тільки фобію, зберігаючи відсоток."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    current_percentage = player["fobias"].split()[-1] if "%" in player["fobias"] else "50%"
    fobias_pool = state.get("fobias_pool", [])
    
    if fobias_pool:
        fobia = fobias_pool.pop()
        player["fobias"] = f"{fobia} {current_percentage}"
        state["fobias_pool"] = fobias_pool
        PlayerOperations.update_and_save(state, player, f"Фобію для {name}")
        return True
    
    return False

def regen_fobia_percentage(state: dict, name: str) -> bool:
    """Регенерує тільки відсоток фобії."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    fobia_name = " ".join(player["fobias"].split()[:-1]) if "%" in player["fobias"] else player["fobias"]
    new_percentage = random.randint(33, 100)
    
    player["fobias"] = f"{fobia_name} {new_percentage}%"
    PlayerOperations.update_and_save(state, player, f"Відсоток фобії для {name}")
    return True

def regen_fobia_and_percentage(state: dict, name: str) -> bool:
    """Регенерує фобію та відсоток разом."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return False
    
    fobias_pool = state.get("fobias_pool", [])
    if fobias_pool:
        fobia = fobias_pool.pop()
        percentage = random.randint(33, 100)
        player["fobias"] = f"{fobia} {percentage}%"
        state["fobias_pool"] = fobias_pool
        PlayerOperations.update_and_save(state, player, f"Фобію та відсоток для {name}")
        return True
    
    return False

# ================ МАСОВА РЕГЕНЕРАЦІЯ ================

def regen_all_players(state: dict, data: dict, field: str) -> int:
    """Перегенеровує обрану характеристику всім гравцям."""
    updated_count = 0
    field_handlers = {
        "fobia": lambda p: _regen_fobia_all(p, state),
        "hobby": lambda p: _regen_hobby_all(p, state),
        "health": lambda p: _regen_health_all(p, state, data),
        "age": lambda p: _regen_age_all(p, data),
        "gender": lambda p: _regen_gender_all(p),
        "body": lambda p: _regen_body_all(p, state),
        "height": lambda p: _regen_height_all(p),
        "backpack": lambda p: _regen_backpack_all(p, state),
        "extra_info": lambda p: _regen_extra_info_all(p, state),
        "large_inventory": lambda p: _regen_large_inventory_all(p, state),
        "trait": lambda p: _regen_trait_all(p, state),
        "job": lambda p: _regen_job_all(p, state),
    }
    
    handler = field_handlers.get(field)
    if not handler:
        print(f"❌ Невірне поле: {field}")
        return 0
    
    for player in state["players"].values():
        if handler(player):
            updated_count += 1
    
    # Зберігаємо стан та файли
    save_state(state)
    for player in state["players"].values():
        save_single_player_file(player)
    
    print(f"✅ {field} перегенеровано для {updated_count} гравців")
    return updated_count

def _regen_fobia_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації фобій."""
    if state.get("fobias_pool"):
        fobia = state["fobias_pool"].pop()
        percentage = random.randint(33, 100)
        player["fobias"] = f"{fobia} {percentage}%"
        return True
    return False

def _regen_hobby_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації хобі."""
    if state.get("hobies_pool"):
        hobby, exp = assign_hobby_with_experience(state["hobies_pool"])
        player["hobies"] = f"{hobby} ({exp})"
        return True
    return False

def _regen_health_all(player: dict, state: dict, data: dict) -> bool:
    """Допоміжна для масової регенерації здоров'я."""
    if state.get("health_pool"):
        used_health = set()
        health_pool = state["health_pool"].copy()
        health_with_stages = data.get("health_with_stages", {})
        
        all_health = (
            [h for h in health_pool if h not in used_health] +
            [d for d in health_with_stages.keys() if d not in used_health]
        )
        
        if all_health:
            health = random.choice(all_health)
            if health in health_with_stages:
                stage = random.choice(health_with_stages[health])
                player["health"] = f"{health} ({stage})"
            else:
                player["health"] = health
            return True
    return False

def _regen_age_all(player: dict, data: dict) -> bool:
    """Допоміжна для масової регенерації віку."""
    player["age"] = random.choice(data.get("ages", [25]))
    return True

def _regen_gender_all(player: dict) -> bool:
    """Допоміжна для масової регенерації статі."""
    player["gender"] = generate_gender()
    return True

def _regen_body_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації статури."""
    if state.get("body_pool"):
        player["body"] = random.choice(state["body_pool"])
        player["height"] = random.randint(140, 200)
        return True
    return False

def _regen_height_all(player: dict) -> bool:
    """Допоміжна для масової регенерації зросту."""
    player["height"] = random.randint(140, 200)
    return True

def _regen_backpack_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації рюкзака."""
    player["backpack"] = []
    items_per_player = state.get("items_per_player", 2)
    items_added = 0
    
    for _ in range(items_per_player):
        if state.get("backpack_pool"):
            player["backpack"].append(state["backpack_pool"].pop())
            items_added += 1
    
    return items_added > 0

def _regen_extra_info_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації додаткової інформації."""
    if state.get("extra_info_pool"):
        player["extra_info"] = state["extra_info_pool"].pop()
        return True
    return False

def _regen_large_inventory_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації великого інвентаря."""
    if state.get("large_inventory_pool"):
        player["large_inventory"] = state["large_inventory_pool"].pop()
        return True
    return False

def _regen_trait_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації рис характеру."""
    if state.get("traits_pool"):
        player["trait"] = state["traits_pool"].pop()
        return True
    return False

def _regen_job_all(player: dict, state: dict) -> bool:
    """Допоміжна для масової регенерації професій."""
    if state.get("jobs_pool"):
        exp, job = assign_job_with_experience(state["jobs_pool"])
        player["job"] = f"{exp} {job}"
        return True
    return False

def regen_player_completely(state: dict, data: dict, name: str) -> Optional[dict]:
    """Повністю перегенеровує картку гравця."""
    player_key, player = PlayerOperations.find_player(state, name)
    if not player_key:
        print(f"❌ Гравця {name} не знайдено")
        return None
    
    # Зберігаємо спеціальні карти, які не мають змінюватися
    special_cards = player.get("special_cards", []).copy()
    
    # Використовуємо існуючі пули зі стану для регенерації
    # Створюємо тимчасові копії пулів
    temp_pools = {}
    for key, value in state.items():
        if key.endswith("_pool") and isinstance(value, list):
            temp_pools[key] = value.copy()
    
    # Додаємо здоров'я зі стадіями
    health_with_stages = data.get("health_with_stages", {})
    
    # Генеруємо нові характеристики з існуючих пулів
    used_health = set()
    
    # Зріст та стать
    player["height"] = random.randint(140, 200)
    player["gender"] = generate_gender()
    
    # Вік
    player["age"] = random.choice(data.get("ages", [25]))
    
    # Статура (body)
    if temp_pools.get("body_pool"):
        player["body"] = temp_pools["body_pool"].pop()
    
    # Риса характеру (trait)
    if temp_pools.get("traits_pool"):
        player["trait"] = temp_pools["traits_pool"].pop()
    
    # Професія з досвідом
    if temp_pools.get("jobs_pool"):
        exp_text, job = assign_job_with_experience(temp_pools["jobs_pool"])
        player["job"] = f"{exp_text} {job}"
    
    # Здоров'я зі стадіями
    health_pool = temp_pools.get("health_pool", [])
    all_health = (
        [h for h in health_pool if h not in used_health] +
        [d for d in health_with_stages.keys() if d not in used_health]
    )
    
    if all_health:
        health = random.choice(all_health)
        used_health.add(health)
        
        if health in health_with_stages:
            stage = random.choice(health_with_stages[health])
            player["health"] = f"{health} ({stage})"
        else:
            player["health"] = health
    
    # Хобі з досвідом
    if temp_pools.get("hobies_pool"):
        hobby, hobby_exp = assign_hobby_with_experience(temp_pools["hobies_pool"])
        player["hobies"] = f"{hobby} ({hobby_exp})"
    
    # Фобія з відсотком
    if temp_pools.get("fobias_pool"):
        fobia_name = temp_pools["fobias_pool"].pop()
        fobia_percentage = random.randint(33, 100)
        player["fobias"] = f"{fobia_name} {fobia_percentage}%"
    
    # Додаткові відомості
    if temp_pools.get("extra_info_pool"):
        player["extra_info"] = temp_pools["extra_info_pool"].pop()
    
    # Великий інвентар
    if temp_pools.get("large_inventory_pool"):
        player["large_inventory"] = temp_pools["large_inventory_pool"].pop()
    
    # Рюкзак (повністю новий)
    player["backpack"] = []
    items_per_player = state.get("items_per_player", 2)
    for _ in range(items_per_player):
        if temp_pools.get("backpack_pool"):
            player["backpack"].append(temp_pools["backpack_pool"].pop())
    
    # Повертаємо спеціальні карти
    player["special_cards"] = special_cards
    
    # Оновлюємо пули в стані
    for pool_name, pool in temp_pools.items():
        state[pool_name] = pool
    
    # Зберігаємо
    save_state(state)
    save_single_player_file(player)
    
    print(f"✅ Гравець {name} повністю перегенерований (картки збережено)")
    return player

# ================ ІНТЕРАКТИВНИЙ РЕЖИМ ================

def interactive_loop(state: dict, data: dict) -> None:
    """Головний цикл адмін панелі."""
    print("\nАдмін панель (help — список команд)\n")
    
    command_map = {
        # Основні команди
        "health": lambda p: PlayerOperations.reroll_health(state, data, p[0]),
        "body": lambda p: PlayerOperations.reroll_body(state, p[0]),
        "trait": lambda p: PlayerOperations.reroll_field(state, p[0], "trait", "traits_pool"),
        "hobby": lambda p: PlayerOperations.reroll_field(state, p[0], "hobies", "hobies_pool"),
        "fobia": lambda p: PlayerOperations.reroll_field(state, p[0], "fobias", "fobias_pool"),
        "extra": lambda p: PlayerOperations.reroll_field(state, p[0], "extra_info", "extra_info_pool"),
        "job": lambda p: PlayerOperations.reroll_field(state, p[0], "job", "jobs_pool"),
        "large": lambda p: PlayerOperations.reroll_field(state, p[0], "large_inventory", "large_inventory_pool"),
        "agegender": lambda p: PlayerOperations.reroll_age_and_gender(state, data, p[0]),
        "age": lambda p: PlayerOperations.reroll_age(state, data, p[0]),
        "gender": lambda p: PlayerOperations.reroll_gender(state, p[0]),
        "backpack": lambda p: PlayerOperations.backpack(state, p[0]),
        
        # Команди з аргументами
        "add": lambda p: _handle_add_command(state, p),
        
        # Часткова регенерація
        "job_only": lambda p: regen_job_only(state, p[0]),
        "job_exp": lambda p: regen_job_experience(state, p[0]),
        "hobby_only": lambda p: regen_hobby_only(state, p[0]),
        "hobby_exp": lambda p: regen_hobby_experience(state, p[0]),
        "fobia_only": lambda p: regen_fobia_only(state, p[0]),
        "fobia_percent": lambda p: regen_fobia_percentage(state, p[0]),
        
        # Масові операції
        "regen_all": lambda p: _handle_regen_all(state, data, p),
        "regen": lambda p: _handle_regen_command(state, data, p),
    }
    
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
            print_help()
            continue

        if action == "regen" and len(parts) >= 2:
            if parts[1].lower() == "bunker":
                regen_bunker(data)
                continue
            elif parts[1].lower() == "cataclysm":
                regen_cataclysm(data)
                continue
        
        if action in command_map:
            try:
                if action in ["regen_all", "regen", "add"]:
                    command_map[action](parts[1:])
                elif len(parts) >= 2:
                    command_map[action](parts[1:])
                else:
                    print(f"❌ Потрібно вказати ім'я гравця. Наприклад: {action} <ім'я>")
            except Exception as e:
                print(f"❌ Помилка виконання команди: {e}")
        else:
            print("❓ Невідома команда")

def _handle_add_command(state: dict, parts: list) -> None:
    """Обробляє команду add."""
    if len(parts) >= 2 and parts[0] == "backpack":
        name = parts[1]
        count = int(parts[2]) if len(parts) > 2 else 1
        PlayerOperations.add_backpack_items(state, name, count)
    else:
        print("❌ Невірний формат команди add. Використовуйте: add backpack <ім'я> [кількість]")

def _handle_regen_all(state: dict, data: dict, parts: list) -> None:
    """Обробляє команду regen_all."""
    if len(parts) >= 1:
        field = parts[0].lower()
        valid_fields = ["fobia", "hobby", "health", "age", "gender", "body", "height", 
                       "backpack", "extra_info", "large_inventory", "trait", "job"]
        
        if field in valid_fields:
            regen_all_players(state, data, field)
        else:
            print(f"❌ Невірне поле. Доступні: {', '.join(valid_fields)}")
    else:
        print("❌ Потрібно вказати поле. Наприклад: regen_all job")

def _handle_regen_command(state: dict, data: dict, parts: list) -> None:
    """Обробляє команду regen."""
    if len(parts) >= 2:
        if parts[0].lower() == "backpack":
            PlayerOperations.backpack(state, parts[1])
        elif parts[1].lower() == "all":
            regen_player_completely(state, data, parts[0])
        else:
            print("❌ Невірний формат команди regen")
    else:
        print("❌ Невірний формат команди regen")

def print_help() -> None:
    """Виводить допомогу по командам."""
    help_text = """
agegender <name> - перегенерувати вік та стать
age <name> - перегенерувати вік
gender <name> - перегенерувати стать 
                  
body <name> - перегенерувати статуру та зріст
                  
trait <name> - перегенерувати рису характеру

job <name> - перегенерувати професію (з досвідом)
job_only <name> - тільки професія (досвід залишається)
job_exp <name> - тільки досвід професії
                  
health <name> - перегенерувати здоров'я

hobby <name> - перегенерувати хобі (з досвідом)
hobby_only <name> - тільки хобі (досвід залишається)
hobby_exp <name> - тільки досвід хобі
                  
fobia <name> - перегенерувати фобію (з відсотком)
fobia_only <name> - тільки фобія (відсоток залишається)
fobia_percent <name> - тільки відсоток фобії
                  
extra <name> - перегенерувати додаткові відомості
                  
large <name> - перегенерувати великий інвентар

backpack <name> - перегенерувати рюкзак
add backpack <name> [N] - додати N предметів у рюкзак

regen_all <field> - перегенерувати поле всім гравцям
  Поля: fobia, hobby, health, age, gender, body, height, backpack, extra_info, large_inventory, trait, job
regen <name> all - повністю перегенерувати гравця
regen bunker - перегенерувати бункер
regen cataclysm - перегенерувати катаклізм

exit - вийти
"""
    print(help_text)

# ================ ОСНОВНА ФУНКЦІЯ ================

def main() -> None:
    """Головна функція програми."""
    if not os.path.exists(DATA_FILE):
        print(f"Не знайдено {DATA_FILE}. Створи data.json")
        sys.exit(1)
    
    data = load_data()
    
    # Спробувати завантажити збережений стан
    state = load_state()
    if state:
        print("Знайдено попередній стан гри.")
        answer = input("Завантажити попередній стан? (Y/n) > ").strip().lower()
        if answer in ("", "y", "yes"):
            print("Завантажую стан...")
            interactive_loop(state, data)
            return
    
    # Нова генерація
    print("Нова сесія. Введіть імена гравців через кому")
    names_input = input("> ")
    player_names = [name.strip() for name in names_input.split(",") if name.strip()]
    
    if not player_names:
        print("❌ Не введено жодного імені")
        return
    
    items_per_player = 2
    cards_per_player = 2
    
    # Генеруємо гравців
    players, pool_manager = generate_players(player_names, data, items_per_player, cards_per_player)
    
    # Зберігаємо файли
    save_player_files(players)
    generate_bunker(data)
    
    # Створюємо стан
    state = {
        "players": players,
        "items_per_player": items_per_player,
        "cards_per_player": cards_per_player,
    }
    
    # Додаємо всі пули до стану
    for pool_name, pool in pool_manager.pools.items():
        if pool_name != "ages":  # ages не зберігається окремо
            state[f"{pool_name}_pool"] = pool
    
    save_state(state)
    print("Генерація завершена.")
    interactive_loop(state, data)

if __name__ == "__main__":
    main()