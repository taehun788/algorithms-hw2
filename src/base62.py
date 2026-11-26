ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode(number):
    if type(number) is not int or number < 0:
        raise ValueError("expected a nonnegative integer")
    if number == 0:
        return "0"
    digits = []
    while number:
        number, remainder = divmod(number, 62)
        digits.append(ALPHABET[remainder])
    return "".join(reversed(digits))


def decode(code):
    if not isinstance(code, str) or not code:
        raise ValueError("expected a nonempty base62 code")
    number = 0
    for letter in code:
        digit = ALPHABET.find(letter)
        if digit < 0:
            raise ValueError("invalid base62 digit")
        number = 62 * number + digit
    return number
