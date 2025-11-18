import os
from dataclasses import dataclass
from typing import List


@dataclass
class PlatformConfiguration:
    url: str
    token: str
    webhook_secret: str


@dataclass
class LlmConfiguration:
    model: str
    temperature: float
    timeout: int
    api_key: str


@dataclass
class ReviewConfiguration:
    maximum_files: int
    maximum_file_size_characters: int
    review_prompt: str
    blocked_file_path_keywords: List[str]


@dataclass
class Configuration:
    platform: PlatformConfiguration
    llm: LlmConfiguration
    review: ReviewConfiguration


def load_configuration() -> Configuration:
    configuration = Configuration(
        platform=_load_platform_configuration(),
        llm=_load_llm_configuration(),
        review=_load_review_configuration()
    )
    
    _validate_configuration(configuration)
    return configuration


def _load_platform_configuration() -> PlatformConfiguration:
    return PlatformConfiguration(
        url=os.getenv("PLATFORM_URL", ""),
        token=os.getenv("PLATFORM_TOKEN", ""),
        webhook_secret=os.getenv("PLATFORM_WEBHOOK_SECRET", "")
    )


def _load_llm_configuration() -> LlmConfiguration:
    temperature_string = os.getenv("LLM_TEMPERATURE", "0.1")
    try:
        temperature = float(temperature_string)
    except ValueError as error:
        raise ValueError(f"Invalid LLM_TEMPERATURE value: {error}")
    
    timeout_string = os.getenv("LLM_TIMEOUT", "300")
    try:
        timeout = int(timeout_string)
    except ValueError as error:
        raise ValueError(f"Invalid LLM_TIMEOUT value: {error}")
    
    return LlmConfiguration(
        model=os.getenv("LLM_MODEL", "codellama:7b"),
        temperature=temperature,
        timeout=timeout,
        api_key=os.getenv("LLM_API_KEY", "")
    )


def _load_review_configuration() -> ReviewConfiguration:
    maximum_files_string = os.getenv("REVIEW_MAX_FILES", "1000")
    try:
        maximum_files = int(maximum_files_string)
    except ValueError as error:
        raise ValueError(f"Invalid REVIEW_MAX_FILES value: {error}")
    
    maximum_size_string = os.getenv("REVIEW_MAX_FILE_SIZE", "10000")
    try:
        maximum_size = int(maximum_size_string)
    except ValueError as error:
        raise ValueError(f"Invalid REVIEW_MAX_FILE_SIZE value: {error}")
    
    blocked_keywords_string = os.getenv("BLOCKED_FILE_PATH_KEYWORDS", "")
    blocked_keywords = []
    if blocked_keywords_string:
        blocked_keywords = [
            keyword.strip() 
            for keyword in blocked_keywords_string.split(",")
        ]
    
    default_prompt = (
        "You are a first-pass code reviewer performing a quick analysis. Examine code changes for security "
        "vulnerabilities, bugs, errors, typos, and code quality issues. Ignore complex business logic, architecture, "
        "organization, performance, user experience, and requirements implementation. If you find issues you're "
        "confident about, provide super concise, actionable feedback with specific fixes. If you find no issues, "
        "respond with exactly: \"No issues detected.\" Do not provide commentary, explanations, or positive feedback "
        "when there are no issues. Your job is to find problems, not to validate correct code."
    )
    
    return ReviewConfiguration(
        maximum_files=maximum_files,
        maximum_file_size_characters=maximum_size,
        review_prompt=os.getenv("REVIEW_PROMPT", default_prompt),
        blocked_file_path_keywords=blocked_keywords
    )


def _validate_configuration(configuration: Configuration) -> None:
    if not configuration.platform.token:
        raise ValueError(
            "platform token is required (set PLATFORM_TOKEN environment variable)"
        )
    
    if not configuration.platform.webhook_secret:
        raise ValueError(
            "platform webhook secret is required "
            "(set PLATFORM_WEBHOOK_SECRET environment variable)"
        )
    
    if not configuration.platform.url:
        raise ValueError(
            "platform URL is required (set PLATFORM_URL environment variable)"
        )