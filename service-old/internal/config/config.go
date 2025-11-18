package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

type Config struct {
	Platform PlatformConfig
	Llm      LlmConfig
	Review   ReviewConfig
}

type PlatformConfig struct {
	Url           string
	Token         string
	WebhookSecret string
}

type LlmConfig struct {
	Model       string
	Temperature float64
	Timeout     int
	ApiKey      string
}

type ReviewConfig struct {
	MaxFiles                int
	MaxFileSizeCharacters   int
	ReviewPrompt            string
	BlockedFilePathKeywords []string
}

func LoadConfig() (*Config, error) {
	config := &Config{}
	if err := loadEnvVariables(config); err != nil {
		return nil, fmt.Errorf("failed to load environment variables: %w", err)
	}

	if err := validateConfig(config); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	return config, nil
}

func loadEnvVariables(config *Config) error {
	// Platform config
	config.Platform.Url = os.Getenv("PLATFORM_URL")
	config.Platform.Token = os.Getenv("PLATFORM_TOKEN")
	config.Platform.WebhookSecret = os.Getenv("PLATFORM_WEBHOOK_SECRET")

	// LLM config
	config.Llm.Model = getEnvOrDefault("LLM_MODEL", "codellama:7b")

	tempStr := getEnvOrDefault("LLM_TEMPERATURE", "0.3")
	temp, err := strconv.ParseFloat(tempStr, 64)
	if err != nil {
		return fmt.Errorf("invalid LLM_TEMPERATURE value: %w", err)
	}
	config.Llm.Temperature = temp

	timeoutStr := getEnvOrDefault("LLM_TIMEOUT", "300")
	timeout, err := strconv.Atoi(timeoutStr)
	if err != nil {
		return fmt.Errorf("invalid LLM_TIMEOUT value: %w", err)
	}
	config.Llm.Timeout = timeout

	config.Llm.ApiKey = getEnvOrDefault("LLM_API_KEY", "")

	// Review config
	maxFilesStr := getEnvOrDefault("REVIEW_MAX_FILES", "1000")
	maxFiles, err := strconv.Atoi(maxFilesStr)
	if err != nil {
		return fmt.Errorf("invalid REVIEW_MAX_FILES value: %w", err)
	}
	config.Review.MaxFiles = maxFiles

	maxSizeStr := getEnvOrDefault("REVIEW_MAX_FILE_SIZE", "10000")
	maxSize, err := strconv.Atoi(maxSizeStr)
	if err != nil {
		return fmt.Errorf("invalid REVIEW_MAX_FILE_SIZE value: %w", err)
	}
	config.Review.MaxFileSizeCharacters = maxSize

	blockedKeywordsStr := getEnvOrDefault("BLOCKED_FILE_PATH_KEYWORDS", "")
	if blockedKeywordsStr != "" {
		keywords := strings.Split(blockedKeywordsStr, ",")
		for i, keyword := range keywords {
			keywords[i] = strings.TrimSpace(keyword)
		}
		config.Review.BlockedFilePathKeywords = keywords
	}

	config.Review.ReviewPrompt = getEnvOrDefault("REVIEW_PROMPT",
		"As a senior software engineer and expert code reviewer, analyze the following code changes for correctness, clarity, maintainability, security, and performance, then provide concise, actionable feedback with specific improvement suggestions.")

	return nil
}

func getEnvOrDefault(key, defaultValue string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultValue
}

func validateConfig(config *Config) error {
	if config.Platform.Token == "" {
		return fmt.Errorf("platform token is required (set PLATFORM_TOKEN environment variable)")
	}
	if config.Platform.WebhookSecret == "" {
		return fmt.Errorf("platform webhook secret is required (set PLATFORM_WEBHOOK_SECRET environment variable)")
	}
	if config.Platform.Url == "" {
		return fmt.Errorf("platform URL is required (set PLATFORM_URL environment variable)")
	}

	return nil
}
