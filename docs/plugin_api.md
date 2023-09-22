# Plugin Services API Documentation

## Introduction

The Plugin Services API is a tool for developers to access resources and functionality beyond the immediate scope of their plugin. The API provides a suite of services available through the `self.services` property of your plugin.

## User Profile methods

### get_profile()

This asynchronous method retrieves the user's profile. The profile is returned as a dictionary.

Example usage: `profile = await self.services.get_profile()`

### set_profile(profile_data)

This asynchronous method sets the user's profile with the provided profile data. The profile data should be in the form of a dictionary. The updated profile is then saved and returned.

Example usage: `updated_profile = await self.services.set_profile({"name": "Joe", "timezone": "America/Denver"})`

### get_profile_field(key)

This asynchronous method retrieves the value of a specific field from the user's profile. The key for the desired field should be provided as a string. The method returns the value of the specified field.

Example usage: `timezone = await self.services.get_profile_field("timezone")`

### set_profile_field(key, value)

This asynchronous method sets the value of a specific field in the user's profile. The key for the desired field and the new value should be provided. The updated profile is then saved and returned.

Example usage: `updated_profile = await self.services.set_profile_field("timezone", "America/New_York")`

### delete_profile_field(key)

This asynchronous method deletes a specific field from the user's profile. The key for the desired field should be provided. If the key exists in the profile, it will be deleted and the updated profile will be saved and returned.

Example usage: `updated_profile = await self.services.delete_profile_field("timezone")`


## Integration & Credentials methods

### get_credentials(integration_name)

The `get_credentials` asynchronous method retrieves the credentials associated with a specified integration, if it is connected. The integration name should be provided as a string.

A dict containing the credentials is returned. The access token or API key for the integration will be available in the `access_token` or `api_key` key, depending on the integration type.

Example usage:

```python
try:
    credentials = await self.services.get_credentials("google_calendar")
    if credentials:
        access_token = credentials["access_token"]
except ValueError:
    print("Integration not found.")
```

## File Management methods

### save_file(file_obj, filename=None, extension="txt")

The `save_file` method saves a file to the conversation's subdirectory. The file_obj is required which should be the file data. Optionally, a filename and extension can be provided. If no filename is provided, a random one is generated. The method ensures the directory exists, writes the file, gets the file size, and returns the filepath, filename, filesize, and url.

Example usage: `file_info = self.services.save_file(file_data, "my_file", "pdf")`

### get_file(filename)

The `get_file` method returns the full path to a file in the plugin's subdirectory. The filename is required.

Example usage: `file_path = self.services.get_file("my_file.pdf")`

### get_file_url_path(filename)

The `get_file_url_path` method returns a URL for a file in the plugin's subdirectory. The filename is required.

Example usage: `file_url = self.services.get_file_url_path("my_file.pdf")`

### delete_file(filename)

The `delete_file` method deletes a file in the plugin's subdirectory. The filename is required.

Example usage: `self.services.delete_file("my_file.pdf")`

## Messaging methods

>[!NOTE]  
> The `conversation_id` is automatically passed to the plugin in the `conversation` object, and can be accessed with `self.conversation.id`

### send_alert_to_ui(message, conversation_id)

The `send_alert_to_ui` asynchronous method sends an alert message to the user interface.

Example usage: `await self.services.send_alert_to_ui("Alert message", self.conversation.id)`

### send_message_to_ui(message, conversation_id)

The `send_message_to_ui` asynchronous method sends a message from the `assistant` role to the user interface.

Example usage: `await self.services.send_message_to_ui("Message content", self.conversation.id)`

### send_file_to_ui(filename, filesize, file_url, conversation_id)

The `send_file_to_ui` asynchronous method sends a downloadable file to the user interface.

Example usage: `await self.services.send_file_to_ui("file_name.extension", 1234, "file_url", self.conversation.id)`