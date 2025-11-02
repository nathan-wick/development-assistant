package reviewer

import (
	"context"
	"fmt"
	"strings"

	"github.com/nathan-wick/development-assistant/internal/config"
	"github.com/nathan-wick/development-assistant/internal/llm"
	"github.com/nathan-wick/development-assistant/internal/platform"
)

type Reviewer struct {
	llm    *llm.OllamaClient
	config *config.Config
}

func NewReviewer(llmClient *llm.OllamaClient, cfg *config.Config) *Reviewer {
	return &Reviewer{
		llm:    llmClient,
		config: cfg,
	}
}

func (r *Reviewer) ReviewPullRequest(ctx context.Context, event *platform.PullRequestEvent) (string, error) {
	var reviews []string

	fileCount := 0
	for _, file := range event.Files {
		if fileCount >= r.config.Review.MaxFiles {
			reviews = append(reviews, "⚠️ Too many files to review. Only reviewed the first files.")
			break
		}

		patchSize := len(file.Patch)
		if patchSize > r.config.Review.MaxFileSizeCharacters {
			reviews = append(reviews, fmt.Sprintf("⚠️ Skipped `%s`: File changes are too large to review. It contains %d characters, exceeding the %d-character limit.", file.Filename, patchSize, r.config.Review.MaxFileSizeCharacters))
			continue
		}

		if file.Status == "removed" {
			continue
		}

		review, err := r.reviewFile(file)
		if err != nil {
			reviews = append(reviews, fmt.Sprintf("❌ Error reviewing `%s`: %v", file.Filename, err))
			continue
		}

		if review != "" {
			reviews = append(reviews, fmt.Sprintf("### 📄 %s\n\n%s", file.Filename, review))
		}

		fileCount++
	}

	if len(reviews) == 0 {
		return "All changes look good! ✅", nil
	}

	return strings.Join(reviews, "\n\n---\n\n"), nil
}

func (r *Reviewer) reviewFile(file platform.FileChange) (string, error) {
	prompt := fmt.Sprintf("%s\n\nFile: %s\n\nChanges:\n```\n%s\n```\n\nProvide a brief review:",
		r.config.Review.ReviewPrompt,
		file.Filename,
		file.Patch,
	)

	response, err := r.llm.Generate(prompt)
	if err != nil {
		return "", err
	}

	return strings.TrimSpace(response), nil
}
