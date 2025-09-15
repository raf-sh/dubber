# Proof of concept video
https://www.youtube.com/watch?v=nVjUJAKRFbg

# Basic usage
`python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw`

## Other options
### `--language` target language (only Tatar is implemented atm)
`python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --language tt`

### `--merge-segments` merges subtitle segments up to 10s to get smoother voiceover
`python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --merge-segments`

### `--add-silence` adds silence blocks into gaps, to decrease the amount of voice speed changes
`python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --add-silence`

### Use cookies to overcome YouTube error on retries in a short window of time
`python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --youtube-cookies-path cookies.txt`

## Export cookies into cookies.txt
`yt-dlp --cookies cookies.txt --cookies-from-browser firefox`
