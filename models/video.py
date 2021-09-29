"""
This is a pydantic model for Videos, which means this is just used for Video manipulation functions unrelarted to the DB
"""

import random
import os
import string
import logging
from urllib.parse import urlparse
from urllib.parse import parse_qs
import youtube_dl
import boto3
from botocore.exceptions import NoCredentialsError

logging.basicConfig(level=logging.DEBUG)


class VideoModel():
    def __init__(self):
        return

    def parse_video_id(self, video_url: str):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        query = urlparse(url = video_url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail?
        return None

    def download_as_mp3(self, video_url: string):
        ydl_opts = {
            'outtmpl': "/tmp/%(title)s.mp3",
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'restrictfilenames': True,
            'progress_hooks': [self.upload_to_s3],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    
    def upload_to_s3(self, vid):
        if vid['status'] == 'finished':
            logging.critical(f"Uploading {vid['filename']} to S3")
            s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                      aws_secret_access_key=os.getenv('AWS_SECRETS_KEY'), 
                      region_name=os.getenv('AWS_REGION'))
            try:
                s3.upload_file(vid['filename'], os.getenv('AWS_S3_BUCKET'), vid['filename'].split("/")[2])
                print("Upload Successful")
                return True
            except FileNotFoundError:
                print("The file was not found")
                return False
            except NoCredentialsError:
                print("Credentials not available")
                return False
        
        return
