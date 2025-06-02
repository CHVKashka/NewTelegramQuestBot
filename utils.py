import colorama
from datetime import datetime
import random

def time(format='time'):
    now = datetime.now()
    if format=='time':
        current_time = now.strftime("%H:%M:%S")
    elif format=='ticks':
        return 10000 * datetime.year + 100 * datetime.month + datetime.day
    return current_time

def log(txt,author,color='log'):

    txt=f'>>Log: {time()}/ {author} >> {txt}'
    match color:
        case "log": print(f"{colorama.Fore.WHITE}{txt}{colorama.Fore.RESET}")
        case "error": print(f"{colorama.Fore.RED}{txt}{colorama.Fore.RESET}")
        case 'weak': print(f"{colorama.Fore.LIGHTYELLOW_EX}{txt}{colorama.Fore.RESET}")
        case 'strong': print(f"{colorama.Fore.LIGHTWHITE_EX}{colorama.Back.LIGHTYELLOW_EX}{txt}{colorama.Fore.RESET}{colorama.Back.RESET}")
        case 'done': print(f"{colorama.Fore.GREEN}{txt}{colorama.Fore.RESET}")
        case 'system': print(f"{colorama.Fore.BLUE}{txt}{colorama.Fore.RESET}")

def char_sequence(count:int):
    sequence=''
    for i in range(int(count/2)):
        letter=chr(random.randint(97,122))
        number=chr(random.randint(48,57))
        sequence=sequence+letter+number
    return sequence

