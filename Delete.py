import time
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ===============================
# CONFIGURATION
# ===============================
API_KEY = 'YOUR_API_KEY'  # Your YouTube Data API key
VIDEO_ID = 'YOUR_VIDEO_ID'  # Video you want to monitor
TRIGGER_WORD = 'Type_A_Trigger_Word'  # Word that triggers deletion
CHECK_INTERVAL = 15  # Seconds between checking new comments

# ===============================
# SETUP LOGGING
# ===============================
logging.basicConfig(
    filename='video_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ===============================
# INITIALIZE YOUTUBE API
# ===============================
youtube = build('youtube', 'v3', developerKey=API_KEY)

# ===============================
# HELPER FUNCTIONS
# ===============================

def get_comments(video_id):
    """Fetch the latest comments on the video"""
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            order='time'  # Get newest comments first
        ).execute()
        return response.get('items', [])
    except HttpError as e:
        logging.error(f"Failed to fetch comments: {e}")
        return []

def delete_video(video_id):
    """Delete the video"""
    try:
        youtube.videos().delete(id=video_id).execute()
        logging.info(f"Video {video_id} deleted successfully!")
        print("Video deleted successfully!")
    except HttpError as e:
        logging.error(f"Failed to delete video: {e}")

def monitor_comments(video_id, trigger_word):
    """Continuously monitor comments for the trigger word"""
    logging.info(f"Starting comment monitor for video {video_id}")
    seen_comments = set()  # Track processed comments to avoid duplicates
    
    while True:
        comments = get_comments(video_id)
        
        for item in comments:
            comment_id = item['snippet']['topLevelComment']['id']
            comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay'].lower()
            
            if comment_id in seen_comments:
                continue  # Skip already processed comments

            seen_comments.add(comment_id)
            
            logging.info(f"Checked comment: {comment_text}")
            
            if trigger_word.lower() in comment_text:
                logging.info(f"Trigger word found in comment: {comment_text}")
                delete_video(video_id)
                return  # Stop monitoring after deletion
        
        time.sleep(CHECK_INTERVAL)

# ===============================
# MAIN EXECUTION
# ===============================
if __name__ == "__main__":
    try:
        monitor_comments(VIDEO_ID, TRIGGER_WORD)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped manually by user.")
        print("Monitoring stopped.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Error occurred: {e}")
