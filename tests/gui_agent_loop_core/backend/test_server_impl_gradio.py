from unittest.mock import Mock, patch

import gradio as gr
import pytest

from gui_agent_loop_core.backend.server_impl_gradio import _create_interface_chat
from gui_agent_loop_core.core.interpreter_manager import InterpreterManager
from gui_agent_loop_core.schema.backend.schema import GuiBackendType, GuiComponentName


# Test helper to create mock components
def create_mock_components():
    return {
        GuiComponentName.AGENT_NAME: gr.Textbox(),
        GuiComponentName.AGENT_NAME_RADIO: gr.Radio(choices=["Agent1", "Agent2"]),
        GuiComponentName.AGENT_IMAGE: gr.Image(),
        GuiComponentName.AGENT_STATE: gr.Textbox(),
        GuiComponentName.AGENT_SESSION: gr.Textbox(),
    }


# Test fixture for interpreter manager
@pytest.fixture
def mock_interpreter_manager():
    manager = Mock(spec=InterpreterManager)
    manager.create_session_instance = Mock(return_value="test_session")
    manager.chat_gradio_like = Mock(return_value="test_response")
    manager.auto_chat = Mock(return_value="auto_chat_response")
    manager.update_state_view = Mock(return_value="state_view_response")
    manager.update_agent_name_view = Mock(return_value="agent_name_response")
    manager.change_state_running = Mock(return_value="running_state")
    return manager


# Test case for verifying the type of components
def test_component_types(mock_interpreter_manager):
    components = create_mock_components()
    assert isinstance(components[GuiComponentName.AGENT_NAME], gr.Textbox)
    assert isinstance(components[GuiComponentName.AGENT_NAME_RADIO], gr.Radio)
    assert isinstance(components[GuiComponentName.AGENT_IMAGE], gr.Image)
    assert isinstance(components[GuiComponentName.AGENT_STATE], gr.Textbox)
    assert isinstance(components[GuiComponentName.AGENT_SESSION], gr.Textbox)


# Test case for verifying the interpreter manager methods
def test_interpreter_manager_methods(mock_interpreter_manager):
    assert mock_interpreter_manager.create_session_instance() == "test_session"
    assert mock_interpreter_manager.chat_gradio_like() == "test_response"
    assert mock_interpreter_manager.auto_chat() == "auto_chat_response"
    assert mock_interpreter_manager.update_state_view() == "state_view_response"
    assert mock_interpreter_manager.update_agent_name_view() == "agent_name_response"
    assert mock_interpreter_manager.change_state_running() == "running_state"


# Main test case
@patch('gui_agent_loop_core.backend.server_impl_gradio.get_gui_common_component')
def test_create_interface_chat(mock_get_components, mock_interpreter_manager):
    # Arrange
    mock_get_components.return_value = create_mock_components()

    # Act
    app, chat_iface, chatbot = _create_interface_chat(mock_interpreter_manager)

    # Assert
    assert isinstance(app, gr.Blocks)
    assert isinstance(chat_iface, gr.ChatInterface)
    assert isinstance(chatbot, gr.Chatbot)

    # Verify component creation
    mock_get_components.assert_called_once_with(
        GuiBackendType.GRADIO, mock_interpreter_manager.create_session_instance()
    )

    # Additional assertions can be added here for specific component properties


# Integration test for Gradio UI interactions
def test_gradio_ui_interactions(mock_interpreter_manager):
    app, chat_iface, chatbot = _create_interface_chat(mock_interpreter_manager)

    # Simulate user interaction
    user_message = "Hello, how are you?"
    history = []
    response = list(mock_interpreter_manager.chat_gradio_like(user_message, history))

    # Assert the response
    assert response == ["test_response"]
    assert history == [{"role": "user", "content": user_message}, {"role": "assistant", "content": "test_response"}]


# Test for streaming response from LLM
def test_streaming_response_from_llm(mock_interpreter_manager):
    app, chat_iface, chatbot = _create_interface_chat(mock_interpreter_manager)

    # Simulate streaming response
    user_message = "Stream this response"
    history = []
    response_stream = mock_interpreter_manager.chat(user_message, is_auto=False)

    # Collect the streaming response
    response = []
    for chunk in response_stream:
        response.append(chunk)

    # Assert the response
    assert response == ["test_response"]
    assert history == [{"role": "user", "content": user_message}, {"role": "assistant", "content": "test_response"}]


# Test for synchronous response from LLM
def test_synchronous_response_from_llm(mock_interpreter_manager):
    app, chat_iface, chatbot = _create_interface_chat(mock_interpreter_manager)

    # Simulate synchronous response
    user_message = "Give me a synchronous response"
    history = []
    response = list(mock_interpreter_manager.chat(user_message, is_auto=False))

    # Assert the response
    assert response == ["test_response"]
    assert history == [{"role": "user", "content": user_message}, {"role": "assistant", "content": "test_response"}]


def main():
    """Test runner function for local testing"""
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    main()
