# Basic usage
python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw

# With specific target language
python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --language tt

# Enable subtitle segment merging
python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --merge-segments

# Add silence buffers instead of speeding up audio
python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --add-silence

# Use cookies for video download
python dubber.py https://www.youtube.com/watch?v=NLtnm_bRzPw --youtube-cookies-path cookies.txt

## Export cookies
yt-dlp --cookies cookies.txt --cookies-from-browser firefox