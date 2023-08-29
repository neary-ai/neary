import os
import uuid
from pathlib import Path


class FileManager:
    def __init__(self, plugin):
        base_directory = Path(__file__).resolve(
        ).parent.parent / 'data' / 'files'
        self.plugin = plugin
        self.plugin_directory = os.path.join(base_directory, plugin.name)

    def save_file(self, file_obj, filename=None):
        """Save a file to the plugin's subdirectory."""
        # Generate a random filename if none is provided
        if filename is None:
            filename = f"{uuid.uuid4()}"

        # Ensure the directory exists
        os.makedirs(self.plugin_directory, exist_ok=True)

        # Full path to the file
        filepath = os.path.join(self.plugin_directory, filename)

        # Write the file
        with open(filepath, 'wb') as out_file:
            out_file.write(file_obj.read())

        # Return the filepath
        return filepath

    def get_file(self, filename):
        """Return the full path to a file in the plugin's subdirectory."""
        return os.path.join(self.plugin_directory, filename)

    def get_file_url_path(self, filename):
        """Return a URL for a file in the plugin's subdirectory."""
        return f"http://localhost:8000/api/files/{self.plugin.name}/{filename}"

    def delete_file(self, filename):
        """Delete a file in the plugin's subdirectory."""
        filepath = self.get_file(filename)
        os.remove(filepath)
