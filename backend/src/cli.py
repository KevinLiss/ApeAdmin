"""CLI entry point for managing the server.

Usage:
    apeadmin serve          Start the development server
    apeadmin migrate        Run Alembic migrations
    apeadmin seed           Seed initial data
    apeadmin plugins list   List discovered plugins
"""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="apeadmin", help="ApeAdmin management CLI")
console = Console()


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(True, help="Auto-reload on file changes"),
    workers: int = typer.Option(1, min=1, help="Uvicorn worker count; hot-plugging requires 1"),
):
    """Start the development server."""
    import uvicorn

    if workers != 1:
        raise typer.BadParameter("插件热拔插当前要求 workers=1；多 worker 协调控制面尚未启用")

    console.print(f"[bold green]Starting ApeAdmin on {host}:{port}[/bold green]")
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="debug",
    )


@app.command()
def init_db():
    """Create all database tables."""
    from src.db import init_db

    console.print("[bold yellow]Creating database tables...[/bold yellow]")
    asyncio.run(init_db())
    console.print("[bold green]Database tables created![/bold green]")


@app.command()
def seed():
    """Seed initial data (super admin, menus, roles)."""
    from src.core.seed import seed_initial_data

    console.print("[bold yellow]Seeding initial data...[/bold yellow]")
    asyncio.run(seed_initial_data())
    console.print("[bold green]Data seeded![/bold green]")


@app.command()
def plugins():
    """List all discovered plugins."""
    from src.plugins import plugin_manager

    plugin_manager.discover()
    all_plugins = plugin_manager.list_plugins()

    if not all_plugins:
        console.print("[yellow]No plugins discovered.[/yellow]")
        return

    table = Table(title="Discovered Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="white")
    table.add_column("Version", style="green")
    table.add_column("Enabled", style="yellow")
    table.add_column("Description", style="dim")

    for p in all_plugins:
        table.add_row(
            p.name,
            p.display_name,
            p.version,
            "✓" if p.enabled else "✗",
            p.description[:50],
        )

    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()
