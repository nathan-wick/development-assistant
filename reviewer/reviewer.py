import asyncio
import logging

from configuration import Configuration
from llm.client import LlmClient
from platform_adapters.models import PullRequestEvent, FileChange

logger = logging.getLogger(__name__)


class Reviewer:

    def __init__(self, llm_client: LlmClient, configuration: Configuration):
        self.llm_client = llm_client
        self.configuration = configuration
        self.github_platform = None
        self.gitlab_platform = None

    def set_github_platform(self, platform): # type: ignore
        self.github_platform = platform # type: ignore

    def set_gitlab_platform(self, platform): # type: ignore
        self.gitlab_platform = platform # type: ignore

    async def post_comment(self, event: PullRequestEvent, message: str) -> None:
        try:
            if self.github_platform is not None: # type: ignore
                await self.github_platform.post_comment( # type: ignore
                    event.owner, event.repo, event.number, message
                )
            elif self.gitlab_platform is not None: # type: ignore
                await self.gitlab_platform.post_comment( # type: ignore
                    event.owner, event.number, message
                )
        except Exception as error:
            logger.error(f"Failed to post comment: {error}")

    def is_file_blocked(self, filename: str) -> bool:
        if not self.configuration.review.blocked_file_path_keywords:
            return False
        
        filename_lower = filename.lower()
        for keyword in self.configuration.review.blocked_file_path_keywords:
            if keyword.lower() in filename_lower:
                return True
        
        return False

    async def review_pull_request(self, event: PullRequestEvent) -> str:
        greeting_message = (
            "🤖 Hello! I'm reviewing your changes now. This may take a moment..."
        )
        await self.post_comment(event, greeting_message)

        reviews = [
            "# 🤖 Automated Review\n\n"
            "Please note that while I strive for accuracy, it's important to "
            "**verify all recommendations before implementing them**. This review "
            "is not meant to replace human review, but to accelerate it by "
            "catching common issues early."
        ]

        file_count = 0
        maximum_files = self.configuration.review.maximum_files

        for file in event.files:
            if file_count >= maximum_files:
                reviews.append(
                    f"🛑 Too many files to review. Only reviewed the first "
                    f"{maximum_files} files."
                )
                break

            if self.is_file_blocked(file.filename):
                reviews.append(
                    f"### 🚫 📄 {file.filename}\n\n"
                    f"Skipped review. This file contains a blocked keyword in its file path."
                )
                continue

            patch_size = len(file.patch)
            maximum_size = self.configuration.review.maximum_file_size_characters
            
            if patch_size > maximum_size:
                reviews.append(
                    f"### 🐘 📄 {file.filename}\n\n"
                    f"File changes are too large to review. It contains {patch_size} "
                    f"characters, exceeding the {maximum_size}-character limit."
                )
                continue

            if file.status == "removed":
                continue

            try:
                review = await self.review_file_with_progress(event, file)
                
                if not review or "no issues" in review.lower():
                    reviews.append(f"### ✅ 📄 {file.filename}\n\n{review}")
                else:
                    reviews.append(f"### ⚠️ 📄 {file.filename}\n\n{review}")
                
                file_count += 1
            except Exception as error:
                reviews.append(
                    f"### 🌋 📄 {file.filename}\n\n"
                    f"Error reviewing: {error}"
                )

        if len(reviews) <= 1:
            reviews.append("No changes to review.")

        return "\n\n---\n\n".join(reviews)

    async def review_file_with_progress(
        self, event: PullRequestEvent, file: FileChange
    ) -> str:
        review_task = asyncio.create_task(self.review_file(file))
        
        progress_interval = 5 * 60
        
        while True:
            try:
                review = await asyncio.wait_for(review_task, timeout=progress_interval)
                return review
            except asyncio.TimeoutError:
                progress_message = (
                    f"🔄 Still reviewing `{file.filename}`... "
                    f"Thanks for your patience!"
                )
                await self.post_comment(event, progress_message)
            except Exception as error:
                raise error

    async def review_file(self, file: FileChange) -> str:
        prompt = (
            f"{self.configuration.review.review_prompt}\n\n"
            f"File: {file.filename}\n\n"
            f"Changes:\n```\n{file.patch}\n```"
        )
        
        response = await self.llm_client.generate(prompt)
        return response.strip()