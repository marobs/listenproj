# listenproj
Usage:
1. Register for an account by going to /register. This will create a username and password and store them in the dao.
2. This will redirect to /login (because we're not smart enough to log you in immediately after registering).
3. After logging in, the site will check if you have an access/refresh token from Spotify. If not, it will prompt the oAuth flow with Spotify.
4. The result of that is a refresh and access token which are then stored in the spotify_token_dao and determine our app's idea of being auth'd.
5. Next, navigate to /reddit, which will:
    1. Query Reddit for the top 25 posts of r/listentothis
    2. Take those tracks and search Spotify for the most-related track
    3. Query Spotify for the user's Spotify ID which will be used for creating a playlist.
    4. Create a playlist for the user
    5. Fill the playlist with the found songs
