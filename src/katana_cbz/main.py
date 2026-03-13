from cyclopts import App
import os
import zipfile
from rich.console import Console
from rich.table import Table
from rich.progress import track
import time
from collections import defaultdict

from pathlib import Path


app = App(help="A tool to convert zip files from mangakatana to cbz")

@app.command
def foo(loops: int):
    for i in range(loops):
        print(f"Looping! {i}")

@app.command(name=["ls", "list"])
def ls():
    console = Console()
    table = Table(title="Manga Serie(s)")
    table.add_column("Series", style="cyan")
    table.add_column("Chapters Converted", style="magenta", justify="right")
    table.add_column("Chapters Downloaded", style="magenta", justify="right")

    series_list = get_series()

    for series in series_list:
        table.add_row(series.name, str(series.chapter_map.values()), series.formatted_chapters)
        print(series.zip_chapters)

    console.print(table)

@app.command(name=["extract"])
def extract():
    series_list = get_series()
    for series in series_list:
        series.extract_zipped_chapters()

@app.command()
def test2():
    for step in track(range(100), description="Processing..."):
        time.sleep(0.1)  # Simulate work

@app.command()
def test():
    series_list = get_series()
    series_list[0].extract_chapter(1)
    print(series_list[0].name)

@app.default
def default_action():
    print("Hello world! This runs when no command is specified.")

def main():
    app()

def get_series() :
    zip_file_paths: list[Path] = get_zip_files_paths()
    series_dict = defaultdict(dict)

    for zip_file_path in zip_file_paths:
        title = zip_file_path.stem.split("_")[0]
        chapters = tuple([float(ch.strip()[1:]) for ch in zip_file_path.stem.split("_")[:] if ch.strip().startswith("c")])
        series_dict[title][chapters] = zip_file_path

    return [Series(name, chapter_map) for name, chapter_map in series_dict.items()]

def get_zip_files_paths() -> list[Path]:
    return list(Path('.').glob('*.zip'))

def get_chapters(zip_path: Path) -> list[float]:
    with zipfile.ZipFile(zip_path, 'r') as z:
        return sorted([float(f[1:-1]) for f in z.namelist() if f.endswith('/')])
    
class Series:
    
    def __init__(self, name, chapter_map) -> None:
        self.name = name
        self.chapter_map: dict[tuple[float,float], Path]= chapter_map
        self.zip_chapters = self.get_zip_chapters()
        self.formatted_chapters = self.get_formatted_chapter_list(self.zip_chapters)

    def get_zip_chapters(self) -> list[float]:
        chapters = []
        for zip_file_path in self.chapter_map.values():
            with zipfile.ZipFile(zip_file_path, 'r') as z:
                chapters.extend([float(f[1:-1]) for f in z.namelist() if f.endswith('/')])
        return sorted(chapters)
    
    def get_formatted_chapter_list(self, numbers):
        if not numbers:
            return ""

        sorted_nums = sorted(set(numbers))
        ranges: list[tuple[float, float]] = []
        start = end = sorted_nums[0]

        for num in sorted_nums[1:]:
            if num - end <= 1:
                end = num
            else:
                ranges.append((start, end))
                start = end = num
        ranges.append((start, end))

        def fmt(n: float) -> str:
            return str(int(n)) if n == int(n) else str(n)

        def fmt_range(start: float, end: float) -> str:
            return f"{fmt(start)}-{fmt(end)}" if start != end else fmt(start)

        return ", ".join(fmt_range(s, e) for s, e in ranges)
    
    def extract_zipped_chapters(self):
        for chapter in track(self.zip_chapters, description=self.name + " - Extracting chapters..."):
            self.extract_chapter(chapter)

    
    def extract_chapter(self, chapter: float):
        output_dir = Path(".").joinpath(self.name)
        output_dir.mkdir(exist_ok=True)

        subfolder_name = f"c{chapter:03.0f}" # name_c001.cbz

        for interval, zip_path in self.chapter_map.items():
                if interval[0] <= chapter <= interval[1]:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        cbz_path = output_dir.joinpath(f"{self.name}_{subfolder_name}.cbz")

                        with zipfile.ZipFile(cbz_path, 'w', compression=zipfile.ZIP_DEFLATED) as cbz:
                            for file in zip_ref.namelist():
                                if file.startswith(subfolder_name + "/"):
                                    file_content = zip_ref.read(file)
                                    cbz_file_path = Path(subfolder_name).joinpath(Path(file).name)
                                    cbz.writestr(str(cbz_file_path), file_content)

    def extract_all(self):
        output_dir = Path(".").joinpath(self.name)
        output_dir.mkdir(exist_ok=True)

        for zip_file_path in self.chapter_map.values():
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                for chapter_dir in zip_ref.namelist():
                    if chapter_dir.endswith('/') and chapter_dir != zip_file_path.stem + "/":
                        subfolder_name = Path(chapter_dir[:-1]).stem
                        cbz_path = output_dir.joinpath(f"{self.name}_{subfolder_name}.cbz")

                        with zipfile.ZipFile(cbz_path, 'w', compression=zipfile.ZIP_DEFLATED) as cbz:
                            for file in zip_ref.namelist():
                                if file.startswith(chapter_dir):
                                    file_content = zip_ref.read(file)
                                    cbz_file_path = Path(subfolder_name).joinpath(Path(file).name)
                                    cbz.writestr(str(cbz_file_path), file_content)