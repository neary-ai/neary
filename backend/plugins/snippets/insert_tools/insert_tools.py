from backend.plugins import Snippet


class InsertToolsSnippet(Snippet):
    name = "insert_tools"
    display_name = "Insert Tools"
    description = "Give Neary context on which tools are available and how to use them."
    is_public = False

    def __init__(self, conversation, settings=None, data=None):
        super().__init__(None, conversation, settings, data)

    async def run(self, context):
        tools_str = """You are a tool-assisted AI assistant. This means you can use tools, if necessary, to accomplish tasks that you wouldn't otherwise be able to accomplish as a Large Language Model.\nTo use a tool, simply append a tool request to the bottom of your response in this format: <<tool:tool_name({"tool_arg": "tool_arg_value"}). Replace 'tool_name', 'tool_arg' and 'tool_arg_value' with the values for the tool you're invoking. Here's a list of tools you have available to you:\n\n"""

        for tool in self.conversation.tools:
            tools_str += f'- {tool.llm_description}\n'

        context.add_snippet(tools_str)
