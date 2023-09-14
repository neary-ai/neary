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

Once you've started Neary, point your browser to http://localhost:8000.

### Setup your account

The first time you load Neary you'll be greeted with a screen asking you to register with an email and a password. Enter whatever you'd like. This information is used for authentication and nothing else.

> **Note**
> Authentication is enabled by default. If you'd like to disable it altogether, set `enable_auth` to false in `settings.toml`.