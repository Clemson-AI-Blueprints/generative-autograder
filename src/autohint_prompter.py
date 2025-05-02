"""
Contains scripts for converting a list of autohint elements into a 
useful prompt for the LLM model.
"""

import enum
from typing import List, Dict


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



def hint_elements_to_prompt(hint_element_dicts: List[Dict]) -> str:
    hint_elements = [HintElement.from_dict(d) for d in hint_element_dicts]

    prompt = (
        "You are a helpful teaching assistant for an introductory programming class. "
        "Your task is to write a short, constructive hint that guides a student toward solving their problem "
        "without giving away the full answer.\n\n"
        "Below are pieces of information about the student's submission:\n"
    )

    for i, element in enumerate(hint_elements, 1):
        source = element.source.name.replace("_", " ").title()
        content = process_element(element).strip()
        context = f"\nContext: {element.context.strip()}" if element.context else ""
        prompt += f"\nElement {i}: ({source}){context}\n{content}\n"

    # 2048 - 100 is the max tokens, enforce than the length of the prompt in characters is less than (2048 - 100) / 4
    # 4 is the average number of tokens per character

    max_length = (1024 - 200) * 4
    if len(prompt) > max_length:
        prompt = prompt[:max_length]
    prompt += "\n\nLength Truncated\n\n"


    prompt += (
        "\n---\n"
        "Based on these elements, write a helpful hint for the student. "
        "Avoid directly giving the answer, and instead guide them to identify or fix the issue themselves."
    )

    return prompt
