with open("wipro.html", "r", encoding="utf-8") as f:
    content = f.read().lower()
    if "successfactors" in content:
        print("SuccessFactors found!")
    if "rmk" in content:
        print("RMK found!")
    if "phenom" in content:
        print("Phenom found!")
