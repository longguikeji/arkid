package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"path"
	"text/template"

	"golang.org/x/oauth2"
)

var (
	ClientID     = os.Getenv("OAUTH_CLIENT_ID")
	ClientSecret = os.Getenv("OAUTH_CLIENT_SECRET")
	RedirectURL  = os.Getenv("OAUTH_REDIRECT_URL")
	SPAuthURL = os.Getenv("OAUTH_SP_AUTH_URL")
	SPTokenURL = os.Getenv("OAUTH_SP_TOKEN_URL")
)

var (
	config = oauth2.Config{
		ClientID:     ClientID,
		ClientSecret: ClientSecret,
		Scopes:       []string{"read", "write"},
		RedirectURL:  RedirectURL,
		// This points to our Authorization Server
		// if our Client ID and Client Secret are valid
		// it will attempt to authorize our user
		Endpoint: oauth2.Endpoint{
			AuthURL:  SPAuthURL,
			TokenURL: SPTokenURL,
		},
	}
)

// LoginPage ...
func LoginPage(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Loginpage Hit!")
	u := config.AuthCodeURL("xyz")
	http.Redirect(w, r, u, http.StatusFound)
}

type Content struct {
	Token string
	Next  string
}

// Authorize ...
func Authorize(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	state := r.Form.Get("state")
	if state != "xyz" {
		http.Error(w, "State invalid", http.StatusBadRequest)
		return
	}

	code := r.Form.Get("code")
	if code == "" {
		http.Error(w, "Code not found", http.StatusBadRequest)
		return
	}

	token, err := config.Exchange(context.Background(), code)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	content := Content{Token: token.AccessToken, Next: "/"}
	fp := path.Join("templates", "oauth.html")
	tmpl, err := template.ParseFiles(fp)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if err := tmpl.Execute(w, content); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func main() {

	// 1 - Any unauthenticated request will redirect to Login
	http.HandleFunc("/oneid/login", LoginPage)

	// 2 - This displays our state, code and
	// token and expiry time that we get back
	// from our Authorization server
	http.HandleFunc("/oauth2", Authorize)

	// 3 - We start up our Client on port 9094
	log.Println("Client is running at 9094 port.")
	log.Fatal(http.ListenAndServe(":9094", nil))
}
