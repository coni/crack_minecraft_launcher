
def find_string(text, string):
    for i in text.splitlines():
        if string in i:
            return i
    return None