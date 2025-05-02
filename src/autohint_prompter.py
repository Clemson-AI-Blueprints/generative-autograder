"""
Contains scripts for converting a list of autohint elements into a 
useful prompt for the LLM model.
"""

import enum
from typing import List, Dict
from transformers import AutoTokenizer


class HintSource(enum.Enum):
    ERROR_MESSAGE = 0
    STUDENT_CODE = 1
    SAMPLE_CODE = 2
    FUNCTION_SIGNATURE = 3
    TEST_CASE_NAME = 4
    INPUT_FILE = 5
    TEST_USER_INPUT = 15  # User input for the test cases
    SAMPLE_OUTPUT = 6
    PROJECT_DIRECTIONS = 7
    PROJECT_DESCRIPTION = 8
    MISSING_PHRASE = 9
    EXPECTED_PHRASE = 14
    TIMED_OUT = 10
    STUDENT_OUTPUT = 11
    GENERAL = 12
    TEST_CASE = 13
    SHELL_COMMAND = 16
    COMPILE_STEP = 17
    FILE = 18
    FINAL_CONTEXT = 19



class HintElement:
    def __init__(
        self,
        content: str,
        source: HintSource,
        context: str = None,
        relevance: float = 1.0,
        metadata: dict = None,
    ):
        self.content = content
        self.source = source
        self.context = context
        self.relevance = relevance
        self.metadata = metadata

    def to_dict(self):
        return {
            "content": self.content,
            "source": self.source.name,
            "context": self.context,
            "relevance": self.relevance,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: dict):
        return HintElement(
            data["content"],
            HintSource[data["source"]],
            data["context"],
            data["relevance"],
            data["metadata"],
        )
    

def process_element(hint_element: HintElement) -> str:
    """
    If it's code, then compact the code block by removing new lines, spaces, and tabs
    """

    if hint_element.source in {HintSource.STUDENT_CODE, HintSource.SAMPLE_CODE, HintSource.FUNCTION_SIGNATURE}:
        # Remove new lines and extra spaces
        content = hint_element.content.replace("\n", " ").replace("\t", " ").strip()
        return f"```\n{content}\n```"
    elif hint_element.source == HintSource.TEST_CASE_NAME:
        return f"Test case name: {hint_element.content}"
    elif hint_element.source == HintSource.TEST_CASE:
        return f"Test case: {hint_element.content}"
    else:
        return hint_element.content


MAX_INPUT_TOKENS = 850

def hint_elements_to_prompt(hint_element_dicts: List[Dict]) -> str:
    hint_elements = [HintElement.from_dict(d) for d in hint_element_dicts]

    system_prompt = (
        "You are a helpful teaching assistant for a college programming course. "
        "The student is struggling with an assignment. Your goal is to offer a specific and concise hint "
        "that helps them identify their mistake or improve their approach without giving away the full solution. "
        "Use the context below to inform your hint."
    )

    instructions = (
        "Write a clear and concise hint for the student using the relevant context provided. "
        "Focus on guiding the student to understand what might be wrong or what to think about, "
        "but do not fix the code or solve the problem for them."
    )

    body = ""
    for i, hint_element in enumerate(hint_elements):
        element_str = f"\n### Element {i + 1}\n"
        element_str += f"**Content**:\n{process_element(hint_element)}\n"
        element_str += f"**Source**: {hint_element.source.name}\n"
        element_str += f"**Context**: {hint_element.context or 'None'}\n"
        element_str += f"**Relevance**: {hint_element.relevance}\n"

        # Token budget
        if len(system_prompt + body + element_str) / 3 > MAX_INPUT_TOKENS:
            print("Warning: The prompt is too long. Skipping this hint element.")
            continue
        body += element_str

    if not body:
        body = "\nNo elements could be included due to length limits."

    return (
        f"<|system|>\n{system_prompt}\n"
        f"<|user|>\n{instructions}\n{body.strip()}\n"
        f"<|assistant|>"
    )
