# PyTubeFX (1.0.0)
A simple GUI implementation of [pytubefix](https://github.com/JuanBindez/pytubefix), based on [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

<div style='width: 640px; height: 480px; margin: auto'>
	<img src='./resources/splash.png'>
</div>
<br>

## Requirements
The main requirement for this program is [FFmpeg](https://ffmpeg.org/), you need to install it and the directory of the binary files must be in system's PATH variable, or the application won't be able to export the video.

### Windows
I suggest you use [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/) to install it, like so:

```pwsh
# The essentials build is sufficient
winget install --id Gyan.FFmpeg.Essentials
```

Alternatively, download the binaries manually from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).

### Linux
You can probably install it from your package manager.
For more information, refer to [FFmpeg's download page](https://ffmpeg.org/download.html#build-linux).

For instance, on Ubuntu, install it like this:

```sh
sudo apt install ffmpeg
```

## Dependencies
>These dependencies are only required if you want to launch the app from Python or if you want to build the executable yourself.<br>
>If you just want to use the app, download the prebuilt executable from the [releases section](https://github.com/andrebore04/PyTubeFX/releases).

Make sure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).

Install the required libraries using the following command:

```sh
pip install -r requirements.txt
```

## About the executable
The executable you can find in the releases section is created by [Pyinstaller](https://pypi.org/project/pyinstaller/), and if you scan it with an antivirus, chances are it will be flagged as malware of some sort.

This (probably) happens because Pyinstaller tightly packs Python and every dependency the app needs into a single executable, and this resembles what a lot of malicious programs do.

Pyinstaller itself does no damage whatsoever, so you will be fine using the executable.

I know it's annoying, and if you feel safer, I advise you download Python and execute the app from source, as explained in the next section.

## Launching the app
Either use the prebuilt executable from the releases or launch the app with python by following these steps:

### Clone the repository

```sh
git clone https://github.com/andrebore04/PyTubeFX.git
cd PyTubeFX
```

### Launch [main.py](https://github.com/andrebore04/PyTubeFX/blob/main/main.py):

```
python ./main.py
```

## Building the executable
To build yourself an executable that doesn't require Python installed, follow these steps:

### Install Pyinstaller

```sh
pip install pyinstaller
```

### Clone the repository

```sh
git clone https://github.com/andrebore04/PyTubeFX.git
cd PyTubeFX
```

### Build the app

```sh
pyinstaller --onefile --noconsole ./main.py
```

## Improvements
These are some known bugs to fix and general features that could be added in the next releases:
- Fix graphics and fonts being a bit tight on linux (as I've seen on Ubuntu 22.04.3).
- Add MacOS binaries (as soon as I find a Mac to do this on).
- Implement langauge files and convert app to use them.
- Implement "Playlist Mode", to download entire playlists.
- Find a workaround to setup oauth without having to use [pytubefix's CLI](https://github.com/JuanBindez/pytubefix/blob/main/pytubefix/innertube.py#L335); this would make it possible for users to download private and age-restricted videos.
- Implement "Advanced Mode", with different codec options and support for higher resolutions.

## Contributing
Any contribution is gladly accepted, I will forever be greatful to you.
