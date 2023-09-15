<h1 align="center">
  <br>
  <img src="images/neary-icon.png" width="75">
  <br>
  User Guide
  <br>
</h1>

Welcome! This guide will walk you through the process of setting up your Neary instance. Along the way, you'll learn about Neary's most important features and how to use them to get more done with LLMs. Let's get started.

## Installation

First things first, take a look at our [installation options](../README.md#installation) and install Neary using whatever method you'd like. For the purposes of this guide, we'll assume you're using the default setup, with an OpenAI chat model and the Neary app available at http://localhost:8000.

Make sure you edit `settings.toml` to include your OpenAI key, and add your credentials for any third-party integrations you want to use under the `[integrations]` section.

Once you've started Neary, navigate to http://localhost:8000.

The first time you load Neary you'll be greeted with a screen asking you to register with an email address and a password. Go ahead and do that. This information is only used for authentication purposes.

> [!NOTE]  
> Authentication is enabled by default. If you'd like to disable it altogether, set `enable_auth` to false in `settings.toml`.

## Getting Setup

Once you create your account, you'll be redirected to the app, where you'll be greeted with a chatbox that's just *begging* to be typed in. But wait! Before you do that, let's do a bit of setup.

### User Profile

Click the user icon &nbsp;<img src="images/account-icon.png">&nbsp; at the bottom of the sidebar on the left-hand side of the screen. This will take you to your Manage Accoutn page, and the first thing you'll see is your user profile.

You don't *have* to fill out your profile, but it's a good idea. Information you add to your profile will automatically be added to context in any conversation where the `Insert User Profile` snippet is active (more on snippets later).

We recommend adding at least your name and location to start. You can always add new items to your profile later.

> [!NOTE]  
> If you have the 'Update User Profile' tool enabled in your conversation, just ask and Neary will update your profile for you!

Excellent. Now Neary knows who you are. Or who you purport to be 😎.

### Spaces

Spaces in Neary are folder-like containers for your conversations. They help you stay organized and find conversations more quickly. Click the grid icon &nbsp;<img src="images/spaces-icon.png">&nbsp; to access your spaces. Here, you can add, edit and delete spaces as needed.

When a new conversation is created, it will be assigned to whatever space is currently active. You can change a conversation's space at anytime.

## Let's Talk About Conversations

Conversations are core to Neary. We've designed them to be **super customizable** and **highly modular** because we feel this is the best way to take advantage of the range of use cases large language models provide.

Let's take a spin through a conversation to see what makes them tick. New conversations can be created in three ways:

1. Click the `New Conversation` button in any empty space
2. Click the `+` icon in the nav bar
3. Use the `/new` slash command

After you create a new conversation, you'll be greeted with an "empty state" that includes fields to set the title, space and preset for your conversation.

>[!NOTE]  
> Slash commands can help you manage a conversation on the fly:
>
> `/new` creates a new conversation  
> `/title [some title]` sets a conversation's title  
> `/archive` archives messages in a conversation  
> `/delete` deletes a conversation  

### Conversation Presets

Since the title and space settings should be obvious by name, let's dig into presets. **Presets are essentially pre-packaged "recipes" that imbue your conversation with a set of abilities**. To illustrate this, let's look at a couple of presets Neary ships with out-of-the-box:

- `Just Chatting` transforms the AI into a friendly conversation partner capable of tailoring responses to your profile and remembering important tidbits, regardless of context.

- `Calendar Chat` turns the AI into a personal assistant, capable of retrieving events on your Google Calendar, scheduling events on your behalf, and brainstorming reasons why you can't make a meeting you're dreading.

- `Document Chat` turns the AI into a smart friend who is happy to read documents and webpages on your behalf, and then answer all of your questions.

We'll get into *how* this happens in a moment, but for now just remember you can radically change the nature and function of any conversation simply by selecting a new preset.

### The Chat Stack

Next, let's checkout the **Chat Stack**. After you create a new conversation, click through on the current preset, or click the stacks icon &nbsp;<img src="images/stack-icon.png">&nbsp;  in the toolbar to view that conversation's chat stack.

The Chat Stack constructs the context for, and capabilities of, your conversation. Here's a brief overview of each setting:

- Changing the `Preset` will load a new set of instructions, snippets and tools into the conversation.

- The `Instructions`, or system message, set the "tone" for the conversation and let the AI know how it should behave.

- `Snippets` are pieces of context that are automatically injected into the conversation behind the scenes. For example, you can enable the `Insert User Profile` snippet to ensure the AI is aware of the information in your profile at all times.

- `Tools` are actions the AI is allowed to take on your behalf. The AI "chooses" which tool to use, if any, based on the chat context. For example, the `Update User Profile` tool allows the AI to update your profile information for you, right in the chat.

And this is where it gets *really fun*. You can mix and match snippets and tools to create your perfect conversation. When you've done it, you can save your custom chat as a preset for one-click access.

Snippets and Tools are packaged together in `Plugins`, but we'll get to those in a moment. For now, let's explore the second set of knobs you have for customizing conversations.

> [!WARNING]  
> When it comes to large language models, context is king. Packing a conversation with unrelated snippets and tools will not only result in worse performance, it'll cost you more money! Instead, it's better to create separate, narrowly focused conversations and switch between them as needed.

### AI Settings

The other part of a conversation's "anatomy" is the AI--or chat model--settings. To access these, click the settings icon &nbsp;<img src="images/settings-icon.png">&nbsp; in the chatbox toolbar.

You're likely familiar with most of these settings, so we'll just touch on a couple for now:

- `API Type` defaults to OpenAI, but it can be set to a custom endpoint, whether that's a local model or model somewhere in the cloud. Just make sure the endpoint uses the OpenAI API schema and configure your endpoint in the `settings.toml` file.

- `Input Tokens` is a setting Neary uses locally to determine how many tokens of context to pass to the chat model. The user message, system message, and enabled tools and snippets are prioritized first, then context from past messages is used for the remaining tokens.

- `Max Tokens` is a parameter that OpenAI's chat endpoint no longer requires (you can keep it at 0 / infinite), but you may need to set this to a real number if you're using a custom model and getting very short responses.

>[!NOTE]  
>You can see the "raw" context and token count from your most recent exchange by selecting the `Show X-Ray` option from the chatbox toolbar.

### Chat Stack + AI Settings = A Preset

And there you have it. A preset is a combination of a conversation's Chat Stack and AI Settings. Taken together, they can unlock varied and powerful applications of large language models.

To really understand the power of presets in Neary, though, we need to take a look at one more thing.

## Using Plugins & Integrations

Plugins and integrations are related, but decoupled for a reason.

- Plugins bundle together a set of themed functions (Snippets and Tools) that can be added to a conversation's Chat Stack.

- Integrations are third-party services that can be connected to in order to enhance plugins with outside data and/or functionality.

To see them for yourself, click the gear icon &nbsp;<img src="images/setup-icon.png">&nbsp; at the bottom of the sidebar.

### Plugins

Plugins are split up into two lists, `Enabled Plugins` and `Available Plugins`. When a plugin is enabled, the Snippets and Tools bundled into that plugin will be available for use in your Chat Stack.

If you're not using a plugin or its functions, you can disable it to keep your list of available Snippets and Tools tidy.

>[!NOTE]  
>If you select a preset that requires a disabled plugin, that plugin will be enabled automatically.

From here, you can drill down into the details of plugin to see:

- What Tools and Snippets the plugin provides
- What settings and configuration options the plugin has
- What integrations the plugin requires

On that note, let's take a look at the final piece of the puzzle.

### Integrations

Selecting the `Integrations` tab on the setup screen will show you a list of available integrations.

When you click `Connect` on one of those integrations, you'll either be asked to authenticate your account via an OAuth flow or you'll be asked for an API key. It just depends on how the third-party is setup.

When complete, the integration will show in the 'Connected Integrations' list and that integration will now be available in supported plugins.

### Writing Your Own Plugins

If you're comfortable with Python, writing your own plugins is easy (and fun!) [Check out this tutorial](./write_a_plugin.md) for an in-depth guide on creating your first plugin.

## What's Next

With what you've learned here, you're now in a position to harness the full power of Neary. Time to experiment! Here's a list of things to consider:

- If you haven't already, fill out your User Profile
- Create some Spaces to organize your conversations
- Create a few conversations and use a different preset in each
- Examine how the preset works by viewing the AI settings and Chat Stack
- Create your own presets and share them with the community
- Figure out how you can break Neary and posted an Issue

Happy chatting!