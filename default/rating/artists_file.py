VK_NAME_TAG = "vk:"
YT_USER_TAG = "youtube-user:"
YT_CHANNEL_TAG = "youtube-channel-id:"
GOOGLE_TRENDS_TAG = "google-trends-term:"
YANDEX_WORDSTAT_TAG = "yandex_wordstat:"
RUSSIAN_TAG = "russian:"
ACTIVE_TAG = "active:"


class ArtistFromFile(object):
    def __init__(self, name='', youtube_channel_id='', youtube_user='', google_trends_term='', yandex_wordstat='',
                 is_russian=False, is_active=True, vk_name=''):
        self.name = name
        self.youtube_channel_id = youtube_channel_id
        self.youtube_user = youtube_user
        self.is_russian = is_russian
        self.is_active = is_active
        self.google_trends_term = google_trends_term
        self.yandex_wordstat = yandex_wordstat
        self.vk_name = vk_name


class ArtistsReader(object):

    def read(self, lines, is_russian):
        artists = []
        a = ArtistFromFile()
        for line in lines:
            if line.startswith(YT_USER_TAG):
                a.youtube_user = line[len(YT_USER_TAG):].strip()

            elif line.startswith(YT_CHANNEL_TAG):
                a.youtube_channel_id = line[len(YT_CHANNEL_TAG):].strip()

            elif line.startswith(GOOGLE_TRENDS_TAG):
                a.google_trends_term = line[len(GOOGLE_TRENDS_TAG):].strip()

            elif line.startswith(YANDEX_WORDSTAT_TAG):
                a.yandex_wordstat = line[len(YANDEX_WORDSTAT_TAG):].strip()

            elif line.startswith(ACTIVE_TAG):
                a.is_active = self.__parse_bool(line[len(ACTIVE_TAG):])

            elif line.startswith(RUSSIAN_TAG):
                a.is_russian = self.__parse_bool(line[len(RUSSIAN_TAG):])

            elif line.startswith(VK_NAME_TAG):
                a.vk_name = line[len(VK_NAME_TAG):].strip()

            elif a.name != line:
                if a.name:
                    artists.append(a)
                a = ArtistFromFile(name=unicode(line), is_russian=is_russian)

        artists.append(a)
        return artists

    def __parse_bool(self, text):
        return True if text.strip().lower() == "true" else False


class ArtistsWriter(object):
    def __init__(self, response):
        self.writer = response

    def write(self, artists):
        for a in artists:
            self.write_artist(a)

    def write_artist(self, artist):
        self.writer.write(artist.name + "\r\n")
        self.__write_attr(VK_NAME_TAG, artist.vk_name)
        self.__write_attr(YT_CHANNEL_TAG, artist.youtube_channel_id)
        self.__write_attr(YT_USER_TAG, artist.youtube_user)
        self.__write_attr(YANDEX_WORDSTAT_TAG, artist.yandex_wordstat_param)
        self.__write_attr(GOOGLE_TRENDS_TAG, artist.google_trends_term)
        self.__write_bool_attr(RUSSIAN_TAG, artist.is_russian)
        if not artist.is_active:
            self.__write_attr(ACTIVE_TAG, artist.is_active)

    def __write_attr(self, tag, value):
        if value:
            self.writer.write("\t{} {}\r\n".format(tag, value.encode('utf-8')))

    def __write_bool_attr(self, tag, value):
        text = 'True' if value else 'False'
        self.__write_attr(tag, text)

