# src/cli/main.py
import click
import logging
import os
from rich.console import Console
from rich.markdown import Markdown
from src.agent.core import CloudOpsAgent
from src.config.settings import settings

console = Console()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@click.command()
@click.argument("query", required=False)
@click.option("--execute", is_flag=True, help="Execute generated commands automatically")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--provider", default=None, help="LLM provider: gemini, groq, openai (default: gemini)")
@click.option("--model", default=None, help="Override model name for the selected provider")
def main(query, execute, debug, provider, model):
    """CloudOps Buddy - Your DevOps AI Assistant with multi‑provider support."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if execute:
        # Inform the user, but do NOT override settings.dry_run globally
        console.print("[yellow]⚠️  Execute mode enabled – commands will be run.[/]")

    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    try:
        if provider == "groq":
            from src.agent.llm_client_groq import GroqClient
            model_name = model or settings.groq_model
            console.print(f"[blue]Using Groq model: {model_name}[/]")
            llm_client = GroqClient(model_name=model_name)

        elif provider == "openai":
            from src.agent.llm_client_openai import OpenAIClient
            model_name = model or settings.openai_model
            console.print(f"[blue]Using OpenAI model: {model_name}[/]")
            llm_client = OpenAIClient(model_name=model_name)

        else:  # gemini
            from src.agent.llm_client import GeminiClient
            model_name = model or settings.gemini_model
            console.print(f"[blue]Using Gemini model: {model_name}[/]")
            llm_client = GeminiClient(model_name=model_name)

    except Exception as e:
        console.print(f"[red]Failed to initialize provider: {e}[/]")
        return

    # Pass the execute_mode flag to the agent
    agent = CloudOpsAgent(llm_client=llm_client, execute_mode=execute)

    if query:
        try:
            response = agent.chat(query)
            console.print(Markdown(response))
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
    else:
        console.print("[bold green]🚀 CloudOps Buddy started[/]")
        console.print("Type 'exit' or 'quit' to quit.\n")
        while True:
            user_input = click.prompt("> ", type=str)
            if user_input.lower() in ["exit", "quit"]:
                break
            try:
                response = agent.chat(user_input)
                console.print(Markdown(response))
            except Exception as e:
                console.print(f"[red]Error: {e}[/]")
            console.print("\n" + "-" * 40 + "\n")

if __name__ == "__main__":
    main()