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
    FILE = 5
    SAMPLE_OUTPUT = 6
    PROJECT_DIRECTIONS = 7
    PROJECT_DESCRIPTION = 8
    EXPECTED_PHRASE = 9
    TIMED_OUT = 10
    SHELL_COMMAND = 11



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

def hint_elements_to_prompt(hint_element_dicts: List[Dict]):
    hint_elements = [HintElement.from_dict(hint_element_dict) for hint_element_dict in hint_element_dicts]
    prompt = "Your job is to generate a hint that will help a student with their programming assignment."
    prompt += "Below are elements that you can pull from to help you generate a hint:\n"

    for i, hint_element in enumerate(hint_elements):
        prompt += f"\n# Element {i + 1}\n"
        prompt += f"## Content\n {hint_element.content}\n"
        prompt += f"## Source\n {hint_element.source.name}\n"
        prompt += f"## Context\n {hint_element.context}\n"
        prompt += f"## Relevance\n {hint_element.relevance}\n"

    prompt += "\nProvide a useful hint that won't give away the answer. The hint should be relevant to the student's current problem."

    return prompt