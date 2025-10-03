import json
import random
import os

def generate_players(player_names, data):
    players = []

    # робимо копії для унікальних характеристик
    professions = data["professions"].copy()
    ages = data["ages"].copy()
    items = data["items"].copy()

    random.shuffle(professions)
    random.shuffle(ages)
    random.shuffle(items)

    for name in player_names:
        player = {
            "name": name.strip(),
            "health": random.choice(data["health"]),  # може повторюватися
            "profession": professions.pop() if professions else "Без професії",
            "age": ages.pop() if ages else "Невідомий",
            "item": items.pop() if items else "Порожньо"
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
            f.write(f"Інвентар: {player['item']}\n")

    print("Згенеровані файли для кожного гравця в папці 'players'.")

def main():
    print("Введіть імена гравців через кому:")
    names_input = input("> ")
    player_names = [name.strip() for name in names_input.split(",") if name.strip()]

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    players = generate_players(player_names, data)
    save_player_files(players)

if __name__ == "__main__":
    main()
