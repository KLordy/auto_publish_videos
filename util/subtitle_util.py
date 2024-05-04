import re


def vtt_to_srt(vtt_file, srt_file):
    with open(vtt_file, 'r') as vtt:
        vtt_content = vtt.read()

    # Remove unnecessary VTT tags
    vtt_content = re.sub(r'<[^>]+>', '', vtt_content)

    # Convert time format from HH:MM:SS.MMM to HH:MM:SS,MMM
    vtt_content = re.sub(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})', r'\1:\2:\3,\4', vtt_content)

    # Split the content into individual subtitle blocks
    subtitle_blocks = vtt_content.strip().split('\n\n')

    # Generate the SRT content
    srt_content = ''
    for i, block in enumerate(subtitle_blocks, start=1):
        lines = block.strip().split('\n')
        time_line = lines[0]
        start_time = ''
        end_time = ''
        # Handle different time format variations
        if ' --> ' in time_line:
            start_time, end_time = time_line.split(' --> ')
        elif ' align:start position:0%' in time_line:
            start_time, end_time = re.findall(r'(\d{2}:\d{2}:\d{2},\d{3})', time_line)

        subtitle_text = '\n'.join(lines[1:])
        srt_content += f"{i}\n{start_time} --> {end_time}\n{subtitle_text}\n\n"

    # Write the SRT content to a file
    with open(srt_file, 'w') as srt:
        srt.write(srt_content)

