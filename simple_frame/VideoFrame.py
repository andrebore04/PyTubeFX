import customtkinter as ctk
import tkinter as tk

from customtkinter.windows.widgets.theme.theme_manager import ThemeManager
from tkinter import Event
from tkinter import StringVar
from PIL import Image
from typing import Any
from typing import Callable
from typing import Optional

class _OKDialog(ctk.CTkToplevel):
    def __init__(self,
                 parent: Any,
                 toplevel_geometry: tuple[int, int, int, int],
                 width = 360,
                 height = 160):
        super().__init__(parent)
        self.title('PyTubeFX')
        self.width = width
        self.height = height
        self.center_dialog(toplevel_geometry)
        self.resizable(False, False)
        self.destroyed = False
        self.protocol('WM_DELETE_WINDOW', self.close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        self.about_title_label = ctk.CTkLabel(
            self,
            text='PyTubeFX',
            font=ctk.CTkFont('Segoe UI', size=20, weight='bold')
        )
        self.about_title_label.grid(row=0, column=0,
                                    pady=(15, 10),
                                    sticky='new')

        description_label = ctk.CTkLabel(
            self,
            text='PyTubeFX, a portable GUI implementation of PyTube.',
            font=ctk.CTkFont('Segoe UI', size=14)
        )
        description_label.grid(row=1, column=0,
                               padx=15, pady=(10, 10),
                               sticky='new')

        ok_button = ctk.CTkButton(self, text="Ok", command=self.close)
        ok_button.grid(row=3, column=0, padx=100, pady=(10, 20), sticky='ews')

    @staticmethod
    def calculate_geometry(width,
                           height,
                           toplevel_geometry: tuple[int, int, int, int]) -> str:
        toplevel_width = toplevel_geometry[0]
        toplevel_height = toplevel_geometry[1]
        toplevel_x = toplevel_geometry[2]
        toplevel_y = toplevel_geometry[3]

        # center of app "relative" to the screen
        absolute_center_x = toplevel_x + (toplevel_width // 2)
        absolute_center_y = toplevel_y + (toplevel_height // 2)

        about_x = absolute_center_x - (width // 2)
        about_y = absolute_center_y - (height // 2)

        return str(width) + 'x' + str(height) + '+'\
               + str(about_x) + '+' + str(about_y)

    def center_dialog(self, new_toplevel_geometry: tuple[int, int, int, int]) -> None:
        new_geometry = _OKDialog.calculate_geometry(
            self.width,
            self.height,
            new_toplevel_geometry
        )
        self.geometry(new_geometry)

    def close(self) -> None:
        self.destroy()
        self.destroyed = True


class _TitleFrame(ctk.CTkFrame):
    """Title frame that contains a title(label)"""
    def __init__(self, master):
        """This is an internal class, not meant for
        external use and serving no specific purpose
        outside the scope of the file it's located in.
        
        Constructs a title frame,
        with 'master' as the master of the frame.\n
        """
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.label_app_title = ctk.CTkLabel(
            self,
            text='PyTubeFX',
            font=ctk.CTkFont('Segoe UI', size=32, weight='bold')
        )
        self.label_app_title.grid(row=0, column=0, columnspan=2,
                                  pady=15, padx=15,
                                  sticky='news')

        self.about_dialog = None

        self.about_box = ctk.CTkButton(
            self,
            text='ⓘ',
            width=20,
            height=30,
            fg_color=(ThemeManager.theme['CTk']['fg_color'][0],
                      ThemeManager.theme['CTk']['fg_color'][1]),
            command=self.create_about_dialog
        )
        self.about_box.grid(row=0, column=1, pady=(21, 20), padx=(0, 185), sticky='e')

    def create_about_dialog(self) -> None:
        if (not self.about_dialog) or self.about_dialog.destroyed:
            self.about_dialog = _OKDialog(
                self.winfo_toplevel(),
                self.get_toplevel_geometry()
            )
        else:
            self.about_dialog.center_dialog(self.get_toplevel_geometry())
        
        self.about_dialog.after(100, self.about_dialog.focus)
    
    def get_toplevel_geometry(self) -> tuple[int, int, int, int]:
        toplevel = self.winfo_toplevel()
        return (toplevel.winfo_width(),
                toplevel.winfo_height(),
                toplevel.winfo_x(),
                toplevel.winfo_y())
                

class _MiddleFrame(ctk.CTkFrame):
    """Middle frame that contains input and status."""
    def __init__(self, master):
        """This is an internal class, not meant for
        external use and serving no specific purpose
        outside the scope of the file it's located in.
        
        Constructs a middle frame,
        with 'master' as the master of the frame.\n
        """
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.status_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.status_frame.grid(row=0, column=0,
                               padx=0, pady=(10, 0),
                               sticky='ew')
        self._status_widgets()

        self.input_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.input_frame.grid(row=1, column=0,
                              padx=0, pady=(0, 10),
                              sticky='ew')
        self._input_widgets()

    def _status_widgets(self) -> None:
        segoeUI_13 = ctk.CTkFont('Segoe UI', size=13)

        # Expands row to fill all vertical space
        self.status_frame.grid_rowconfigure(0, weight=1)
        # Doesn't expand column
        self.status_frame.grid_columnconfigure(0, weight=0)
        # Expands column to fill all remaining horizontal space
        self.status_frame.grid_columnconfigure(1, weight=1)

        # Label on the left that says 'Status: '
        self.status_label = ctk.CTkLabel(self.status_frame,
                                         text='Status:',
                                         font=segoeUI_13)
        self.status_label.grid(row=0, column=0,
                               padx=(20, 5), pady=10,
                               sticky='nws')

        # Status box (frame) that contains the status message
        self.container_frame = ctk.CTkFrame(
            self.status_frame,
            height=28,
            fg_color=(ThemeManager.theme['CTk']['fg_color'][0],
                      ThemeManager.theme['CTk']['fg_color'][1])
        )
        self.container_frame.grid(row=0, column=1,
                                  padx=(5, 20), pady=10,
                                  sticky='ew')
        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(0, weight=1)

        # Label that contains the status message
        self.status_message_label = ctk.CTkLabel(self.container_frame,
                                                 text='Waiting for input...',
                                                 font=segoeUI_13)
        self.status_message_label.grid(row=0, column=0,
                                       padx=20, pady=0,
                                       sticky='ew')

    def _input_widgets(self) -> None:
        # Expands row to fill all vertical space
        self.input_frame.grid_rowconfigure(0, weight=1)
        # Expands column to fill all remaining horizontal space
        self.input_frame.grid_columnconfigure(0, weight=1)
        # Doesn't expand column
        self.input_frame.grid_columnconfigure(1, weight=0)

        self.input_entry_box = ctk.CTkEntry(self.input_frame,
                                            placeholder_text='URL goes here.')
        self.input_entry_box.grid(row=0, column=0,
                                  padx=(20, 5), pady=10,
                                  sticky='ew')
        self.input_entry_box_current_callback = None

        self.process_button = ctk.CTkButton(self.input_frame, text='Process')
        self.process_button.grid(row=0, column=1,
                                 padx=(5, 20), pady=10,
                                 sticky='ew')

    def _unbind_entry_box(self) -> None:
        if self.input_entry_box_current_callback:
            self.input_entry_box.unbind('<Return>')
            self.input_entry_box_current_callback = None

    # Internal API
    def _get_input_text(self) -> str:
        return self.input_entry_box.get()
    
    def _set_status(self, new_status_message: str) -> None:
        self.status_message_label.configure(text=new_status_message)

    def _set_callback_functions(
        self,
        new_input_entry_callback: Optional[Callable[([Event], None)]] = None,
        new_process_button_callback: Optional[Callable[([], None)]] = None
    ) -> None:
        self._unbind_entry_box() # Multiple callbacks are possible,
                                 # so unbind old before binding new
        if new_input_entry_callback:
            self.input_entry_box_current_callback = new_input_entry_callback
            self.input_entry_box.bind('<Return>', new_input_entry_callback)
        if new_process_button_callback:
            self.process_button.configure(command=new_process_button_callback)

    def _set_process_button(self, enabled: bool) -> None:
        self.process_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)


class _ExportFrame(ctk.CTkFrame):
    """Export frame that contains a variety
    of widgets to download and export a video"""

    def __init__(self, master):
        """This is an internal class, not meant for
        external use and serving no specific purpose
        outside the scope of the file it's located in.
        
        Constructs an export frame,
        with 'master' as the master of the frame.\n
        """
        super().__init__(master)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self._export_widgets()

    def _export_widgets(self) -> None:
        segoeUI_15 = ctk.CTkFont('Segoe UI', size=15)
        segoeUI_13 = ctk.CTkFont('Segoe UI', size=13)

        self.video_title_label = ctk.CTkLabel(self, text='Insert Video URL!', font=segoeUI_15)
        self.video_title_label.grid(row=0, column=0,
                                    padx=(20, 10), pady=(20, 0),
                                    sticky='nw', columnspan=3)

        self.video_resolution_label = ctk.CTkLabel(self,
                                                   text='Video Resolution:',
                                                   font=segoeUI_13)
        self.video_resolution_label.grid(row=1, column=0,
                                         padx=(20, 10), pady=(15, 5),
                                         sticky='nw')

        self.video_resolution_menu = ctk.CTkOptionMenu(self,
                                                       values=['N/A'],
                                                       font=segoeUI_13,
                                                       state=tk.DISABLED)
        self.video_resolution_menu.grid(row=1, column=1, padx=10, pady=(15, 5), sticky='nw')

        self.audio_bitrate_label = ctk.CTkLabel(self, text='Audio Bitrate:', font=segoeUI_13)
        self.audio_bitrate_label.grid(row=2, column=0,
                                      padx=(20, 10), pady=(10, 0),
                                      sticky='nw')

        self.audio_bitrate_menu = ctk.CTkOptionMenu(self,
                                                    values=['N/A'],
                                                    font=segoeUI_13,
                                                    state=tk.DISABLED)
        self.audio_bitrate_menu.grid(row=2, column=1, padx=10, pady=(10, 0), sticky='nw')

        self.thumbnail_label = ctk.CTkLabel(self,
                                            #(16 : 9) * 11
                                            width=16*11,
                                            height=9*11,
                                            text='',
                                            bg_color='dark gray')
        self.thumbnail_label.grid(row=0, column=2, padx=20, pady=20, rowspan=3, sticky='ne')

        self.download_button = ctk.CTkButton(self,
                                             text='Download',
                                             font=segoeUI_13,
                                             state=tk.DISABLED)
        self.download_button.grid(row=3, column=0, columnspan=3,
                                  padx=180, pady=(0, 20),
                                  sticky='ews')

    # Internal API
    def _get_selected_bitrate(self) -> str:
        return self.audio_bitrate_menu.get()
    
    def _get_selected_resolution(self) -> str:
        return self.video_resolution_menu.get()
    
    def _set_widgets(self, enabled) -> None:
        self.video_resolution_menu.configure(state=tk.NORMAL if enabled else tk.DISABLED)
        self.audio_bitrate_menu.configure(state=tk.NORMAL if enabled else tk.DISABLED)
        self.download_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def _set_bitrate_list(self, new_bitrate_list: list[str]) -> None:
        self.audio_bitrate_menu.configure(
            values=new_bitrate_list,
            variable=StringVar(self.audio_bitrate_menu, new_bitrate_list[0])
        )

    def _set_resolution_list(self, new_resolution_list: list[str]) -> None:
        self.video_resolution_menu.configure(
            values=new_resolution_list,
            variable=StringVar(self.video_resolution_menu,
                               new_resolution_list[0])
        )

    def _set_video_title(self, new_video_title: str) -> None:
        if len(new_video_title) > 54:
            new_video_title = new_video_title[:54] + '...'

        self.video_title_label.configure(text=new_video_title)

    def _set_video_thumbnail(self, new_video_thumbnail: Image) -> None:
        thumbnail_wrap = ctk.CTkImage(new_video_thumbnail,
                                      None,
                                      (16 * 11, 9 * 11))
        self.thumbnail_label.configure(True, image=thumbnail_wrap)

    def _set_callback_function(
        self,
        new_download_button_callback: Optional[Callable[([], None)]] = None
    ) -> None:
        if new_download_button_callback:
            self.download_button.configure(
                command=new_download_button_callback
            )


class VideoFrame(ctk.CTkFrame):
    """Defines the \"simple-mode\" frame of the application."""
    
    def __init__(self, master):
        """ 
        Constructs a simple frame, with 'master' as the master of the frame
        """
        super().__init__(master, fg_color='transparent')

        # _TitleFrame, high enough to contain widgets and padding
        self.grid_rowconfigure(0, weight=0)
        # _MiddleFrame, same as row 0
        self.grid_rowconfigure(1, weight=0)
        # _ExportFrame, expands vertically until the end of the frame
        self.grid_rowconfigure(2, weight=1)

        # everything expands horizontally until the end of the frame
        self.grid_columnconfigure(0, weight=1)

        self._simple_widgets()

    def _simple_widgets(self) -> None:
        self.title_frame = _TitleFrame(self)
        self.title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky='new')
        
        self.middle_frame = _MiddleFrame(self)
        self.middle_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky='new')

        self.export_frame = _ExportFrame(self)
        self.export_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky='news')

    # Main API
    def get_input_text(self) -> str:
        return self.middle_frame._get_input_text()

    def get_selected_bitrate(self) -> str:
        return self.export_frame._get_selected_bitrate()

    def get_selected_resolution(self) -> str:
        return self.export_frame._get_selected_resolution()

    def set_bitrate_list(self, new_bitrate_list: list[str]) -> None:
        self.export_frame._set_bitrate_list(new_bitrate_list)

    def set_export_widgets(self, enabled):
        self.export_frame._set_widgets(enabled)

    def set_export_callback_function(
        self,
        new_download_button_callback: Optional[Callable[([], None)]] = None
    ) -> None:
        self.export_frame._set_callback_function(new_download_button_callback)

    def set_input_callback_functions(
        self,
        new_input_entry_callback: Optional[Callable[([], None)]] = None,
        new_process_button_callback: Optional[Callable[([Event], None)]] = None
    ) -> None:
        self.middle_frame._set_callback_functions(new_input_entry_callback,
                                                  new_process_button_callback)

    def set_process_button(self, enabled: bool) -> None:
        self.middle_frame._set_process_button(enabled)

    def set_resolution_list(self, new_resolution_list: list[str]) -> None:
        self.export_frame._set_resolution_list(new_resolution_list)

    def set_status(self, new_status_message: str) -> None:
        self.middle_frame._set_status(new_status_message)

    def set_video_thumbnail(self, new_video_thumbnail: Image) -> None:
        self.export_frame._set_video_thumbnail(new_video_thumbnail)

    def set_video_title(self, new_video_title: str) -> None:
        self.export_frame._set_video_title(new_video_title)
