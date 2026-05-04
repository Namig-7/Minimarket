import json, time, os
from datetime import datetime

DATA_DIR = "data"

def load_json(path, default):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(default, f, indent=2)
        return default
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def log(username, text):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/history_{username}.log", "a") as f:
        f.write(f"[{datetime.now()}] {text}\n")

def login():
    users = load_json(f"{DATA_DIR}/users.json", [])
    while True:
        username = input("Username: ")
        password = input("Password: ")

        for user in users:
            if user["username"] == username:

                if user["lock_until"] and time.time() < user["lock_until"]:
                    print("10 saniyə gözlə!")
                    continue

                if user["password"] == password:
                    user["failed_attempts"] = 0
                    save_json(f"{DATA_DIR}/users.json", users)
                    log(username, "LOGIN_SUCCESS")
                    return user
                else:
                    user["failed_attempts"] += 1
                    log(username, "LOGIN_FAIL")

                    if user["failed_attempts"] >= 3:
                        print("3 səhv! 10 saniyə bloklandı")
                        user["lock_until"] = time.time() + 10
                        user["failed_attempts"] = 0

                    save_json(f"{DATA_DIR}/users.json", users)

        print("İstifadəçi tapılmadı")

def show_products():
    products = load_json(f"{DATA_DIR}/products.json", {})
    for cat, items in products.items():
        print(f"\n{cat}")
        for p in items:
            print(p["id"], p["name"], p["price"])

def main():
    user = login()
    username = user["username"]

    basket_file = f"{DATA_DIR}/basket_{username}.json"
    basket = load_json(basket_file, [])

    while True:
        print("\n1.Products 2.Basket 0.Exit")
        ch = input("Seçim: ")

        if ch == "1":
            show_products()
            name = input("Məhsul adı: ")
            price = float(input("Qiymət: "))
            qty = int(input("Miqdar: "))

            basket.append({
                "product": name,
                "unit": price,
                "qty": qty,
                "total": price * qty
            })

            save_json(basket_file, basket)
            log(username, f"BASKET_ADD {name}")

        elif ch == "2":
            total = sum(x["total"] for x in basket)
            print("Cəm:", total)

            if total <= user["balance"]:
                user["balance"] -= total
                basket.clear()
                save_json(basket_file, basket)

                users = load_json(f"{DATA_DIR}/users.json", [])
                for u in users:
                    if u["username"] == username:
                        u["balance"] = user["balance"]
                save_json(f"{DATA_DIR}/users.json", users)

                log(username, "CHECKOUT_SUCCESS")
                print("Alış tamamlandı")
            else:
                log(username, "CHECKOUT_FAIL")
                print("Balans çatmır")

        elif ch == "0":
            break

main()
