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

> **Note**
> Authentication is enabled by default. If you'd like to disable it altogether, set `enable_auth` to false in `settings.toml`.

The first time you load Neary you'll be greeted with a screen asking you to register with an email and a password. Enter whatever you'd like. This information is only used for authentication purposes.

## Setup Your Space

And you're in! You'll be welcomed with a screen that looks like this:

![A fresh install](./images/empty-state.png)

Before you get to typing (you'll have plenty of time for that, trust me), let's do a bit of setup.

### Add Profile Information

<img align="right" width="250" src="./images/profile.png" style="padding-left:30px;">

Click the person icon in the bottom of the sidebar on the left side. This will take you to your Account Settings, and the first thing you'll see is your user profile.

You don't *have* to fill out your profile, but it's a good idea. **Information you add to your profile will automatically be added to context in any conversation where the `Insert User Profile` snippet is active**.

We recommend adding at least your name and location to start. You can always add new items to your profile later.

> **Note**
> If you have the 'Update User Profile' tool enabled in your conversation, just ask and Neary will update your profile for you!