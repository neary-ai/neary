from github import Github
from backend.plugins import BasePlugin, tool, snippet

class GithubPlugin(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

        self.active_repo = self.settings.get('set_active_repo', {}).get('repo_name', None)
        
    @tool
    async def get_repos(self):
        credentials = await self.services.get_credentials('github')
        g = Github(credentials["access_token"])

        repos = ""
        for repo in g.get_user().get_repos():
            repos += f"{repo.name}\n"
        return repos

    @tool
    async def set_active_repo(self, repo_name):
        self.settings['set_active_repo']['repo_name'] = repo_name
        await self.save_state()
        return f"Active repository set to `{repo_name}`."

    @snippet
    async def insert_active_repo(self, context):
        if self.active_repo:
            context.add_snippet(f"The active repository is set to: {self.active_repo}")
        else:
            context.add_snippet("No active repository is currently set.")

    @tool
    async def get_project_tree(self, repo_name=None):
        if not repo_name:
            if self.active_repo:
                repo_name = self.active_repo
            else:
                return "No active repository is set; a repo_name is required."

        credentials = await self.services.get_credentials('github')
        g = Github(credentials["access_token"])

        repo = g.get_user().get_repo(repo_name)

        # Get file and directory structure at the root
        contents = repo.get_contents("")

        # Recursive function to fetch file structure
        def get_directory_structure(contents, indent = ""):
            result = ""
            for content in contents:
                if content.type == "dir":
                    result += indent + content.name + "\n"
                    result += get_directory_structure(repo.get_contents(content.path), indent + "  ")
            return result

        # Get the directory structure
        return get_directory_structure(contents)

    @tool
    async def get_files_in_directory(self, directory_path, repo_name=None):
        if not repo_name:
            if self.active_repo:
                repo_name = self.active_repo
            else:
                return "No active repository is set; a repo_name is required."
        
        credentials = await self.services.get_credentials('github')
        g = Github(credentials["access_token"])

        repo = g.get_user().get_repo(repo_name)
        directory_contents = repo.get_contents(directory_path)

        # Get names of all files in the directory
        file_names = [content.name for content in directory_contents if content.type == "file"]

        return ", ".join(file_names)

    @tool
    async def get_file(self, file_path, repo_name=None):
        if not repo_name:
            if self.active_repo:
                repo_name = self.active_repo
            else:
                return "No active repository is set; a repo_name is required."
        
        credentials = await self.services.get_credentials('github')
        g = Github(credentials["access_token"])

        repo = g.get_user().get_repo(repo_name)
        file_content = repo.get_contents(file_path)

        return file_content.decoded_content.decode()