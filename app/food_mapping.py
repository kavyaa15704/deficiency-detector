"""
Curated food recommendations per nutrient deficiency.
~8-10 foods per nutrient, 130+ total (with overlap, since many foods are
good sources of multiple nutrients - that overlap is realistic).
"""

FOOD_MAP = {
    "Iron": ["red meat", "spinach", "lentils", "chickpeas", "tofu",
             "pumpkin seeds", "quinoa", "dark chocolate", "dried apricots"],
    "Vitamin B12": ["salmon", "eggs", "milk", "yogurt", "nutritional yeast",
                    "chicken breast", "sardines", "fortified cereal"],
    "Vitamin D": ["salmon", "egg yolks", "fortified milk", "mushrooms",
                  "cod liver oil", "fortified orange juice", "tuna"],
    "Vitamin C": ["oranges", "strawberries", "bell peppers", "broccoli",
                  "kiwi", "brussels sprouts", "papaya", "guava"],
    "Vitamin A": ["carrots", "sweet potato", "spinach", "kale", "mango",
                  "butternut squash", "liver", "apricots"],
    "Vitamin E": ["almonds", "sunflower seeds", "avocado", "hazelnuts",
                  "spinach", "olive oil", "peanut butter"],
    "Vitamin K": ["kale", "spinach", "broccoli", "brussels sprouts",
                  "parsley", "green beans", "cabbage"],
    "Folate": ["lentils", "spinach", "asparagus", "black beans", "avocado",
               "broccoli", "fortified bread", "oranges"],
    "Calcium": ["milk", "yogurt", "cheese", "kale", "almonds", "tofu",
                "sardines", "fortified orange juice"],
    "Magnesium": ["almonds", "spinach", "cashews", "black beans", "avocado",
                  "dark chocolate", "pumpkin seeds", "brown rice"],
    "Potassium": ["bananas", "sweet potato", "spinach", "avocado", "beans",
                  "coconut water", "yogurt", "salmon"],
    "Zinc": ["oysters", "beef", "pumpkin seeds", "chickpeas", "cashews",
             "eggs", "yogurt", "lentils"],
    "Iodine": ["seaweed", "cod", "shrimp", "dairy milk", "eggs",
               "iodized salt", "tuna", "prunes"],
    "Vitamin B6": ["chickpeas", "chicken breast", "salmon", "potatoes",
                   "bananas", "fortified cereal", "turkey"],
    "Omega-3": ["salmon", "walnuts", "chia seeds", "flaxseeds", "sardines",
                "mackerel", "soybeans", "hemp seeds"],
}


def get_foods(nutrient: str) -> list[str]:
    if nutrient not in FOOD_MAP:
        raise ValueError(f"No food mapping for '{nutrient}'")
    return FOOD_MAP[nutrient]


if __name__ == "__main__":
    total = sum(len(v) for v in FOOD_MAP.values())
    unique = len({f for foods in FOOD_MAP.values() for f in foods})
    print(f"Nutrients: {len(FOOD_MAP)} | Food entries: {total} | Unique foods: {unique}")
    for nutrient, foods in FOOD_MAP.items():
        print(f"  {nutrient:<12} ({len(foods)}): {', '.join(foods)}")
