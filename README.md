# GuiAgentLoopCore

![Top Image](docs/images/top_image.png)

## Architecture Diagram

```mermaid
graph LR
    User((<i class="fas fa-user"></i>))---UI
    UI --- OpenGuiConnector
    OpenGuiConnector --- TaskAgent
    TaskAgent --- Agent1
    TaskAgent --- Agent2
    Agent1 --- LLM
    Agent2 --- LLM

    subgraph Interaction_Layer
    User((<i class="fas fa-user"></i>))
    UI(UI)
    end

    subgraph Processing_Layer
    OpenGuiConnector(OpenGuiConnector<br>- Event handling<br>- I/O conversion<br>- Multimodal support)
    end

    subgraph Task_Management_Layer
    TaskAgent(TaskAgent<br>- Task decomposition<br>- Subtask prioritization<br>- Agent assignment)
    end

    subgraph Execution_Layer
    Agent1(Agent1<br>Specialized role)
    Agent2(Agent2<br>Specialized role)
    end

    subgraph Language_Model_Layer
    LLM(LLM<br>Base language model)
    end

    style Interaction_Layer fill:#f9f,stroke:#333,stroke-width:2px,color:#333
    style Processing_Layer fill:#cff,stroke:#333,stroke-width:2px,color:#333
    style Task_Management_Layer fill:#ffc,stroke:#333,stroke-width:2px,color:#333
    style Execution_Layer fill:#cfc,stroke:#333,stroke-width:2px,color:#333
    style Language_Model_Layer fill:#ccf,stroke:#333,stroke-width:2px,color:#333


```

### Interaction_Layer - Processing_Layer

```mermaid
graph LR
    subgraph Interaction_Layer
        GuiAgentLoopCore(gui_agent_loop_core.py)
        GradioUI(Gradio UI)
        OpenAPISpec(OpenAPI Specification)
        InterpreterManager(InterpreterManager)
        AppLogic(Application Logic)

        GuiAgentLoopCore --> |Launch| GradioUI
        GradioUI --> |User Input| InterpreterManager
        InterpreterManager --> |Parse and Validate| OpenAPISpec
        OpenAPISpec --> |Formatted Data| AppLogic
        AppLogic --> |Result| OpenAPISpec
        OpenAPISpec --> |Formatted Data| InterpreterManager
        InterpreterManager --> |Format Response| GradioUI
    end

    style Interaction_Layer fill:#f9f,stroke:#333,stroke-width:2px,color:#333
```

[![pypi](https://img.shields.io/pypi/v/GuiAgentLoopCore.svg)](https://pypi.org/project/GuiAgentLoopCore/)
[![python](https://img.shields.io/pypi/pyversions/GuiAgentLoopCore.svg)](https://pypi.org/project/GuiAgentLoopCore/)
[![Build Status](https://github.com/nobu007/GuiAgentLoopCore/actions/workflows/dev.yml/badge.svg)](https://github.com/nobu007/GuiAgentLoopCore/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/nobu007/GuiAgentLoopCore/branch/main/graphs/badge.svg)](https://codecov.io/github/nobu007/GuiAgentLoopCore)

## What is GuiAgentLoopCore?

Core logic of GUI and LLM agent bridge, including loop and controls.

## Getting Started


### Prerequisites


### Installation


## Usage


* Documentation: <https://nobu007.github.io/GuiAgentLoopCore>
* GitHub: <https://github.com/nobu007/GuiAgentLoopCore>
* PyPI: <https://pypi.org/project/GuiAgentLoopCore/>
* Free software: MIT


## Features

* TODO

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.
