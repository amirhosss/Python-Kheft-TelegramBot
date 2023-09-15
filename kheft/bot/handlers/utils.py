def normalize_from_en(num: int):
    persian_map = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    }
    num = "{:,}".format(num)

    return "".join(
        [persian_map[digit] if digit in persian_map.keys() else digit for digit in num]
    )
