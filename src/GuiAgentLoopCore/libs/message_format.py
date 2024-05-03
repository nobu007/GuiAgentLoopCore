import base64
from copy import deepcopy
from io import BytesIO

from PIL import Image


def format_response(chunk):
    response = ""
    chunk_type = chunk.get("type", "")
    chunk_role = chunk.get("role", "")
    chunk_start = chunk.get("start", False)
    chunk_end = chunk.get("end", False)
    # print(
    #     "format_response chunk_type=",
    #     chunk_type,
    #     ", chunk_role=",
    #     chunk_role,
    #     ", chunk_start=",
    #     chunk_start,
    #     ", chunk_end=",
    #     chunk_end,
    # )
    # Message
    if chunk_type == "message":
        response += chunk.get("content", "")
        if chunk_end:
            response += "\n"

    # Code
    if chunk_type == "code":
        if chunk_start:
            response += "```python\n"
        response += chunk.get("content", "")
        if chunk_end:
            response += "\n```\n"

    # Output
    if chunk_type == "confirmation":
        if chunk_start:
            response += "```python\n"
        response += chunk.get("content", {}).get("code", "")
        if chunk_end:
            response += "```\n"

    # Console
    if chunk_type == "console":
        if chunk_start:
            response += "```python\n"
        if chunk.get("format", "") == "active_line":
            console_content = chunk.get("content", "")
            if console_content is None:
                response += "No output available on console."
        if chunk.get("format", "") == "output":
            console_content = chunk.get("content", "")
            response += console_content
        if chunk_end:
            response += "\n```\n"

    # Image
    if chunk_type == "image":
        if chunk_start or chunk_end:
            response += "\n"
        else:
            image_format = chunk.get("format", "")
            if image_format == "base64.png":
                image_content = chunk.get("content", "")
                if image_content:
                    image = Image.open(BytesIO(base64.b64decode(image_content)))
                    new_image = Image.new("RGB", image.size, "white")
                    new_image.paste(image, mask=image.split()[3])
                    buffered = BytesIO()
                    new_image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    response += f"![Image](data:image/png;base64,{img_str})\n"

    return response, chunk_type, chunk_role, chunk_start, chunk_end


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
