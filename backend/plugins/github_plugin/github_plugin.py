from github import Github
from backend.plugins import BasePlugin, tool
from backend.services.credential_manager import CredentialManager

class GithubPlugin(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    @tool
    async def get_repos(self):
        credential_manager = await CredentialManager.create('github')
        credentials = await credential_manager.get_credentials()
        g = Github(credentials["access_token"])

        repos = ""
        for repo in g.get_user().get_repos():
            repos += f"{repo.name}\n"
        return repos
    
    @tool
    async def get_project_tree(self, repo_name):
        credential_manager = await CredentialManager.create('github')
        credentials = await credential_manager.get_credentials()
        g = Github(credentials["access_token"])

        repo = g.get_user().get_repo(repo_name)

        # Get file and directory structure at the root
        contents = repo.get_contents("")

        # Recursive function to fetch file structure
        def get_directory_structure(contents, indent = ""):
            result = ""
            for content in contents:
                result += indent + content.name + "\n"
                if content.type == "dir":
                    result += get_directory_structure(repo.get_contents(content.path), indent + "  ")
            return result

        # Get the directory structure
        return get_directory_structure(contents)