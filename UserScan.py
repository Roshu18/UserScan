import argparse
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from utils.checker import check_site
from utils.config import DEFAULT_THREADS
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()

# Load sites from JSON
with open("sites.json", "r") as file:
    SITES = json.load(file)

def check_usernames(username, threads, output):
    results = []
    progress = Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} sites checked"),
        console=console
    )
    
    with progress:
        task = progress.add_task("Checking usernames...", total=len(SITES))
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_site = {executor.submit(check_site, site, username): site for site in SITES}
            
            for future in future_to_site:
                site_name, status = future.result()
                results.append((site_name, status))
                progress.advance(task)
    
    # Display results in a formatted table
    table = Table(title=f"Username Check Results for '{username}'", show_lines=True)
    table.add_column("Site", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="green")
    
    for site, status in results:
        table.add_row(site, status)
    
    console.print(table)
    
    # Save results if output file is specified
    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=4)
        console.print(f"\n✅ [bold green]Results saved to {output}[/bold green]")

# CLI Argument Parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Username Checker Tool")
    parser.add_argument("-u", "--username", required=True, help="Username to check")
    parser.add_argument("-t", "--threads", type=int, default=DEFAULT_THREADS, help="Number of threads (default: 10)")
    parser.add_argument("-o", "--output", help="Save results to a JSON file")
    
    args = parser.parse_args()
    check_usernames(args.username, args.threads, args.output)