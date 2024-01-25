import logging
import os
from pprint import pformat
import shutil
import subprocess
import tempfile
import customtkinter as ctk
import exceptions as app_exceptions
import pytubefix.exceptions as pytube_exceptions
import requests
import re

from threading import Thread
from io import BytesIO
from PIL import Image
from pytubefix import YouTube
from pytubefix import Stream
from simple_frame import SimpleFrame
from tkinter import Event
from tkinter.filedialog import asksaveasfilename
from typing import Dict
from typing import Optional
from typing import Tuple
from urllib.error import URLError

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

        # App defaults to "Simple Mode" upon start
        self.current_mode_class = SimpleFrame
        self.current_frame = self.current_mode_class(self)
        self.current_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        self.current_frame.set_input_callback_functions(self.process_user_input,
                                                        self.process_user_input)
        self.current_frame.set_export_callback_function(self.start_download)
        
        logger.info('Application.__init__() Application created.\n')

    @staticmethod
    def animation_charset(n):
        LOADING_CHARS = ['\\', '|', '/', '-']
        current_n = n
        
        while True:
            yield LOADING_CHARS[(current_n) % len(LOADING_CHARS)]
            current_n += 1

    def check_download(self) -> None:
        """
        Method that checks the download thread's state every 0.3s (arbitrarily chosen)

        While checking, it updates the status to show info about the download.

        On thread completion, invokes `self.download_complete`.
        """
        if self.thread.is_alive():
            self.current_frame.set_status(f'Downloading {self.download_percentage}%'
                                          f' [{next(self.char_generator)}]')
            self.current_frame.after(300, self.check_download)
        else:
            logger.info('check_download()[Main Thread] Thread finished.\n')
            self.current_frame.set_status(f'Downloading completed! Choose where to save the video.')
            self.current_frame.after(0, self.download_complete)
    
    def download_complete(self) -> None:
        """
        Method that prepares the downloaded files,
        asks the user the save path of the video,
        and calls `Application.process_ffmpeg`
        """
        export_filetype = [('Video Files', '*.mp4')]
        extension = '.mp4'

        if self.audio_path and not self.video_path:
            export_filetype = [('Audio Files', '*.m4a')]
            extension = '.m4a'

        output_path = asksaveasfilename(confirmoverwrite=True,
                                        defaultextension=extension,
                                        filetypes=export_filetype,
                                        initialdir='~\\Desktop')

        new_status = 'Download completed! Video saved!'

        if not output_path: # User didn't choose a file and closed the dialog
            new_status = 'Download canceled.'
        else:
            try:
                logger.info('download_complete() Building FFmpeg process.')
                Application.process_ffmpeg(self.video_path,
                                           self.audio_path,
                                           output_path)
                logger.info('download_complete() FFmpeg process successfully executed.')
            except FileNotFoundError as e:
                logger.error('download_complete() FFmpeg not found.')
                new_status = 'FFmpeg was not found, install it and try again.'

        self.current_frame.set_status(new_status)
        shutil.rmtree(self.temp_dir)
        self.temp_dir = '' # This is now invalid

        # Re-enable widgets
        self.current_frame.set_export_widgets(True)
        self.current_frame.set_process_button(True)
        
        # Reset callbacks
        self.current_frame.set_input_callback_functions(self.process_user_input,
                                                        self.process_user_input)
        self.current_frame.set_export_callback_function(self.start_download)

    def download_threaded(self,
                          video_itag: int,
                          audio_itag: int) -> Tuple[str | None, str | None]:
        """
        Method that downloads the streams in self.temp_dir and updates
        self.video_path and self.audio_path with their respective values.
        
        This method is supposed to be called from a thread.
        
        ### Parameters
        - `video_itag`, the video stream itag.
        - `audio_itag`, the audio stream itag.
        
        ### Exceptions
        - `FileNotFoundError`, an exception raised when
        the ffmpeg executable is not found.

        ### Return value
        - `Tuple[str | None, str | None]`,
            a tuple containing the temporary download paths to the streams
        """
        # Chosen arbitrarily
        VIDEO_FILENAME = 'video_track'
        AUDIO_FILENAME = 'audio_track'

        logger.info('download_threaded()[Thread] Starting download.')

        if video_itag:
            video_stream = self.video_object.streams.get_by_itag(video_itag)
            self.video_path = video_stream.download(self.temp_dir, VIDEO_FILENAME)
        if audio_itag:
            audio_stream = self.video_object.streams.get_by_itag(audio_itag)
            self.audio_path = audio_stream.download(self.temp_dir, AUDIO_FILENAME)

        logger.info('download_threaded()[Thread] Download finished.\n')

    def get_streams(self, user_input: str) -> Tuple[Dict, Dict]:
        """
        Method that uses pytube to get, organize and
        return the video streams as dictionaries.
        
        ### Parameters
        - `user_input`, the user's input, in URL form.
        
        ### Exceptions
        - `InvalidInput`, an exception raised when
        the user's input is invalid

        ### Return value
        - `Tuple[Dict, Dict]`, a tuple containing streams dictionaries
        """
        if len(user_input) == 0:
            raise app_exceptions.InvalidInput(user_input=user_input,
                                              error_info="no input provided")

        if len(user_input) < 28:
            raise app_exceptions.InvalidInput(
                user_input=user_input,
                error_info=f"minimum URL length is 28 characters, "
                           f"user input is {len(user_input)}",
            )

        logger.info("get_streams() Input is valid.\n")

        try:
            self.video_object = YouTube(user_input, on_progress_callback=self.update_percentage)
        except pytube_exceptions.RegexMatchError:
            raise app_exceptions.InvalidInput(
                user_input=user_input,
                error_info="input is not a valid video url"
            )

        dash_avc_streams = self.video_object.streams.filter(
            only_video=True,
            adaptive=True,
            custom_filter_functions=[ # video_codec=avc1.******
                lambda s: re.match(r"(?:avc1\.[\w]+)",
                                    s.video_codec) is not None
            ]
        )

        dash_aac_streams = self.video_object.streams.filter(
            only_audio=True,
            adaptive=True,
            custom_filter_functions=[ # audio_codec=mp4a.**.*
                lambda s: re.match(r"(?:mp4a\.[\d]{2}\.\d)",
                                    s.audio_codec) is not None
            ]
        )

        # { 'None' : None,
        #   '144p @ 30fps' : 160,
        #    ... }
        dash_avc_streams_dict = {str(s.resolution) + " @ " + str(s.fps) + "fps": s.itag
                                 for s in dash_avc_streams
                                 if s.resolution}
        dash_avc_streams_dict.update({'None': None})

        # { 'None' : None,
        #   '160kbps' : 251,
        #    ... }
        dash_aac_streams_dict = {stream.abr if stream.abr else '30kbps' : stream.itag
	                             for stream in dash_aac_streams}
        dash_aac_streams_dict.update({'None': None})

        logger.debug(f'get_streams() Video streams:')
        logger.debug(pformat(dash_avc_streams_dict))
        logger.debug(f'get_streams() Audio streams:')
        logger.debug(pformat(dash_aac_streams_dict) + '\n')

        return (dash_avc_streams_dict, dash_aac_streams_dict)
    
    @staticmethod
    def process_ffmpeg(video_path: Optional[str],
                       audio_path: Optional[str],
                       output_path: str) -> None:
        """
        Method that uses pytube to get, organize and
        return the video streams as dictionaries.
        
        ### Parameters
        - `video_path`: path to video track, optional
        - `audio_path`: path to audio track, optional
        - `output_path`: path to output track

        ### Return value
        - `Tuple[Dict, Dict]`, a tuple containing streams dictionaries
        """
        """
        Static method that constructs a ffmpeg command and executes it
        as a subprocess
        """
        if (video_path and not os.path.exists(video_path)) or \
            (audio_path and not os.path.exists(audio_path)) or \
            not output_path:
            logger.critical('process_ffmpeg() Invalid track_path\n')
            return

        ffmpeg_command = ['ffmpeg', '-hide_banner']

        input_flags = []
        codec_flags = []

        if video_path:
            input_flags.extend(['-i', video_path])
            codec_flags.extend(['-c:v', 'copy'])

        if audio_path:
            input_flags.extend(['-i', audio_path])
            codec_flags.extend(['-c:a', 'copy'])

        ffmpeg_command.extend(input_flags)
        ffmpeg_command.extend(codec_flags)
        ffmpeg_command.append('-y')
        ffmpeg_command.append(output_path)

        logger.debug('process_ffmpeg() Command: ' + ' '.join(ffmpeg_command))
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True)

        logger.debug(f'process_ffmpeg() Subprocess returncode: {result.returncode}\n')

        # Ffmpeg outputs logging data to stderr
        logger.debug('process_ffmpeg() FFmepg output:')
        logger.debug(result.stderr + '\n')

    def process_user_input(self, _: Optional[Event] = None):
        """
        Callback method that processes the user's input, passes it
        to the processing functions and updates the gui

        This method also handles the exceptions thrown by
        `self.get_streams()` and `self.update_frame()`

        ### Parameters
        - `_`: optional event that will be discarded, defaults to None
        """
        user_input = self.current_frame.get_input_text()

        logger.info(f"process_user_input() Got input: {user_input}")

        enable_export_widgets = True
        status = 'Video loaded successfully!'

        try:
            self.videos, self.audios = self.get_streams(user_input)
            self.update_frame()
        except app_exceptions.InvalidInput as e:
            logger.error(f'process_user_input() {e.error_string_color}')
            status = e.error_string
            enable_export_widgets = False
        except URLError as e:
            logger.error(f'process_user_input() URLError: {e.args}.')
            status = 'Could not resolve address, '\
                     'check your internet connection.'
            enable_export_widgets = False
        except app_exceptions.ThumbnailNotFound as e:
            logger.warning(f'process_user_input() {e.error_string_color}'
                          + 'This error should not happen; ',
                          + 'if possible, file an issue on GitHub: '
                          + '<GitHub Issues link>\n')
            status = e.error_string
        
        self.current_frame.set_export_widgets(enabled=enable_export_widgets)
        self.current_frame.set_status(new_status_message=status)
    
    def start_download(self):
        """
        Method that handles getting the correct streams' itags,
        starts the download thread, and invokes `self.check_download()`.
        """
        selected_resolution = self.current_frame.get_selected_resolution()
        selected_bitrate = self.current_frame.get_selected_bitrate()

        video_itag = self.videos.get(selected_resolution)
        audio_itag = self.audios.get(selected_bitrate)

        logger.debug(f'start_download() Selected resolution: {selected_resolution}'
                   + f'start_download() Itag paired: {video_itag}\n')
        
        logger.debug(f'start_download() Selected bitrate: {selected_bitrate}'
                   + f'start_download() Itag paired: {audio_itag}\n')

        if not video_itag and not audio_itag:
            logger.info('start_download() Nothing selected')
            self.current_frame.set_status('No stream selected, nothing happened!')
            return

        self.temp_dir = tempfile.mkdtemp(prefix="PyTubeFX.")
        logger.debug(f'start_download() Temporary directory: {self.temp_dir}')
        
        self.video_path = None
        self.audio_path = None

        self.char_generator = Application.animation_charset(0) # To display download animation
        self.download_percentage = 0.0 # To display the percentage
        
        # The percentage bugs out after 100%
        # this holds it there until the thread has finished
        self.stop_percentage = False

        self.thread = Thread(target=self.download_threaded,
                             args=[video_itag, audio_itag])
        
        self.thread.start()

        # Disable widgets
        self.current_frame.set_export_widgets(False)
        self.current_frame.set_process_button(False)
        
        # Disable callbacks
        self.current_frame.set_input_callback_functions()
        self.current_frame.set_export_callback_function()

        # Start thread-checking loop after half a second
        self.current_frame.after(500, self.check_download)

    # Modified version of the 'on_progress' function found in pytubefix.cli
    def update_percentage(self,
                          stream: Stream,
                          _: bytes,
                          bytes_remaining: int) -> None:
        """
        Method that updates the percentage.
        Passed to the pytubefix.YouTube class as the 'on_progress_callback' function.

        ### Paramters
        - `stream`: the stream that's being downloaded
        - `_`: represents the current chunk being downloaded, unused.
        - `bytes_remaining`: number of bytes remaining as an integer.
        """
        if self.stop_percentage:
            return
        
        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        self.download_percentage = round(100.0 * bytes_received / float(filesize), 1)

        if int(self.download_percentage) == 100:
            self.stop_percentage = True

    def update_frame(self):
        """
        Method that updates the frame's widgets with the video information.

        ### Exceptions
        `exceptions.ThumbnailNotFound`:
        Exception thrown when the thumbnail fails to load
        """
        logger.info('update_frame() Setting resolution menu')
        self.current_frame.set_resolution_list(
            [key for key in self.videos]
        )
        
        logger.info('update_frame() Setting bitrate menu')

        def sorting_key(value):
            if value == 'None':
                return -1
            match = re.match(r'([\d]+)kbps', value)
            return int(match.group(1))
        
        self.current_frame.set_bitrate_list( # Sort by audio bitrate
            sorted([key for key in self.audios],
                   key=sorting_key,
                   reverse=True)
        )

        logger.info('update_frame() Setting video title')
        self.current_frame.set_video_title(self.video_object.title)

        logger.info('update_frame() Setting video thumbnail\n')
        # Try to get a HD 16:9 thumbnail
        thumbnail_response = requests.get(
            f'https://i.ytimg.com/vi/'
            f'{self.video_object.video_id}'
            '/maxresdefault.jpg'
        )
        
        if thumbnail_response.status_code == 200:
            thumbnail = Image.open(BytesIO(thumbnail_response.content))
        else:
            # If HD fails, fall back to SD and crop to 16:9
            thumbnail_response = requests.get(self.video_object.thumbnail_url)
            if thumbnail_response == 200:
                thumbnail = Image.open(
                    BytesIO(thumbnail_response.content)
                ).crop((0, 60, 640, 420))
            else:
                # Thumbnail not found
                raise app_exceptions.ThumbnailNotFound(
                    self.video_object.video_id
                )
        
        self.current_frame.set_video_thumbnail(thumbnail)

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting...")