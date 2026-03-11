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

    series_dict = get_series_dict()

    for name, files in series_dict.items():
        table.add_row(name, str(files))

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

def get_series_dict() -> dict[str, list[Path]]:
    zip_files = get_zip_files_paths()
    series_dict = {}

    for zip_file in zip_files:
        title = zip_file.stem.split("_")[0]
        series_dict.setdefault(title, []).append(zip_file)
    return series_dict

def get_zip_files_paths() -> list[Path]:
    return list(Path('.').glob('*.zip'))

def get_chapters(zip_path: Path) -> list[float]:
    with zipfile.ZipFile(zip_path, 'r') as z:
        return sorted([float(f[1:-1]) for f in z.namelist() if f.endswith('/')])