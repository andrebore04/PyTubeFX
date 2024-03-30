import logging
import customtkinter as ctk
import app_exceptions as app_exceptions

from simple_frame.VideoFrame import VideoFrame
from simple_frame.VideoLogic import VideoLogic

logger = logging.getLogger(__name__)

class Application(ctk.CTk):
    def __init__(self):
        """
        Constructs the application.
        """
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("System")

        super().__init__()

        self.title("PyTubeFX")
        self.geometry("640x480")
        self.resizable(False, False)

        # App defaults to "Simple Video Mode" upon start
        self.current_frame_class = VideoFrame
        self.current_frame = self.current_frame_class(self)
        self.current_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        
        self.current_logic_class = VideoLogic
        self.current_logic = self.current_logic_class(self.current_frame)

        self.current_frame.set_input_callback_functions(self.current_logic.process_user_input,
                                                        self.current_logic.process_user_input)
        self.current_frame.set_export_callback_function(self.current_logic.start_download)
        
        logger.info('Application.__init__() Application created.\n')

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting...")