from cyclopts import App
from rich.console import Console
from rich.table import Table
from .filesystem import get_series


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
    table.add_column("Zipped Downloaded", style="magenta", justify="right")

    series_list = get_series()

    for index, series in enumerate(series_list, start=1):
        table.add_row(f"({index}) {series.name}", str(len(series.zip_chapters)), series.formatted_chapters)

    console.print(table)

@app.command(name=["extract"])
def extract(index: int | None = None):
    series_list = get_series()

    if index is not None and not (1 <= index <= len(series_list)):
        console = Console()
        console.print(f"[red]Invalid index {index}, must be between 1 and {len(series_list)}[/red]")
        return
    
    if index is None:
        targets = series_list
    else:
        targets = [series_list[index - 1]]  # 1-based index

    for series in targets:
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


    
