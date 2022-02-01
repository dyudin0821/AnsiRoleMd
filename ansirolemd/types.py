from dataclasses import dataclass


@dataclass
class SupportPlatform:
    os: str = ""
    version: str = "ALL"


@dataclass
class Varible:
    m_name: str = ""
    m_required: str = "No"
    m_default: str = "-"
    m_description: str = "Please fill the description."
    m_value: str = "-"
    m_example: str = "Please fill the example."
