import click
import re
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from lens.core.registry import COLLECTORS
from lens.core.workspace import create_workspace, save_json
from lens.core.collector_manager import run_collectors
from lens.core.report_generator import generate_reports

# Define color palette
THEME = Theme({
    "accent": "#E0B0FF",      # Mauve: Primary accents and highlights
    "secondary": "#CCCCFF",   # Periwinkle: Secondary info and structure
    "fail": "#FF5F5F",        # Red: Failure states
    "success": "white",       # White: Main content and results
    "dim": "dim",
})

console = Console(theme=THEME)

def print_header():
    console.print("[accent]Lens.[/accent]")
    console.rule(style="secondary")
    console.print()

@click.group()
@click.version_option(version="0.1.3", prog_name="lens")
def main():
    """Lens: Local AI research agent."""
    pass

@main.command(name="research")
@click.option("-q", "--query", help="Query text to research.")
@click.argument("query_arg", required=False)
def research(query, query_arg):
    """Run research on a given query."""
    run_research(query, query_arg)

@main.command(name="list")
def list_sessions():
    """List all research sessions."""
    workspace_dir = Path("workspace")
    if not workspace_dir.exists():
        console.print("[dim]No sessions found.[/dim]")
        return
    
    sessions = sorted([d.name for d in workspace_dir.iterdir() if d.is_dir()], reverse=True)
    if not sessions:
        console.print("[dim]No sessions found.[/dim]")
        return

    table = Table(box=None, expand=False)
    table.add_column("Session ID", style="accent")
    for session in sessions:
        table.add_row(session)
    console.print(table)

@main.command(name="resume")
@click.argument("session_id")
def resume(session_id):
    """Resume a research session."""
    workspace_path = Path("workspace") / session_id
    if not workspace_path.exists():
        console.print(f"[fail]Error: Session {session_id} not found.[/fail]")
        return
    
    console.print(f"[accent]Resuming session:[/accent] [white]{session_id}[/white]")
    
    # Reload workspace info
    meta_path = workspace_path / "meta.json"
    if meta_path.exists():
        import json
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        console.print(f"[secondary]Query:[/secondary] [white]{meta.get('query', 'Unknown')}[/white]")
    
    console.print(f"[secondary]Path:[/secondary] [white]{workspace_path.resolve()}[/white]")
    
    # Re-generate reports if they don't exist
    report_path = workspace_path / "report.md"
    if not report_path.exists():
        console.print("[secondary]Re-generating reports...[/secondary]")
        # We need a workspace_info dict similar to what create_workspace returns
        workspace_info = {
            "base": workspace_path,
            "raw": workspace_path / "raw",
            "logs": workspace_path / "logs",
            "query": meta.get("query", "") if meta_path.exists() else session_id
        }
        generate_reports(workspace_info)
        console.print("[success]Reports re-generated.[/success]")

def run_research(query, query_arg):
    clean_query = (query or query_arg or "").strip()
    if not clean_query:
        console.print("[fail]Error: Query cannot be empty. Use -q 'query' or provide it as an argument.[/fail]")
        return

    print_header()
    
    console.print("[secondary]Research[/secondary]")
    console.print(f"[white]{clean_query}[/white]")
    console.print()
    
    # 1. Create workspace
    workspace = create_workspace(clean_query)
    
    # 2. Execute collectors
    console.print("[secondary]Collecting Sources[/secondary]")
    console.print()

    execution_reports = []
    total_collectors = len(COLLECTORS)
    
    with Progress(
        SpinnerColumn(style="accent"),
        BarColumn(bar_width=30, complete_style="accent", finished_style="accent"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}% ({task.completed}/{task.total})", style="secondary"),
        console=console
    ) as progress:
        task = progress.add_task("[secondary]Collecting...[/secondary]", total=total_collectors)
        
        for report in run_collectors(COLLECTORS, clean_query):
            execution_reports.append(report)
            progress.advance(task)
            
    console.print()

    # 3. Save results
    all_sources = {}
    for report in execution_reports:
        if report["status"] == "success":
            # Save raw individual result
            file_path = workspace["raw"] / f"{report['collector']}.json"
            save_json(file_path, report["data"])
            all_sources[report["collector"]] = report["data"]
    
    # Save sources.json in root
    save_json(workspace["base"] / "sources.json", all_sources)
    
    # Save meta.json in root
    meta = {
        "query": clean_query,
        "timestamp": workspace["timestamp"],
        "session_id": workspace["name"],
        "version": "0.1.3"
    }
    save_json(workspace["base"] / "meta.json", meta)
    
    # 4. Generate reports
    generate_reports(workspace)
    
    console.print("[success]Research complete.[/success]")
    console.print(f"[secondary]Workspace saved at:[/secondary] [white]workspace/{workspace['name']}/[/white]")
    console.print()


if __name__ == "__main__":
    main()
