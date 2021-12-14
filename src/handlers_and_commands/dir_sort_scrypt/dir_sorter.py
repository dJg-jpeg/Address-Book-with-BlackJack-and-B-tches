from pathlib import Path
import re
import shutil
from typing import Generator, List, Tuple, Any, Optional

FOLDERS_NAMES = ('image', 'video', 'audio', 'document', 'archive', 'unknown')
FILE_TYPES_EXTENSIONS = (
    ('.jpeg', '.jpg', '.png', '.svg'),
    ('.avi', '.mp4', '.mov', '.mkv'),
    ('.mp3', '.ogg', '.wav', '.amr'),
    ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
    ('.zip', '.gz', '.tar')
)


def check_file_extension(extension: str) -> str:
    for file_types in FILE_TYPES_EXTENSIONS:
        if extension in file_types:
            return FOLDERS_NAMES[FILE_TYPES_EXTENSIONS.index(file_types)]
    return FOLDERS_NAMES[5]


def find_all_files(path: Generator[Path, Any, Any], files: List[list]) -> Tuple[List[Path]]:
    for content in path:
        if content.is_file():
            extension = check_file_extension(get_filename_and_extension(content)[1])
            files[FOLDERS_NAMES.index(extension)].append(content)
        elif content.name not in FOLDERS_NAMES:
            inside_dirs = find_all_files(content.iterdir(), files)
            files = inside_dirs
    return files


def make_dirs(path: Path) -> List[Path]:
    sort_folders = []
    for folder_name in FOLDERS_NAMES:
        if check_is_dir_exist(path / folder_name) is False:
            ((path / folder_name).mkdir())
        sort_folders.append(check_is_dir_exist(path / folder_name))
    return sort_folders


def check_is_dir_exist(path: Path) -> Path or bool:
    if path.exists() is True:
        return path
    return path.exists()


def move_files(files: Tuple[List[Path]], dirs: List[Path]) -> Tuple[List[Path]]:
    for file_type in files:
        for file_path in file_type:
            file_path.replace(dirs[files.index(file_type)] / file_path.name)
            files[files.index(file_type)][files[files.index(file_type)].index(file_path)] = \
                dirs[files.index(file_type)] / file_path.name
    for archive in files[4]:
        path_to_archive_dir = dirs[4] / get_filename_and_extension(archive)[0]
        archive_path = path_to_archive_dir / archive.name
        path_to_archive_dir.mkdir()
        archive.replace(archive_path)
        files[4][files[4].index(archive)] = path_to_archive_dir
        unpack_archives(archive_path, path_to_archive_dir)
        archive_path.unlink()
    return files


def unpack_archives(archive: Path, new_dir_path: Path) -> None:
    shutil.unpack_archive(archive, new_dir_path)


def get_filename_and_extension(filename: Path) -> Tuple[str, str]:
    return filename.resolve().stem, filename.suffix


def rename_files(files: Tuple[List[Path]]) -> Tuple[List[Path]]:
    for category in files:
        for content in category:
            filename = normalize(get_filename_and_extension(content)[0]) + get_filename_and_extension(content)[1]
            content.rename(content.parent / filename)
            files[files.index(category)][category.index(content)] = content.parent / filename
    return files


def remove_empty_dirs(path: Generator[Path, Any, Any]) -> None:
    for content in path:
        if content.is_dir() is True and len(list(content.iterdir())) > 0:
            remove_empty_dirs(content.iterdir())
        if content.is_dir() is True and len(list(content.iterdir())) == 0:
            content.rmdir()
        else:
            continue


def normalize(name: str) -> str:
    table_symbols = ('абвгґдеєжзиіїйклмнопрстуфхцчшщюяыэАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЮЯЫЭьъЬЪ',
                     (
                         *u'abvhgde', 'ye', 'zh', *u'zyi', 'yi', *u'yklmnoprstuf', 'kh', 'ts',
                         'ch', 'sh', 'shch', 'yu', 'ya', 'y', 'ye', *u'ABVHGDE', 'Ye', 'Zh', *u'ZYI',
                         'Yi', *u'YKLMNOPRSTUF', 'KH', 'TS', 'CH', 'SH', 'SHCH', 'YU', 'YA', 'Y', 'YE',
                         *(u'_' * 4)
                     )
                     )
    map_cyr_to_latin = {ord(src): dest for src, dest in zip(*table_symbols)}
    rx = re.compile(r"[^\w_]")
    return rx.sub('_', name.translate(map_cyr_to_latin))


def sort_dir(dir_name: str) -> Optional[str]:
    p = Path(dir_name)
    if p.is_dir():
        all_files = find_all_files(p.iterdir(), [[], [], [], [], [], []])
        all_files = rename_files(all_files)
        new_dirs = make_dirs(p)
        move_files(all_files, new_dirs)
        remove_empty_dirs(p.iterdir())
        return "Sorted successfully , go check your folder)"
    else:
        return None
