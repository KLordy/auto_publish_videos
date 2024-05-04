from datetime import timedelta

from datetime import datetime


def generate_schedule_time_today(total_videos, videos_per_day, daily_times=None, timestamps=False, start_days=0):
    """
    Generate a schedule for video uploads, starting from the next day.

    Args:
    - total_videos: Total number of videos to be uploaded.
    - videos_per_day: Number of videos to be uploaded each day.
    - daily_times: Optional list of specific times of the day to publish the videos.
    - timestamps: Boolean to decide whether to return timestamps or datetime objects.
    - start_days: Start from after start_days.

    Returns:
    - A list of scheduling times for the videos, either as timestamps or datetime objects.
    """
    if videos_per_day <= 0:
        raise ValueError("videos_per_day should be a positive integer")

    if daily_times is None:
        # Default times to publish videos if not provided
        daily_times = [6, 11, 14, 16, 22]

    if videos_per_day > len(daily_times):
        raise ValueError("videos_per_day should not exceed the length of daily_times")

    # Generate timestamps
    schedule = []
    current_time = datetime.now()

    # 先依据当前时间的hour，来找到daily_times中最近的下一个hour的idx，从这个hour的idx开始发布视频


    for video in range(total_videos):
        # '//' 两数相除，并且向下取整，如果有10个视频，每日发布4个视频，则[0-3]第二天发；[4-7]第三天发；[8-10]则第四天发
        day = video // videos_per_day + start_days + 1  # +1 to start from the next day
        daily_video_index = video % videos_per_day

        # Calculate the time for the current video
        hour = daily_times[daily_video_index]
        time_offset = timedelta(days=day, hours=hour - current_time.hour, minutes=-current_time.minute,
                                seconds=-current_time.second, microseconds=-current_time.microsecond)
        timestamp = current_time + time_offset

        schedule.append(timestamp)

    if timestamps:
        schedule = [int(time.timestamp()) for time in schedule]
    return schedule
