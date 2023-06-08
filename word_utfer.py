import random
import unicodedata

def TextUTFy(input, min, max, block):
    output = u'\u2B1E\n\n\n' if block else ''
    # min, max = 10, 50
    for char in input:
        temp_ch = char
        rnd_amount = random.randrange(min, max)
        for i in range(rnd_amount):
            while True:
                accent = random.randrange(300, 370)
                temp_ch = char + (b'\\u0%d' % accent).decode('raw_unicode_escape')
                if sum(not unicodedata.combining(ch) for ch in temp_ch) == 1:
                    char = temp_ch
                    break
        output += char
    output += u'\n\n\n\u2B1E' if block else ''
    return output
