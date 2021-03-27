playlists = {}


def get_playlist_for_date(date):
    global playlists
    if date in playlists:
        return playlists[date]
    return None


def add_playlist_for_date(date, tracks):
    global playlists
    if date not in playlists:
        playlists[date] = tracks
