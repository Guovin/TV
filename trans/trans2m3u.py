import logging

logger = logging.getLogger("tv")


def trans2m3u(tvbox_file, m3u_file):
    with open(tvbox_file, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    channels = {}
    current_genre = None

    # Parse the tvbox file
    for line in lines:
        line = line.strip()
        if line.endswith('#genre#'):
            current_genre = line.split(',')[0]
        elif line:
            channel_name, channel_url = line.split(',')
            if current_genre not in channels:
                channels[current_genre] = []
            channels[current_genre].append((channel_name, channel_url))

    # Generate the m3u playlist
    with open(m3u_file, 'w', encoding="utf-8") as f:
        for genre, channel_list in channels.items():
            f.write("#EXTM3U\n")
            for channel_name, channel_url in channel_list:
                f.write(
                    '#EXTINF:-1 tvg-name="{channel_name}" group-title="{genre}",{channel_name}\n{channel_url}\n'.format(
                        channel_name=channel_name, genre=genre, channel_url=channel_url))
            f.write('\n')

    logger.info('Conversion complete. The m3u playlist has been saved as', m3u_file)


if __name__ == '__main__':
    tvbox_file = '../user_result.txt'
    m3u_file = '../playlist.m3u'
    trans2m3u(tvbox_file, m3u_file)
