To setup the Google Calendar integration, you need to have a Google Cloud account with the Google Calendar API enabled and a set of OAuth credentials. Here's the step-by-step:

1. Go to the [Google Cloud Console](console.developers.google.com).

2. If you haven't created a project yet, create a new one. If you already have a project, select it.

3. In the left-side menu, go to "APIs & Services" > "Library".

4. In the search bar, type "Google Calendar API" and select it from the list.

5. Click on "Enable" to enable the Google Calendar API for your project.

6. After enabling the API, go back to the left-side menu and navigate to "APIs & Services" > "Credentials".

7. Click "Create Credentials" and select "OAuth client ID".

8. Choose "Web application" for the application type, then choose a name for your client (any name will do). Finally, add `http://localhost:8000/api/oauth2/callback` as a URI under "Authorized redirect URIs". Change your base URL to match your setup, if necessary.

9.  Click "Create". Your client ID and client secret will be shown.

10. Open your `settings.toml` file and add your client ID and client secret in the integrations section like so:

```
# OAuth credentials for Google integrations
google_client_id = "YOUR_CLIENT_ID"
google_client_secret = "YOUR_CLIENT_SECRET"
```