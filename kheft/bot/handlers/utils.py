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
    num = "{:,}".format(num).replace(",", "،")

    return "".join(
        [persian_map[digit] if digit in persian_map.keys() else digit for digit in num]
    )


def normalize_to_en(num: str):
    en_map = {
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
    }

    return "".join(
        [en_map[digit] if digit in en_map.keys() else digit for digit in num]
    )
