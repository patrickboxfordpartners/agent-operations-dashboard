"""CLI interface for querying the Second Brain"""
import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from query.search import brain_search
from shared.monitoring import cost_tracker

console = Console()

@click.group()
def cli():
    """Second Brain CLI - Query your consulting knowledge base"""
    pass

@cli.command()
@click.argument('query')
@click.option('--vertical', '-v', help='Filter by vertical')
@click.option('--limit', '-n', default=5, help='Number of results')
def search(query: str, vertical: str, limit: int):
    """Search for similar projects"""

    async def _search():
        results = await brain_search.search(query, vertical=vertical, limit=limit)

        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        table = Table(title=f"Results for: {query}")
        table.add_column("Client", style="cyan")
        table.add_column("Pain Point", style="yellow", max_width=40)
        table.add_column("ROI", style="green")
        table.add_column("Score", style="blue")

        for r in results:
            meta = r.get('metadata', {})
            table.add_row(
                meta.get('client_name', 'Unknown'),
                meta.get('pain_point', 'N/A')[:40],
                meta.get('roi_metric', 'N/A'),
                f"{r.get('score', 0):.2f}"
            )

        console.print(table)

        # Show spend
        spend = cost_tracker.get_spend_summary()
        console.print(f"\n[dim]💰 Today's spend: ${spend['spent']:.2f} / ${spend['limit']:.2f}[/dim]")

    asyncio.run(_search())

@cli.command()
@click.argument('project_id')
def show(project_id: str):
    """Show full project details"""

    async def _show():
        from storage.vector_store import vector_store

        project = await vector_store.get_by_id(project_id)

        if not project:
            console.print(f"[red]Project not found: {project_id}[/red]")
            return

        # Format as panel
        content = f"""[bold]Client:[/bold] {project.get('client_name')}
[bold]Vertical:[/bold] {project.get('vertical')}

[bold]Pain Point:[/bold]
{project.get('pain_point')}

[bold]Solution:[/bold]
{project.get('solution_description')}

[bold]Tools Used:[/bold] {', '.join(project.get('tools_used', []))}
[bold]ROI:[/bold] {project.get('roi_metric', 'Not specified')}

[bold]Quality Scores:[/bold]
- Completeness: {project.get('completeness_score', 0):.2f}
- Reusability: {project.get('reusability_score', 0):.2f}
- Documentation: {project.get('documentation_quality', 0):.2f}

[bold]Completed:[/bold] {project.get('date_completed')}
"""

        console.print(Panel(content, title=f"Project: {project_id}", border_style="green"))

    asyncio.run(_show())

@cli.command()
@click.argument('client_name')
def client(client_name: str):
    """Show all projects for a client"""

    async def _client():
        projects = await brain_search.get_by_client(client_name)

        if not projects:
            console.print(f"[yellow]No projects found for: {client_name}[/yellow]")
            return

        console.print(f"\n[bold]Projects for {client_name}:[/bold]\n")

        for i, proj in enumerate(projects, 1):
            console.print(f"{i}. {proj.get('solution_category', 'Project')} - {proj.get('roi_metric', 'N/A')}")
            console.print(f"   [dim]{proj.get('pain_point', '')}[/dim]\n")

    asyncio.run(_client())

@cli.command()
def stats():
    """Show Second Brain statistics"""

    async def _stats():
        from storage.vector_store import vector_store

        stats = vector_store.get_stats()
        spend = cost_tracker.get_spend_summary()

        console.print("\n[bold]Second Brain Statistics[/bold]\n")
        console.print(f"📊 Total projects: {stats.get('total_vector_count', 0)}")
        console.print(f"💰 Today's spend: ${spend['spent']:.2f} / ${spend['limit']:.2f} ({spend['utilization']*100:.0f}%)")
        console.print(f"💵 Budget remaining: ${spend['remaining']:.2f}\n")

    asyncio.run(_stats())

if __name__ == "__main__":
    cli()
