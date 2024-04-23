

def trans2tvbox(m3u_file, tvbox_file):
    with open(m3u_file, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    channels = {}
    current_genre = None

    # Parse the m3u playlist
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF'):
            info = line.split('"')
            channel_name = info[3]
            current_genre = info[1]
            if channel_name not in channels:
                channels[channel_name] = {}
        elif line and not line.startswith('#'):
            channel_url = line
            if current_genre not in channels[channel_name]:
                channels[channel_name][current_genre] = [channel_url]
            else:
                channels[channel_name][current_genre].append(channel_url)

    # Generate the tvbox config file
    with open(tvbox_file, 'w', encoding="utf-8") as f:
        for genre, channel_list in channels.items():
            f.write('{},#genre#\n'.format(genre))
            for channel_name, channel_urls in channel_list.items():
                for url in channel_urls:
                    if url is not None:
                        f.write(channel_name + "," + url + "\n")

    print('Conversion complete. The tvbox config file has been saved as', tvbox_file)

if __name__ == '__main__':
    m3u_file = 'iptv.m3u'
    tvbox_file = 'result_config.txt'
    trans2tvbox(m3u_file, tvbox_file)