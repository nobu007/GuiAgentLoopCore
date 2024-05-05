"""Console script for gui_agent_loop_core."""

import click
from gui_agent_loop_core.gui_agent_loop_core import GuiAgentLoopCore


@click.command()
def main():
    """Main entrypoint."""
    click.echo("GuiAgentLoopCore")
    click.echo("=" * len("GuiAgentLoopCore"))
    click.echo("Core logic of GUI and LLM agent bridge, including loop and controls.")
    obj = GuiAgentLoopCore()
    obj.launch_server()


if __name__ == "__main__":
    main()  # pragma: no cover