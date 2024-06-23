import instaloader
import os

# Create an instance of Instaloader
L = instaloader.Instaloader(download_videos=True, download_geotags=False, download_comments=False, save_metadata=False)

# Login (optional but recommended to avoid rate limits)
username = 'feedom.hackathon'
password = 'Hackathon'
L.login(username, password)

# Specify the Instagram username whose reels you want to download
target_username = 'education'

# Create a directory to save the videos if it doesn't exist
os.makedirs('videos', exist_ok=True)

# Change the download directory
L.dirname_pattern = 'videos'

# Load the target user's profile
profile = instaloader.Hashtag.from_name(L.context, target_username)

# Iterate through the user's posts and download only reels (IGTV and regular posts are skipped)
for post in profile.get_posts_resumable():
    print(post.typename, post.is_video)
    if post.typename == 'GraphVideo' and post.is_video:
        print(f"Downloading {post.shortcode}")
        L.download_post(post, target=profile.username)
