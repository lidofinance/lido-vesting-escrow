from contextlib import contextmanager
import curses


color_hl = "\x1b[38;5;141m"
color_green = "\033[92m"
color_yellow = "\033[93m"
color_blue = "\033[94m"
color_red = "\033[31m"
color_end = "\033[0m"


def highlight(text, color=color_hl):
    return f"{color}{text}{color_end}"


def prompt_yes_no(text):
    answer = input(f"{color_yellow}{text} (y/n) > {color_end}")
    return "y" in answer.lower()


def info(text, value=None):
    result = highlight("[info] ", color_blue) + text

    if value is not None:
        result += ": " + highlight(value, color_hl)

    print(result)


def okay(text, value=None):
    result = highlight("[okay] ", color_green) + text

    if value is not None:
        result += ": " + highlight(value, color_hl)

    print(result)


def warn(text, value=None):
    result = highlight("[warn] ", color_yellow) + text

    if value is not None:
        result += ": " + highlight(value, color_hl)

    print(result)


def error(text, value=None):
    result = highlight("[error] ", color_red) + text

    if value is not None:
        result += ": " + highlight(value, color_hl)

    print(result)


def note(text, value=None):
    result = highlight("[>>>>] ", color_yellow) + text

    if value is not None:
        result += ": " + highlight(value, color_hl)

    print(result)


def assert_equals(desc, actual, expected):
    assert actual == expected, f"{desc}: expected {expected} bot got {actual}"
    okay(desc, actual)


@contextmanager
def block(msg: str):
    header = f"{highlight('[info]', color_blue)} {msg} ..."
    failed = False
    try:
        print(header, end=" ")
        print(highlight("IN PROGRESS", color_yellow))
        yield
    except Exception as e:
        failed = True
        raise e
    finally:
        print(header, end=" ")
        if failed:
            print(highlight("FAIL", color_red))
        else:
            print(highlight("OK", color_green))
