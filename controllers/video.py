from __future__ import unicode_literals
import logging
import cgi
import os
import youtube_dl
import boto3
import SQLmodels as SQLmodels
from sqlalchemy import exc
from datetime import datetime
from core.Initializer import db_inst
from urllib.parse import urlparse
from urllib.parse import parse_qs
from fastapi import HTTPException
from botocore.exceptions import NoCredentialsError


logging.basicConfig(level=logging.DEBUG)

# DB instantiation
db = db_inst.SessionLocal()
db_video = SQLmodels.Videos

class Video():

    __video_metadata = {}

    def __init__(self):
        return

    def get_video_by_id(self, video_id: str):
        return db.query(db_video).filter(db_video.id == video_id).first()

    def get_videos(self, skip: int = 0, limit: int = 100):
        return db.query(db_video).offset(skip).limit(limit).all()

    def create_video(self, video_url: str):
        self.__get_video_metadata(video_url)
        logging.info(self.__video_metadata)
        mp3_link = self.__get_video_s3_url()
        existing_video = self.get_video_by_id(video_id=self.__video_metadata['id'])
        if not existing_video:
            self.__download_video_as_mp3(video_url = video_url)
            try:
                new_video = db_video(id=self.__video_metadata['id'],
                                   source=cgi.escape(video_url), # sanitize videp
                                   mp3_link=mp3_link,
                                   created_at=datetime.now())
                db.add(new_video)
                db.commit()
            except exc.SQLAlchemyError as e:
                db.rollback()
                logging.critical("Could not save record on DB")
                logging.critical(e)
                raise HTTPException(status_code=500, detail="Error the the database connection")
        # increase download count and updated_at
        else:
            try:
                existing_video.download_count = existing_video.download_count + 1
                existing_video.updated_at = datetime.now()
                db.add(existing_video)
                db.commit()
            except exc.SQLAlchemyError as e:
                db.rollback()
                logging.critical("Could not update record on DB")
                logging.critical(e)
        return {'download_url': mp3_link}
    
    #
    # private functions
    #

    def __parse_video_id(self, video_url: str):
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

    def __get_video_metadata(self, video_url: str):
        try:
            with youtube_dl.YoutubeDL() as ydl:
                meta = ydl.extract_info(video_url, download=False)
                self.__video_metadata = {
                    'id': meta['id'],
                    'duration': meta['duration'],
                    'title': meta['title']
                }
                return True
        except:
            raise HTTPException(status_code=500, detail="Failed fetching video information")

    def __download_video_as_mp3(self, video_url: str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'verbose': True,
            'progress_hooks': [self.__upload_to_s3_hook]
        }
        logging.info("Starting video download")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if not self.__video_metadata['duration'] >= 1800: # this means video is over 10 mins long
                ydl.download([video_url])
                return True
            else:
                raise HTTPException(status_code=500, detail="Video is over 30 minutes long")

    def __upload_to_s3_hook(self, vid):
        # upload video once it has finished downloading
        if vid['status'] == 'finished':
            logging.critical(f"Uploading {vid['filename']} to S3")
            if os.getenv('AWS_ACCESS_KEY'):
                s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                      aws_secret_access_key=os.getenv('AWS_SECRETS_KEY'), 
                      region_name=os.getenv('AWS_REGION'))
            else:
                s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION'))

            try:
                s3.upload_file(vid['filename'], os.getenv('AWS_S3_BUCKET'), f"{self.__video_metadata['id']}.mp3", ExtraArgs={'ACL':'public-read'})
                logging.info(f"{vid['filename']} Upload Successful")
                return True
            except FileNotFoundError:
                logging.error(f"{vid['filename']} not found")
                raise HTTPException(status_code=500, detail="Unexpected Error")
            except NoCredentialsError:
                logging.error("AWS Credentials not found")
                raise HTTPException(status_code=500, detail="Internal Server Error")
    
    def __get_video_s3_url(self):
        # return link for video download on s3/cdn
        return f"https://{os.getenv('AWS_S3_BUCKET')}.s3.amazonaws.com/{self.__video_metadata['id']}.mp3"