from collections import defaultdict
from pathlib import Path
from .series import Series

def get_series() -> list[Series]:
    zip_file_paths: list[Path] = get_zip_files_paths()
    series_dict = defaultdict(dict)

    for zip_file_path in zip_file_paths:
        title = zip_file_path.stem.split("_")[0]
        chapters = tuple([float(ch.strip()[1:]) for ch in zip_file_path.stem.split("_")[:] if ch.strip().startswith("c")])
        series_dict[title][chapters] = zip_file_path

    return [Series(name, chapter_map) for name, chapter_map in series_dict.items()]

def get_zip_files_paths() -> list[Path]:
    return list(Path('.').glob('*.zip'))