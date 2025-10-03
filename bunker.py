import json
import random
import os

def generate_players(player_names, data):
    players = []

    professions = data["professions"].copy()
    ages = data["ages"].copy()
    backpack = data["backpack"].copy()

    random.shuffle(professions)
    random.shuffle(ages)
    random.shuffle(backpack)

    for name in player_names:
        player = {
            "name": name.strip(),
            "health": random.choice(data["health"]),
            "profession": professions.pop() if professions else "Без професії",
            "age": ages.pop() if ages else "Невідомий",
            "backpack": backpack.pop() if backpack else "Порожньо",
            "backpack2": backpack.pop() if backpack else "Порожньо"
        }
        players.append(player)

    return players

def save_player_files(players):
    if not os.path.exists("players"):
        os.makedirs("players")

    for player in players:
        filename = f"players/{player['name']}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Гравець: {player['name']}\n")
            f.write(f"Вік: {player['age']}\n")
            f.write(f"Здоров'я: {player['health']}\n")
            f.write(f"Професія: {player['profession']}\n")
            f.write(f"Наплічник: {player['backpack']}" + " i " + f"{player['backpack2']}\n")

    print("Згенеровані файли для кожного гравця в папці 'players'.")

def generate_bunker(data):
    cataclysm = random.choice(data["cataclysms"])
    description = random.choice(data["descriptions"])
    bunker_items = random.sample(data["bunker_items"], 3)

    size = random.randint(21, 500)  # м²
    time = random.randint(9, 41)    # місяців
    food = random.randint(3, 24)    # на скільки місяців вистачить
    water = random.randint(3, 24)

    with open("players/bunker.txt", "w", encoding="utf-8") as f:
        f.write(f"Катаклізм: {cataclysm}\n")
        f.write(f"Опис бункера: {description}\n")
        f.write(f"Інвентар бункера: {', '.join(bunker_items)}\n")
        f.write(f"Розмір: {size} м²\n")
        f.write(f"Час перебування: {time} місяців\n")
        f.write(f"Їжа: вистачить на {food} місяців\n")
        f.write(f"Вода: вистачить на {water} місяців\n")

    print("Згенеровано bunker.txt")

def main():
    print("Введіть імена гравців через кому")
    names_input = input("> ")
    player_names = [name.strip() for name in names_input.split(",") if name.strip()]

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    players = generate_players(player_names, data)
    save_player_files(players)
    generate_bunker(data)

if __name__ == "__main__":
    main()
