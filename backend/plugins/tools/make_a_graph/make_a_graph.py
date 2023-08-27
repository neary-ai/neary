import io
import matplotlib.pyplot as plt
import numpy as np

from backend.plugins import Tool
from backend.services import FileManager
from backend.services import MessageHandler


class MakeAGraphTool(Tool):
    name = "make_a_graph"
    display_name = "Make a Graph"
    description = "Returns an image of a sine wave line graph"
    llm_description = "`make_a_graph`: Returns an image of a sine wave line graph. Takes no arguments."

    requires_approval = False
    follow_up_on_output = False

    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self):
        file_manager = FileManager(self)
        message_handler = MessageHandler()

        # Set the style
        plt.style.use('bmh')

        # Sample data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        # Create the plot
        plt.plot(x, y)

        # Save the plot to a BytesIO object
        plot_file = io.BytesIO()
        plt.savefig(plot_file, format='png')

        # Move to the beginning of the file-like object
        plot_file.seek(0)

        # Save the plot using the FileManager
        file_manager.save_file(plot_file, filename='output.png')

        file_path = file_manager.get_file_url_path('output.png')

        await message_handler.send_message_to_ui(
            f"""![A Sine Wave]({file_path})""", self.conversation.id)

        return f"File saved: {file_manager.get_file_url_path('output.png')}"
