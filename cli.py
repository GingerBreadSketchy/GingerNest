import sys
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from news_service import fetch_all_news

console = Console()

def display_welcome():
    welcome_text = Text()
    welcome_text.append("🌍 GLOBAL PULSE NEWS TERMINAL 🚀\n", style="bold magenta")
    welcome_text.append("Sleek, professional command-line editorial dashboard.", style="italic cyan")
    panel = Panel(welcome_text, border_style="bold blue", expand=False)
    console.print(panel)

def format_date(iso_str):
    if not iso_str:
        return "N/A"
    try:
        parts = iso_str.replace('Z', '').split('T')
        if len(parts) == 2:
            return f"{parts[0]} {parts[1][:5]}"
        return iso_str[:16]
    except Exception:
        return iso_str

def display_menu():
    console.print("\n[bold yellow]Menu Options:[/bold yellow]")
    console.print(" [1] 🚀 [bold]Spaceflight News[/bold] (Spaceflight API + NASA Feed)")
    console.print(" [2] 📝 [bold]Spaceflight Blogs[/bold]")
    console.print(" [3] 💻 [bold]Technology News[/bold] (TechCrunch + Hacker News)")
    console.print(" [4] 🔬 [bold]AI & Research Papers[/bold] (arXiv preprints)")
    console.print(" [5] 🌍 [bold]World News[/bold] (BBC World)")
    console.print(" [6] ✨ [bold]Show All Consolidated News[/bold]")
    console.print(" [r] 🔄 [bold]Force Refresh Feeds[/bold]")
    console.print(" [q] ❌ [bold]Exit[/bold]")

def show_news_table(articles, category_title):
    if not articles:
        console.print(f"\n[bold red]No articles found under {category_title}. Check your internet connection.[/bold red]")
        return None

    table = Table(title=f"\n📰 {category_title.upper()}", title_style="bold magenta", show_lines=True)
    table.add_column("No.", justify="center", style="cyan", no_wrap=True)
    table.add_column("Source", justify="center", style="green", no_wrap=True)
    table.add_column("Date", justify="center", style="yellow", no_wrap=True)
    table.add_column("Headline", style="bold white")

    for i, art in enumerate(articles[:15]): # Show top 15 in CLI
        table.add_row(
            str(i + 1),
            art.get("news_site", "N/A"),
            format_date(art.get("published_at")),
            art.get("title")
        )

    console.print(table)
    return articles[:15]

def interactive_loop():
    force_refresh = False
    all_news = fetch_all_news(force_refresh=force_refresh)
    
    while True:
        display_welcome()
        display_menu()
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "r", "q"], default="6")

        if choice == 'q':
            console.print("\n[bold magenta]Thank you for using GlobalPulse! Goodbye![/bold magenta]\n")
            sys.exit(0)
            
        elif choice == 'r':
            console.print("\n[bold yellow]🔄 Refreshing all news sources directly...[/bold yellow]")
            all_news = fetch_all_news(force_refresh=True)
            console.print("[bold green]✓ Done![/bold green]")
            continue

        category_map = {
            "1": ("space_articles", "Spaceflight Articles"),
            "2": ("space_blogs", "Spaceflight Blogs"),
            "3": ("tech_news", "Technology (TechCrunch + HN)"),
            "4": ("ai_research", "AI & Research (arXiv)"),
            "5": ("world_news", "World News (BBC)"),
            "6": ("all", "Consolidated News")
        }

        key, title = category_map[choice]
        articles = all_news[key]
        
        try:
            articles = sorted(articles, key=lambda x: x.get('published_at', ''), reverse=True)
        except Exception:
            pass

        listed_articles = show_news_table(articles, title)

        if listed_articles:
            console.print("\n[bold yellow]Interactive Options:[/bold yellow]")
            console.print(" • Enter a [bold cyan]number[/bold cyan] (e.g. [cyan]1[/cyan]-[cyan]{}[/cyan]) to view details & open in browser".format(len(listed_articles)))
            console.print(" • Press [bold cyan]Enter[/bold cyan] to return to the main menu")
            
            sub_choice = Prompt.ask("\nAction").strip()
            if sub_choice.isdigit():
                idx = int(sub_choice) - 1
                if 0 <= idx < len(listed_articles):
                    art = listed_articles[idx]
                    console.print("\n" + "=" * 80, style="blue")
                    console.print(f"[bold magenta]Title:[/bold magenta] {art['title']}")
                    console.print(f"[bold green]Source:[/bold green] {art['news_site']} | [bold yellow]Date:[/bold yellow] {format_date(art['published_at'])}")
                    console.print("-" * 80, style="dim white")
                    console.print(f"[bold white]Summary:[/bold white]\n{art['summary']}")
                    console.print("-" * 80, style="dim white")
                    console.print(f"[bold cyan]URL:[/bold cyan] {art['url']}\n")
                    
                    open_url = Prompt.ask("Would you like to open this article in your default browser? (y/n)", choices=["y", "n"], default="y")
                    if open_url == 'y':
                        console.print(f"[bold green]Opening browser to[/bold green]: {art['url']}")
                        webbrowser.open(art['url'])
                    console.print("=" * 80 + "\n", style="blue")
                    Prompt.ask("Press Enter to continue back to menu")
                else:
                    console.print("[bold red]Invalid article number![/bold red]")
                    time_sleep(1)

def time_sleep(sec):
    import time
    time.sleep(sec)

if __name__ == "__main__":
    try:
        interactive_loop()
    except KeyboardInterrupt:
        console.print("\n\n[bold magenta]Session closed. Goodbye![/bold magenta]\n")
