import re
import sys
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

SOURCE_DIR = Path().cwd()
ROOT_DIR = SOURCE_DIR.parent
GEO_DIR = SOURCE_DIR / "GEO_files"
MICKEY = """
              ,n888888n,
             .8888888888b
             888888888888nd8P~''8g,
             88888888888888   _  `'~\.  .n.
             `Y888888888888. / _  |~\\ (8"8b
            ,nnn.. 8888888b.  |  \ \m\|8888P
          ,d8888888888888888b. \8b|.\P~ ~P8~
          888888888888888P~~_~  `8B_|      |
          ~888888888~'8'   d8.    ~      _/
           ~Y8888P'   ~\ | |~|~b,__ __--~
       --~~\   ,d8888888b.\`\_/ __/~
            \_ d88888888888b\_-~8888888bn.
              \8888P   "Y888888888888"888888bn.
           /~'\_"__)      "d88888888P,-~~-~888
          /  / )   ~\     ,888888/~' /  / / 8'
       .-(  / / / |) )-----------(/ ~  / /  |---.
______ | (   '    /_/              (__/     /   |_______
\      |   (_(_ ( /~                \___/_/'    |      /
 \     |    RESULTS FILE SAVED SUCCESSFULLY     |     /
 /     (________________________________________)     \\
/__________)     __--|~mb  ,g8888b.         (__________\\
               _/    8888b(.8P"~'~---__
              /       ~~~| / ,/~~~~--, `\\
             (       ~\,_) (/         ~-_`\\
              \  -__---~._ \             ~\\\\
              (           )\\\\              ))
              `\          )  "-_           `|
                \__    __/      ~-__   __--~
                   ~~"~             ~~~
"""

sys.path.insert(0, str(ROOT_DIR))


def parse_file(file_path: Path, data: list) -> list:
    x_coordinate, y_coordinate, _ = data[4].strip().split(" ")
    width, length, _ = data[5].strip().split(" ")
    width = abs(float(x_coordinate)) + abs(float(width))
    length = abs(float(y_coordinate)) + abs(float(length))
    thick = data[19].strip()
    material = data[18].strip()

    bends = 0
    punch = 0
    flag = 0
    for line in data:
        if re.findall('^LIN', line.strip()) and flag == 0:
            flag = 1
            continue
        if re.findall('^3 0', line.strip()) and flag == 1:
            bends += 1
            flag = 0
        if re.findall('PKT', line.strip()):
            punch += 1

    return [file_path, material, width, length, thick, bends, punch]


def write_csv(file_path: Path, data: list, header: list = None) -> None:
    """ Write data to a csv file """
    import csv
    with file_path.open(mode="w", encoding="utf-8") as csv_file:
        f_write = csv.writer(csv_file)
        if header:
            f_write.writerow(header)

        f_write.writerows(data)


def progress_bar(files: list):
    p_bar = tqdm(files, unit="files", desc="Processing geo files", ncols=80)
    p_bar.bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}'
    return p_bar


def p_continue():
    action = input('continue?')
    if action not in 'yY':
        exit()


def main():
    global SOURCE_DIR
    global ROOT_DIR
    global GEO_DIR

    today = datetime.now().strftime('%Y-%m-%d')

    # Prompt for path, use default if nothing provided
    while True:
        geo_file_path_str = input(f"Enter path to .geo-files: [{GEO_DIR}] ")

        if geo_file_path_str:
            tmp_dir = Path(geo_file_path_str)
            if tmp_dir.is_dir():
                geo_files = list(tmp_dir.glob('*.[gG][eE][oO]'))
                if geo_files:
                    GEO_DIR = Path(geo_file_path_str)
                else:
                    print(f"This directory [{GEO_DIR}] has no geo file!")
                    p_continue()
            else:
                print(f'Given path {geo_file_path_str} does not exists!')
                p_continue()
        else:
            geo_files = list(GEO_DIR.glob('*.[gG][eE][oO]'))
            break

    # Find max file name length for padding the progress bar i.e [    567.geo]
    file_name_len = max([len(file.name) for file in geo_files])

    # Parse all *.geo files and collect result in output
    p_bar = progress_bar(sorted(geo_files, key=lambda file_p: file_p.name))
    output = []
    for file in p_bar:
        data = open(file, "r", encoding='utf-8', errors='ignore').readlines()
        output.append(parse_file(file.name, data))
        spc = (file_name_len - len(file.name)) * ' '
        p_bar.set_postfix_str(f'[{spc + file.name}]')

    # Write results to file
    file_output_name = GEO_DIR / f"{today}_results.csv"
    header = ['file', 'material', 'width', 'length', 'thickness', 'bendmarks', 'punching_features']
    write_csv(file_output_name, output, header=header)
    print(MICKEY)


if __name__ == '__main__':
    main()
