<h1 align="center">
  <br>
  <img src="images/neary-icon.png" width="75">
  <br>
  User Guide
  <br>
</h1>

Ready to get cozy with Neary? Follow along as you setup your Neary account to get full acquainted.

## Configuration & Installation

First things first, install Neary using your preferred [installation option](../README.md#installation). For the purposes of this guide, we'll assume you're using the default setup, with Neary available at http://localhost:8000.

Make sure you edit `settings.toml` to include your OpenAI key and/or custom endpoint, and add your credentials for any third-party integrations you want to use under the `[integrations]` section.

Once you've started Neary, head to http://localhost:8000 to create an account.

> [!NOTE]  
> Authentication is enabled by default. If you'd like to disable it altogether, set `enable_auth` to false in `settings.toml`.

The first time you load Neary you'll be greeted with a screen asking you to register with an email and a password. Enter whatever you'd like. This information is only used for authentication purposes.

## Setup Your Space

And you're in! Before you get to typing (you'll have plenty of time for that, trust me), let's do a bit of setup.

### Your User Profile

Click the &nbsp;<span style="background-color: #808080; padding: 1px; padding-top: 4px; border-radius: 15%;"><img src="https://api.iconify.design/heroicons/user-solid.svg"></span>&nbsp; icon at the bottom of the sidebar. This will take you to your Account Settings, and the first thing you'll see is your user profile.



You don't *have* to fill out your profile, but it's a good idea. Information you add to your profile will automatically be added to context in any conversation where the `Insert User Profile` snippet is active.

We recommend adding at least your name and location to start. You can always add new items to your profile later.

> [!NOTE]  
> If you have the 'Update User Profile' tool enabled in your conversation, just ask and Neary will update your profile for you!

Excellent. Now Neary knows who you are. Or who you purport to be.

### Spaces

Spaces in Neary are like folders for your conversations. They help you stay organized and find what you're looking for more quickly. Click the <img src="https://api.iconify.design/heroicons/squares-2x2-solid.svg"> icon to access your spaces. You can add, edit and remove spaces at any time.

You can add a conversation to a space simply by making sure the space is selected when you create a new conversation, and you can always change the space a conversation is assigned to.

## Let's Talk About Conversations

Conversations are core to Neary. They're also **super customizable** and **highly modular**. This is the best way to take advantage of the wide range of use cases that LLMs unlock for us.

Let's take a spin through a fresh conversation to see what makes them tick. New conversations can be created in three ways:

1. Click the `New Conversation` button in any empty space
2. Click the `+` icon in the nav bar
3. Use the `/new` slash command

After you create a new conversation, you'll be greeted with an "empty state" that includes fields to set the title, space and preset for your conversation.

>[!NOTE]  
> Use these slash commands to quicky manage conversations:
>
> `/new` creates a new conversation  
> `/title [some title]` sets a conversation's title  
> `/archive` archives messages in a conversation  
> `/delete` deletes a conversation  

### Conversation Presets

Presets are essentially pre-packaged "recipes" that imbue your conversation with a set of super powers. To illustrate this, let's look at a couple of presets Neary ships with out-of-the-box:

- `Just Chatting` turns the AI into a friendly conversation partner capable of tailoring responses to your profile and remembering important tidbits, regardless of context.

- `Calendar Chat` turns the AI into a personal assistant, capable of retreiving events on your Google Calendar, scheduling events on your behalf, and brainstorming reasons why you can't make a meeting you'd rather miss.

- `Document Chat` turns the AI into a smart friend who is happy to read documents and webpages on your behalf, and then answer all of your questions.

We'll get into *how* this happens in a moment, but for now just remember you can radically change the nature and function of any conversation simply by selecting a new preset.

### The Chat Stack

To see what makes a conversation tick, let's first checkout the **Chat Stack**. After your create a new conversation, click through on the current preset, or click the "stacks" (<img src="https://api.iconify.design/heroicons/square-3-stack-3d-20-solid.svg">)  icon in the toolbar to view that conversation's chat stack.

The chat stack essentially constructs the **flow** of your conversation. In order of their appearance:

- Changing the `Preset` will load a new set of instructions, snippets and tools into the conversation.

- The `Instructions`, or system message, you set the "tone" for the conversation. For more in-depth examples, check out the different presets and see how varied instructions can be.

