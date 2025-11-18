package llm

import (
	"context"
	"fmt"
	"time"

	"google.golang.org/genai"
)

type GeminiClient struct {
	apiKey      string
	model       string
	temperature float64
	timeout     time.Duration
}

func NewGeminiClient(apiKey, model string, temperature float64, timeout int) *GeminiClient {
	return &GeminiClient{
		apiKey:      apiKey,
		model:       model,
		temperature: temperature,
		timeout:     time.Duration(timeout) * time.Second,
	}
}

func (c *GeminiClient) Generate(prompt string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), c.timeout)
	defer cancel()

	client, err := genai.NewClient(ctx, &genai.ClientConfig{APIKey: c.apiKey})
	if err != nil {
		return "", fmt.Errorf("failed to create Gemini client: %w", err)
	}

	// TODO Add temperature as option
	result, err := client.Models.GenerateContent(
		ctx,
		"gemini-2.5-flash",
		genai.Text(prompt),
		nil,
	)
	if err != nil {
		return "", fmt.Errorf("gemini generation failed: %w", err)
	}

	return result.Text(), nil
}
