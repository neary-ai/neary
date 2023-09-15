To setup the GitHub integration, you need to have a GitHub account and a set of OAuth credentials. Here's the step-by-step:

- Go to your GitHub account settings.

- In the left-side menu, click "Developer settings".

- On the next page, select "OAuth Apps".

- Click "New OAuth App".

- Fill in the "Application name", "Homepage URL", "Application description" (optional), and "Authorization callback URL". For the callback URL, use http://localhost:8000/api/oauth2/callback. Change your base URL to match your setup, if necessary.

- Click "Register Application". Your client ID and client secret will be shown.

Open your `settings.toml` file and add your client ID and client secret in the integrations section like so:

```
# OAuth credentials for GitHub integrations
github_client_id = "YOUR_CLIENT_ID"
github_client_secret = "YOUR_CLIENT_SECRET"
```

Remember to replace "YOUR_CLIENT_ID" and "YOUR_CLIENT_SECRET" with the client ID and client secret provided by GitHub.