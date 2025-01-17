package main

// Package forms-api provides a for interacting with Google Forms API,
// allowing retrieval and management of form responses. It supports authentication via
// Google service accounts and exposes HTTP endpoints for accessing form data to local clients.
// We interact with select endpoints from the Google Forms API here:
// https://forms.googleapis.com/$discovery/rest?version=v1
// Then implement simple handles for the behaviors we want to allow local clients to perform.

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/forms/v1"
)

type Server struct {
	formsService *forms.Service
	suggestionsFormID string
	ballotFormID string
	suggestionsDataPath string
	ballotDataPath string
}

func newServer() (*Server, error) {
	ctx := context.Background()
	
	if err := godotenv.Load(); err != nil {
		log.Printf("Error loading .env file: %v", err)
	}

	// Load credentials file from the environment variable
	credentialsFile := os.Getenv("GOOGLE_CREDENTIALS_FILE")
	service, err := forms.NewService(ctx, option.WithCredentialsFile(credentialsFile))
	if err != nil {
		return nil, err
	}

	return &Server{
		formsService: service,
		suggestionsFormID: os.Getenv("SUGGESTIONS_FORM_ID"),
		ballotFormID: os.Getenv("BALLOT_FORM_ID"),
		suggestionsDataPath: os.Getenv("SUGGESTIONS_DATA_PATH"),
		ballotDataPath: os.Getenv("BALLOT_DATA_PATH"),
	}, nil
}

// downloadAndSaveResponses downloads form responses and saves them to the specified file path
func (s *Server) downloadAndSaveResponses(ctx context.Context, formID, filePath string) error {
	resp, err := s.formsService.Forms.Responses.List(formID).Context(ctx).Do()
	if err != nil {
		return fmt.Errorf("failed to list responses: %v", err)
	}

	// Marshal responses to JSON
	data, err := json.MarshalIndent(resp, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal responses: %v", err)
	}

	// Write to file
	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return fmt.Errorf("failed to write responses to file: %v", err)
	}

	return nil
}

// clearFormResponses clears all responses from the specified form
func (s *Server) clearFormResponses(ctx context.Context, formID string) error {
	_, err := s.formsService.Forms.Responses.BatchDelete(formID, &forms.BatchDeleteResponsesRequest{}).Context(ctx).Do()
	if err != nil {
		return fmt.Errorf("failed to clear form responses: %v", err)
	}
	return nil
}

// toggleFormAcceptingResponses enables or disables response collection for a form
func (s *Server) toggleFormAcceptingResponses(ctx context.Context, formID string, accepting bool) error {
	form, err := s.formsService.Forms.Get(formID).Context(ctx).Do()
	if err != nil {
		return fmt.Errorf("failed to get form: %v", err)
	}

	form.AcceptingResponses = accepting
	
	_, err = s.formsService.Forms.Update(formID, form).Context(ctx).Do()
	if err != nil {
		return fmt.Errorf("failed to update form: %v", err)
	}
	
	return nil
}

// updateBallotForm updates the ballot form with new questions based on suggestions
func (s *Server) updateBallotForm(ctx context.Context) error {
	// Read suggestions data
	data, err := os.ReadFile(s.suggestionsDataPath)
	if err != nil {
		return fmt.Errorf("failed to read suggestions data: %v", err)
	}

	var suggestions forms.ListFormResponsesResponse
	if err := json.Unmarshal(data, &suggestions); err != nil {
		return fmt.Errorf("failed to unmarshal suggestions: %v", err)
	}

	// Disable responses and save current ballot data
	if err := s.toggleFormAcceptingResponses(ctx, s.ballotFormID, false); err != nil {
		return err
	}

	// Save current ballot responses before clearing
	if err := s.downloadAndSaveResponses(ctx, s.ballotFormID, s.ballotDataPath); err != nil {
		return err
	}

	// Clear current ballot responses
	if err := s.clearFormResponses(ctx, s.ballotFormID); err != nil {
		return err
	}

	// Update ballot form with new questions from suggestions
	// This is a placeholder - actual implementation would depend on your specific form structure
	form, err := s.formsService.Forms.Get(s.ballotFormID).Context(ctx).Do()
	if err != nil {
		return fmt.Errorf("failed to get ballot form: %v", err)
	}

	// TODO: Process suggestions and update form structure
	// This would involve creating new questions/options based on the suggestions
	// The exact implementation depends on your form structure and requirements

	// Update the form
	_, err = s.formsService.Forms.Update(s.ballotFormID, form).Context(ctx).Do()
	if err != nil {
		return fmt.Errorf("failed to update ballot form: %v", err)
	}

	// Re-enable responses
	return s.toggleFormAcceptingResponses(ctx, s.ballotFormID, true)
}

// HandleSuggestionsReset handles the reset of suggestions form
func (s *Server) HandleSuggestionsReset(ctx context.Context) error {
	// First download and save current responses
	if err := s.downloadAndSaveResponses(ctx, s.suggestionsFormID, s.suggestionsDataPath); err != nil {
		return err
	}

	// Then clear the responses
	return s.clearFormResponses(ctx, s.suggestionsFormID)
}

func main() {
	server, err := newServer()
	if err != nil {
		log.Fatalf("Failed to create server: %v", err)
	}

	ctx := context.Background()

	// Example usage of the implemented functions
	if err := server.HandleSuggestionsReset(ctx); err != nil {
		log.Printf("Failed to reset suggestions: %v", err)
	}

	if err := server.updateBallotForm(ctx); err != nil {
		log.Printf("Failed to update ballot form: %v", err)
	}
}
