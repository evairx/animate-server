# Animete Server
Create your own Media Server to watch Anime with <a 
href="https://github.com/evairx/animate-server">Animate Server</a>
 
## What is Animate Server? and why was it created?
Animate Server was created to run Animate Client, basically it is a HTTP server (REST API) developed in Python using Flask,

## How does it work?
Animate Server reads the given path, and scans all the folders in that path, once scanned it GETs to the <a href="https://developer.themoviedb.org/reference/intro/getting-started">TMDB</a> API and returns the Anime information to the Animate client which can be Series or Movies.

# Steps to create your server

1. Download the server and run it, a new file named settings.json will be created.
2. Open the .json file and configure it.
```json
{
	"path": "", // Here will be the path of Anime series
	"format": "mp4", // here is the format of the chapters, the Animate Client player will adapt according to the format you put here
	"language": "en", // The language of the information to be brought by the TMDB API
	"apiKey": "" // Tu API Key de TMDB
}
 ```
3. Re-start the server and enjoy the server
4. 
## How do I order my series/movies in PATH?
Inside the folder that you will use as path in the .json, you must sort correctly your anime series or movies for it to work correctly. follow the next steps

1. You must get the anime ID from <a href="https://www.themoviedb.org/?language=es">TMDB</a>.
2. Once the id is obtained, create the folder that will simulate the series and name it as follows: ``{id}`` or  ``name-folder-{id}``
**EXAMPLE**:
<img src="https://raw.githubusercontent.com/evairx/animate-server/main/.github/doc/example-path-1.PNG?token=GHSAT0AAAAAACMXNXNF74RJDOFKD4GO2WRMZR5T7SQ"/>
3.   Once you have created the folder for the series, create another folder containing the seasons with the following name: ``season-{number}``
**EXAMPLE**:
<img src="https://raw.githubusercontent.com/evairx/animate-server/main/.github/doc/example-path-2.PNG?token=GHSAT0AAAAAACMXNXNE3EADFWV3MYC2YSVUZR5UAZQ"/>
## What video format can I use?

Well, the formats of the videos is important, since this will recognize the videos that are in your anime path and will configure the Animate Client player, the formats that you can use are as follows

 - [x] **MP4**: the option "format": "mp4" will recognize all chapters/movies ending in .mp4 and the player will adapt to play mp4 files

 - [x] **HLS**:  the "format" option: "hls" will recognize all chapters/movies ending in .m3u8 and the player will be adapted to play HLS

 - [x] **DASH**:   the "format" option: "dash" will recognize all chapters/movies ending in .mpd and the player will be adapted to play DASH