- `Snippets` are pieces of context that are automatically injected into the conversation behind the scenes. For example, you can enable the `Insert User Profile` snippet to ensure the AI is aware of the information in your profile when its responding.

- `Tools` are actions the AI is allowed to take on your behalf. The AI "chooses" which tool to use, if any, based on the chat context. For example, the `Update User Profile` tool allows the AI to update your profile information for you, right in the chat.

And this is where it gets *really fun*. You can mix and match snippets and tools to create your perfect conversation. And, when you've done it, you can save your custom Chat Stack as as a preset for easy access.

Snippets and Tools are packaged together in Plugins, but we'll get to that in a moment. For now, let's explore the second set of knobs you have for customizing conversations.

> [!WARNING]  
> When it comes to LLMs, context is king. Packing a conversation with unrelated snippets and tools will not only result in worse performance, it'll cost you more money! Instead, create several narrowly focused conversations and switch between them as necessary.

### AI Settings

The other part of a conversation's "anatomy" is the AI--or chat model--settings. To access these, click the settings (<img src="https://api.iconify.design/heroicons/adjustments-horizontal-20-solid.svg">) icon in the chatbox toolbar.

You're likely familiar with most of these settings, so we'll just touch on a couple things here:

- `API Type` can be set set a custom endpoint, whether that's a local model or model somewhere in the cloud. Just make sure the endpoint uses the OpenAI API schema, and configure your endpoint in the `settings.toml` file.

- `Input Tokens` is a setting Neary uses locally to determine how many tokens of context to pass to the chat model. The user message, system message, and enabled tools and snippets are prioritized first, then context from past messages is used.

- `Max Tokens` is a parameter that OpenAI's chat endpoint no longer requires (you can keep it at 0 / infinite), but you may need to set this to a real number if you're using a custom model and getting very short responses.

>[!NOTE]  
>You can see the "raw" context of your most recent message by selecting the `Show X-Ray` option from the toolbar.

### Chat Stack + AI Settings = A Preset

And there you have it. A preset is a combination of these two important parts of a conversation's anatomy. Taken together, they can unlock varied and powerful applications of large language models.

Now things are really starting to heat up 🔥, yes?

## Using Plugins & Integrations

The last components of Neary you should familiarize yourself with are Plugins and Integrations:

- Plugins bundle together a set of themed Snippets and Tools that can be added to a conversation's Chat Stack.

- Integrations are third-party services and apps that can be connected to in order to enhance the plugins and their functions.

Click the gear (<img src="https://api.iconify.design/heroicons/cog-6-tooth-solid.svg">) icon at the bottom of the sidebar to view your plugins and integrations.

### Plugins

First, you'll see a list of `Enabled Plugins` and a list of `Available Plugins`. When a plugin is enabled, the snippets and tools bundled into that plugin are available to add in your conversations.

If you're not using a plugin, you can disable it to keep your list of available snippets and tools decluttered.

>[!NOTE]  
>When you select a preset, it will automatically enable any plugins required by the tools and/or snippets in that preset.

Viewing the details of a plugin will tell you a few things, namely:

- What tools and snippets the plugin provides
- What settings and configuration options the plugin has
- What integrations the plugin requires

### Integrations

Selecting the 'Integrations' tab on the setup screen will show you a list of available Integrations.

When you click `Connect` on one of those integrations, you'll either be asked to authenticate your account via an OAuth flow or you'll be asked for an API key.

When complete, the integration will show in the 'Connected Integrations' list and that integration can now be used in supported plugins.

Integrations are decoupled from the plugins themselves so that they can be reused across multiple plugins--you'll only have to connect once to make that integration available to all plugins.

### Creating Your Own Plugins

If you're comfortable with Python, writing your own plugins is easy (and fun!) Checkout this tutorial to find out how to create your first plugin.

## What's Next

With what you've learned here, your in a position to harnass the full power of Neary. Time to experiment! Here's a list of things to do next:

- If you haven't already, fill out your User Profile
- Create some Spaces to organize your conversations
- Create a few conversations and use a different preset in each
- Examine how the preset works by viewing its AI settings and Chat Stack
- Create your own presets and share them with the community!

If you have any other questions, feel free to open an Issue or a Discussion.
