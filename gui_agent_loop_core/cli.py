"""Console script for gui_agent_loop_core."""

import click

from gui_agent_loop_core.gui_agent_loop_core import GuiAgentLoopCore
from gui_agent_loop_core.schema.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterBase,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatResponse,
    GuiAgentInterpreterChatResponseAny,
)


class DummyInterpreter(GuiAgentInterpreterBase):
    def __init__(self):
        pass

    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display: bool = False,
        stream: bool = False,
        blocking: bool = False,
    ) -> GuiAgentInterpreterChatResponseAny:
        content_res = request_core.content + "\ndisplay=" + display + "stream=" + stream + "blocking=" + blocking
        response = GuiAgentInterpreterChatResponse(content=content_res)
        return response


@click.command()
@click.option(
    "--interpreter", default=None, type=click.UNPROCESSED, callback=lambda _, __, value: value or DummyInterpreter()
)
def main(interpreter: GuiAgentInterpreterABC):
    """Main entrypoint."""
    click.echo("GuiAgentLoopCore")
    click.echo("=" * len("GuiAgentLoopCore"))
    click.echo("Core logic of GUI and LLM agent bridge, including loop and controls.")
    obj = GuiAgentLoopCore()
    obj.launch_server(interpreter)


if __name__ == "__main__":
    main()  # pragma: no cover
