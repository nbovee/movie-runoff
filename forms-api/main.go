package main

// Package forms-api provides a for interacting with Google Forms API,
// allowing retrieval and management of form responses. It supports authentication via
// Google service accounts and exposes HTTP endpoints for accessing form data to local clients.
// We interact with select endpoints from the Google Forms API here:
// https://forms.googleapis.com/$discovery/rest?version=v1
// Then implement simple handles for the behaviors we want to allow local clients to perform.

// we will also implement handles that run POST to the endpoints expected of the Google Apps Script hooks on our forms for opening and closing form submissions
// that functionality is not present in the google forms api, so we roll our own

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	"google.golang.org/api/forms/v1"
	"google.golang.org/api/option"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: Error loading .env file: %v", err)
	}

	ctx := context.Background()
	
	// Create the Forms service with proper scopes
	client, err := forms.NewService(ctx, 
		option.WithScopes(
			"https://www.googleapis.com/auth/forms.body.readonly",
			"https://www.googleapis.com/auth/forms.responses.readonly",
		),
	)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}
	fmt.Println("Client created successfully")

	// Get form IDs from environment variables
	suggestFormID := os.Getenv("SUGGEST_FORM_ID")
	ballotFormID := os.Getenv("BALLOTS_FORM_ID")

	if suggestFormID == "" || ballotFormID == "" {
		log.Fatal("Form IDs not found in environment variables")
	}

	// Run suggestion form get request
	suggestForm, err := client.Forms.Get(suggestFormID).Do()
	if err != nil {
		log.Fatalf("Failed to get suggestion form: %v", err)
	}

	// Run ballot form get request
	ballotForm, err := client.Forms.Get(ballotFormID).Do()
	if err != nil {
		log.Fatalf("Failed to get ballot form: %v", err)
	}

	// Print form information
	fmt.Println("\nSuggest Form Details:")
	fmt.Printf("Form ID: %s\n", suggestForm.FormId)
	fmt.Printf("Title: %s\n", suggestForm.Info.Title)
	fmt.Printf("Document Title: %s\n", suggestForm.Info.DocumentTitle)
	fmt.Printf("Description: %s\n", suggestForm.Info.Description)

	fmt.Println("\nBallot Form Details:")
	fmt.Printf("Form ID: %s\n", ballotForm.FormId)
	fmt.Printf("Title: %s\n", ballotForm.Info.Title)
	fmt.Printf("Document Title: %s\n", ballotForm.Info.DocumentTitle)
	fmt.Printf("Description: %s\n", ballotForm.Info.Description)
}
