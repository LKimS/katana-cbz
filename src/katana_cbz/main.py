from cyclopts import App
import os
import zipfile
from rich.console import Console
from rich.table import Table

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
        table.add_row(series.name, str(series.zip_file_paths), series.formatted_chapters)

    console.print(table)

@app.command()
def test():
    zip_file = get_zip_files_paths()[0]
    chapters = get_chapters(zip_path=zip_file)
    print(chapters)



@app.default
def default_action():
    print("Hello world! This runs when no command is specified.")

def main():
    app()

def get_series():
    zip_file_paths = get_zip_files_paths()
    series_dict = {}

    for zip_file_path in zip_file_paths:
        title = zip_file_path.stem.split("_")[0]
        series_dict.setdefault(title, []).append(zip_file_path)

    return [Series(name, zip_file_paths) for name, zip_file_paths in series_dict.items()]

def get_zip_files_paths() -> list[Path]:
    return list(Path('.').glob('*.zip'))

def get_chapters(zip_path: Path) -> list[float]:
    with zipfile.ZipFile(zip_path, 'r') as z:
        return sorted([float(f[1:-1]) for f in z.namelist() if f.endswith('/')])
    
class Series:
    
    def __init__(self, name, zip_files_paths) -> None:
        self.name = name
        self.zip_file_paths = zip_files_paths
        self.zip_chapters = self.get_zip_chapters()
        self.formatted_chapters = self.get_formatted_chapter_list(self.zip_chapters)

    def get_zip_chapters(self) -> list[float]:
        chapters = []
        for zip_file_path in self.zip_file_paths:
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
