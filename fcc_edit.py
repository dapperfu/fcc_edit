#!/usr/bin/python3 python3
import sys

assert (
    len(sys.argv) == 2
), f"""Please select a movie: ./fcc_edit.py <movie>

Subtitles must be stored with the same filename but extension .srt.

Only works with .srt subtitle files.
"""


from moviepy.editor import VideoFileClip, concatenate
import srt
from ffprobe import FFProbe
import os

movie_file = os.path.abspath(sys.argv[1])

base, ext = os.path.splitext(movie_file)

sub_file = f"{base}.srt"

assert os.path.exists(
    sub_file
), f"Check to make sure the subtitles file {sub_file} exists."

subs_text = open(sub_file).read()

subs = list(srt.parse(subs_text))
new_movie = list()

sub = subs[0]

# Assume movie doesn't start out with swearing.
last_clean_scene = sub
# For each of the remaining subtitles.
for idx, sub in enumerate(subs[1:]):
    # Check if a badword is in the badwords list.
    for badword in ["shit", "damn"]:
        # If the badword is found in the subtitle
        if badword in sub.content.lower():
            # Add the a clean scene to the new fcc edit
            new_movie.append(
                [
                    last_clean_scene.start.seconds
                    + last_clean_scene.start.microseconds / 100000,
                    sub.start.seconds + sub.start.microseconds / 100000,
                ]
            )
            # Set the next last clean scene as the scene after the swearing.
            last_clean_scene = subs[idx + 2]


video = VideoFileClip(movie_file)
""" Concatenate cuts and generate a video file. """
final = concatenate([video.subclip(start, end) for (start, end) in new_movie])

metadata = FFProbe(movie_file)
fps = round(metadata.video[0].frames() / metadata.video[0].duration_seconds(), 2)
fcc_edit = f"{base}.fcc.{ext}"
final.write_videofile(fcc_edit, fps=fps)