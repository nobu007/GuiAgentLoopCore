import enum


class AgentName(str, enum.Enum):
    AGENT_EXECUTOR = "agent_executor"
    LLM_PLANNER = "llm_planner"
    SUPERVISOR = "supervisor"
    THOUGHT = "thought"
    OTHER = "other"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class InterpreterState(str, enum.Enum):
    STATE_INIT = "init"
    STATE_RUNNING = "running"
    STATE_STOP = "stop"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
