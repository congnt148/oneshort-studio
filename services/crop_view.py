from moviepy.video.fx.all import crop

def crop_video_to_center(video_clip, center_x):
    height = video_clip.size[1]
    new_width = height * 9 / 16

    left = max(0, center_x - new_width / 2)
    right = min(video_clip.size[0], center_x + new_width / 2)

    if right - left < new_width:
        if left == 0:
            right = new_width
        else:
            left = video_clip.size[0] - new_width
    cropped_clip = crop(video_clip, x1=left, x2=right, y1=0, y2=height)
    return cropped_clip