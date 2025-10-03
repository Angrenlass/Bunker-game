import json
import random
import os

def generate_players(num_players, data):
    players = []

    # робимо копії для унікальних характеристик
    professions = data["professions"].copy()
    ages = data["ages"].copy()
    items = data["items"].copy()

    random.shuffle(professions)
    random.shuffle(ages)
    random.shuffle(items)

    for i in range(num_players):
        player = {
            "id": i + 1,
            "health": random.choice(data["health"]),  # може повторюватися
            "profession": professions.pop() if professions else "Без професії",
            "age": ages.pop() if ages else "Невідомий",
            "item": items.pop() if items else "Порожньо"
        }
        players.append(player)

    return players

def save_player_files(players):
    # створюємо папку, щоб файли були окремо
    if not os.path.exists("players"):
        os.makedirs("players")

    for player in players:
        filename = f"players/player{player['id']}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Гравець {player['id']}\n")
            f.write(f"Вік: {player['age']}\n")
            f.write(f"Здоров'я: {player['health']}\n")
            f.write(f"Професія: {player['profession']}\n")
            f.write(f"Інвентар: {player['item']}\n")

    print("✅ Згенеровані файли для кожного гравця в папці 'players'.")

def main():
    num_players = int(input("Введіть кількість гравців: "))

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    players = generate_players(num_players, data)
    save_player_files(players)

if __name__ == "__main__":
    main()
