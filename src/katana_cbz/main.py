from cyclopts import App
from rich.console import Console
from rich.table import Table
from typing import Annotated
from cyclopts import Parameter
from .filesystem import get_series


app = App(help="A tool to convert zip files from mangakatana to cbz")

@app.command
def foo(loops: int):
    for i in range(loops):
        print(f"Looping! {i}")

@app.command(name=["ls", "list"])
def ls():
    series_list = get_series()

    console = Console()
    if len(series_list) == 0:
        console.print("[yellow]No series found in the current directory.[/yellow]")
        return
    
    table = Table(title="Manga Serie(s)")
    table.add_column("Series", style="cyan")
    table.add_column("Chapters Converted", style="magenta", justify="right")
    table.add_column("Zipped Downloaded", style="magenta", justify="right")

    for index, series in enumerate(series_list, start=1):
        table.add_row(f"({index}) {series.name}", str(len(series.zip_chapters)), series.formatted_chapters)

    console.print(table)

@app.command(name=["extract"])
def extract(index: int | None = None, *, chapter: Annotated[float | None, Parameter(name=["--chapter", "-c"])] = None):
    console = Console()
    series_list = get_series()

    if len(series_list) == 0:
        console.print("[yellow]No series found in the current directory.[/yellow]")
        return

    if index is not None and not (1 <= index <= len(series_list)):
        console.print(f"[red]Invalid index {index}, must be between 1 and {len(series_list)}[/red]")
        return

    targets = [series_list[index - 1]] if index is not None else series_list

    for series in targets:
        if chapter is not None:
            series.extract_chapter(chapter)
        else:
            series.extract_zipped_chapters()

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


    
