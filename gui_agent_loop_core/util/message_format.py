import base64
from copy import deepcopy
from io import BytesIO

from PIL import Image

from gui_agent_loop_core.schema.schema import GuiAgentInterpreterChatMessage, GuiAgentInterpreterChatResponse


def format_response_confirmation(chunk_content, chunk: GuiAgentInterpreterChatResponse) -> (str, str):
    new_chunk_code = ""
    new_chunk_content = ""

    if chunk_content:
        if isinstance(chunk_content, dict):
            if chunk_content["format"] == "code":
                new_chunk_code = chunk_content["content"]
            elif chunk_content["format"] == "python":
                new_chunk_code = chunk_content["content"]
            else:
                print("TODO: format_response_confirmation no impl format=", chunk_content["format"])
                print("format_response CONFIRMATION chunk_content=", chunk_content)
                print("format_response CONFIRMATION full chunk=", chunk)
        else:
            new_chunk_content = chunk_content

    return new_chunk_code, new_chunk_content


def format_response(chunk: GuiAgentInterpreterChatResponse) -> GuiAgentInterpreterChatResponse:
    response_str = ""
    chunk_content = chunk.content
    chunk_type = chunk.type
    chunk_role = chunk.role
    chunk_format = chunk.format
    chunk_code = chunk.code  # working change(may nothing set)
    chunk_start = chunk.start
    chunk_end = chunk.end
    print(
        "format_response chunk_type=",
        chunk_type,
        ", chunk_role=",
        chunk_role,
        ", chunk_start=",
        chunk_start,
        ", chunk_end=",
        chunk_end,
    )
    # Message
    if chunk_type == GuiAgentInterpreterChatMessage.Type.MESSAGE:
        response_str = chunk_content
        if chunk_end:
            response_str += "\n"

    # Code
    if chunk_type == GuiAgentInterpreterChatMessage.Type.CODE:
        if chunk_start:
            response_str += "```python\n"
        if chunk_code:
            response_str += chunk_code
        elif chunk_content:
            # code may in chunk_content
            response_str += chunk_content
        if chunk_end:
            response_str += "\n```\n"

    # Output
    if chunk_type == GuiAgentInterpreterChatMessage.Type.CONFIRMATION:
        new_chunk_code, new_chunk_content = format_response_confirmation(chunk_content, chunk)
        if chunk_start:
            response_str += "```python\n"
        # TODO: fix CONFIRMATION format

        if new_chunk_code:
            response_str += new_chunk_code
        elif new_chunk_content:
            response_str += new_chunk_content
        if chunk_end:
            response_str += "```\n"

    # Console
    if chunk_type == GuiAgentInterpreterChatMessage.Type.CONSOLE:
        if chunk_start:
            response_str += "```python\n"
        if chunk_format == "active_line":
            console_content = chunk_content
            if console_content is None:
                response_str += "No output available on console."
        if chunk_format == "output":
            console_content = chunk_content
            response_str += console_content
        if chunk_end:
            response_str += "\n```\n"

    # Image
    if chunk_type == GuiAgentInterpreterChatMessage.Type.IMAGE:
        if chunk_start or chunk_end:
            response_str += "\n"
        else:
            image_format = chunk_format
            if image_format == GuiAgentInterpreterChatResponse.Format.BASE64_PNG:
                image_content = chunk_content
                if image_content:
                    image = Image.open(BytesIO(base64.b64decode(image_content)))
                    new_image = Image.new("RGB", image.size, "white")
                    new_image.paste(image, mask=image.split()[3])
                    buffered = BytesIO()
                    new_image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    response_str += f"![Image](data:image/png;base64,{img_str})\n"

    response = GuiAgentInterpreterChatResponse()
    response.content = response_str
    response.role = chunk_role
    response.code = chunk_code
    response.start = chunk_start
    response.end = chunk_end
    return response


def show_data_debug(data, name: str):
    """
    dataの構造をデバッグ表示する関数

    :data: 表示するメッセージ[str/list/dict]
    """
    print(f"#### show_data_debug({name}) ####")
    data_copy = deepcopy(data)
    show_data_debug_iter("", data_copy)
    print(f"#### show_data_debug({name}) end ####")


def show_data_debug_iter(indent: str, data):
    """
    メッセージまたは任意の構造の配列をデバッグ表示する関数

    :param data: 表示するデータ
    """
    indent_next = indent + "  "
    if isinstance(data, dict):
        show_data_debug_dict(indent_next, data)
    elif isinstance(data, list):
        show_data_debug_array(indent_next, data)
    else:
        show_data_debug_other(indent, data)


def show_data_debug_dict(indent, data):
    """
    再帰的にメッセージの辞書構造を表示する関数

    :param indent: インデント文字列
    :param data: 表示するデータの辞書
    """
    for k, v in data.items():
        print(f"{indent}dict[{k}]: ", end="")
        show_data_debug_iter(indent, v)


def show_data_debug_array(indent, data):
    """
    再帰的にメッセージの配列構造を表示する関数

    :param indent: インデント文字列
    :param data: 表示するデータの配列
    """
    for i, item in enumerate(data):
        print(f"{indent}array[{str(i)}]: ")
        show_data_debug_iter(indent, item)


def show_data_debug_other(indent, data):
    """
    配列と辞書でないデータを表示する関数

    :param indent: インデント文字列
    :param data: 表示するデータ
    """
    stype = str(type(data))
    s = str(data)
    print(f"{indent}{s[:20]}[type={stype}]")
