# Introduction to Neary

Neary is a chat-based app that helps users get more done with large language models. It goes a level deeper than ChatGPT and similar interfaces, with an intuitive UI for managing conversations across different contexts and a fresh take on leveraging tools and third-party integrations.

# Key Concepts

- Conversations are core to Neary. To create a Conversation, click the `+` button at the top right of the window or use the `/new` slash command.

- Conversations can be neatly organized into Spaces, akin to folders. Spaces can be accessed, created, edited, and deleted via the "stacks" icon at the bottom of the sidebar.

- Every Conversation possesses its own set of customizable settings. Access these by clicking the gear icon in the toolbar or by using the `/settings` slash command.

- Conversations can be further enhanced with Programs. Each Program provides special functionality to the conversation. Only one Program can be activated at a time and can be managed in Settings. Refer to the [current program list](#programs) for available programs.

# Programs

## Document Chat

This feature enables users to interact with their documents. It supports text files (plain-text and pdf) and website content. You can add these to the conversation and ask the AI questions about them. It's like having a knowledgeable friend who provides the answers you need.

### Usage

- Once this program is activated, a paperclip icon will appear in the toolbar. Click this to access Documents for the current conversation. From here, you can upload new documents or load them from the web via a URL.

- Neary can also load webpages directly from the conversation upon request.

- Once documents are added to the conversation, Neary will extract relevant information from your documents to answer your questions.

### Tips

- For optimal performance, limit the number of documents in a conversation.

## Calendar Chat

With Google Calendar API integration, users can inquire about their schedule and even have the AI schedule events for them.

### Usage

- This program requires Google OAuth credentials. Refer to [this link](docs/calendar_chat.md) for setup instructions.

- You'll be prompted to Login with Google after sending your first message to the conversation.

- When you ask about your calendar, Neary will use the `Get Calendar Events` tool to retrieve events from your calendar and answer your questions.

- Neary can also schedule events for you using the `Create Calendar Event` tool. Just ask!

### Tips

- If you haven't added your location to your profile, ask Neary to do it for you. This ensures Neary uses the correct timezone when scheduling events and answering questions.

## Support

This program initiates when Neary first starts. It aims to assist users in setting up their profile and answering questions about the app.

### Usage

- Feel free to ask any questions you have about Neary!

# Settings

Access a conversation's settings by clicking the gear icon in the toolbar. Here, you can set the conversation title, space, and program.

The subsequent section contains settings that influence the AI's behavior. If a program is activated, these settings will be adjusted accordingly. These are advanced settings and can be left untouched if you are unsure.

- **Instructions** - Also known as a "system message", these instructions allow you to guide the model's behavior.

- **Model** - Select the AI model you prefer for generating responses.

- **Token Limit** - This sets the maximum number of tokens to use when sending a new message to the model. Fewer tokens mean less context for the model, while more tokens provide more context but increase the request cost. The current maximum allowed is 8000 tokens.

- **Tool Approval Required** - If checked, the user will be prompted before any potentially destructive/irreversible actions are taken. Disable this option with caution!

# Slash Commands

Several slash commands are available:

- `/new` creates a new conversation
- `/delete` removes a conversation
- `/archive` archives a conversation's messages without deleting the conversation itself
- `/settings` opens the Settings for the selected conversation
- `/title` sets the conversation title, e.g. '/title My New Title'

# Toolbar Options

The toolbar, located above the chat box, includes:

- **Room to Grow**. When selected, incoming messages will start at the top of the window, rather than from the bottom.

- **View Archived Messages**. This option toggles the visibility of archived messages. Regardless of their visibility, archived messages are never included in the context when new messages are sent.

- **View Settings**. This option opens the Settings window for the current conversation.

- **More**. This option reveals a menu with additional options, like Archive Messages and Delete Conversation.