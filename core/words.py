import csv

def load_words(level, category):
    result = []

    with open("assets/words.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["level"] == str(level) and row["category"] == category:
                result.append({
                    "en": row["english"],
                    "zh": row["chinese"]
                })

    return result