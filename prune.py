import os
import requests
from datetime import timedelta

from plexapi.server import PlexServer
from plexapi.video import Movie, Show
from datetime import datetime

# Define custom exceptions


class MissingRadarrMovie(Exception):
    pass


class MissingSonarrSeries(Exception):
    pass


class MissingTMDBID(Exception):
    pass


class MissingTVDBID(Exception):
    pass


audience_score = 7.0
sonarr_url = 'https://chaosinthecrd.lyra.usbx.me/sonarr/api/v3'
radarr_url = 'https://chaosinthecrd.lyra.usbx.me/radarr/api/v3'
plex_url = 'http://lyra-direct.usbx.me:13425'
diskspace_path = '/home/chaosinthecrd/MergerFS'
max_tb = 3
max_diskspace = max_tb * (1024 ** 4)
default_timeout = 60


def get_plex_film_tmdb_id(plex_film):
    # Quote from a Radarr developer: TMDb is usually better as it guarantees a
    # match, IMDb only gets matched if the TMDb entry has the correct IMDb ID
    # association. We don't actually talk to IMDb:
    # https://trash-guides.info/Radarr/Radarr-recommended-naming-scheme
    tmdb_scheme = 'tmdb://'
    for guid in plex_film.guids:
        if guid.id.startswith(tmdb_scheme):
            return int(guid.id[len(tmdb_scheme):])
    raise MissingTMDBID(
        f'Failed to find TMDB ID for Plex film "{plex_film.title}"!'
    )


def get_plex_tv_show_tvdb_id(plex_tv_show):
    tvdb_scheme = 'tvdb://'
    for guid in plex_tv_show.guids:
        if guid.id.startswith(tvdb_scheme):
            return int(guid.id[len(tvdb_scheme):])
    raise MissingTVDBID(
        f'Failed to find TVDB ID for Plex TV series "{plex_tv_show.title}"!'
    )


def find_radarr_movie(plex_film):
    try:
        tmdb_id = get_plex_film_tmdb_id(plex_film)
    except MissingTMDBID as e:
        print(f"Error finding TMDB ID for film {plex_film.title}: {e}")
        raise MissingRadarrMovie(
            f"Cannot find radarr movie for film {plex_film.title}."
        )

    for radarr_movie in radarr_movies_list:
        if tmdb_id == radarr_movie['tmdbId']:
            return radarr_movie
    raise MissingRadarrMovie(
        f'Failed to find Plex film "{plex_film.title}" in Radarr!'
    )


def find_sonarr_series(plex_tv_show):
    try:
        tvdb_id = get_plex_tv_show_tvdb_id(plex_tv_show)
    except MissingTVDBID as e:
        print(f"Error finding TVDB ID for show {plex_tv_show.title}: {e}")
        raise MissingSonarrSeries(
            f"Cannot find Sonarr series for show {plex_tv_show.title}."
        )
    for sonarr_series in sonarr_series_list:
        if tvdb_id == sonarr_series['tvdbId']:
            return sonarr_series
    raise MissingSonarrSeries(
        f'Failed to find Plex TV series "{plex_tv_show.title}" in Sonarr!'
    )


def delete_plex_film(plex_film):
    try:
        radarr_movie = find_radarr_movie(plex_film)
        print(f'Deleting movie "{radarr_movie["title"]}" from Radarr...')
    except MissingRadarrMovie as e:
        print(f"Cannot delete movie {plex_film.title} ({e}), continuing")
        return

    # https://github.com/Radarr/Radarr/blob/5dac6badf2fdbca9d83501c5d9f5607c3eea816d/src/Radarr.Api.V3/Movies/MovieController.cs#L251
    r = requests.delete(f'{radarr_url}/movie/{radarr_movie["id"]}?deleteFiles=true', headers={
                        "X-Api-Key": radarr_api_key}, timeout=default_timeout)
    r.raise_for_status()
    print(f'\n\n===\nMovie {plex_film.title} deleted successfully!\n===\n\n')


def delete_plex_tv_show(plex_tv_show):
    try:
        sonarr_series = find_sonarr_series(plex_tv_show)
        print(f'Deleting series "{sonarr_series["title"]}" from Sonarr...')
    except MissingSonarrSeries as e:
        print(f"Cannot delete series {e}, continuing")
        return

    # https://github.com/Sonarr/Sonarr/blob/b8481006932e904c93f46182ec4d91030d1461e1/src/Sonarr.Api.V3/Series/SeriesController.cs#L172
    r = requests.delete(f'{sonarr_url}/series/{sonarr_series["id"]}?deleteFiles=true', headers={
                        "X-Api-Key": sonarr_api_key}, timeout=default_timeout)
    r.raise_for_status()
    print('Series deleted successfully!')


def delete_plex_content(plex_content):
    if isinstance(plex_content, Movie):
        delete_plex_film(plex_content)
    elif isinstance(plex_content, Show):
        delete_plex_tv_show(plex_content)
    else:
        raise Exception(f'Unknown content type: {type(plex_content)}')
    # radarr and sonarr have a fit if they're spammed
    # time.sleep(60)

# Get content size on disk


def get_radarr_movie_size(radarr_movie):
    return radarr_movie['sizeOnDisk']


def get_sonarr_series_size(sonarr_series):
    return sonarr_series['statistics']['sizeOnDisk']


def get_plex_film_size(plex_film):
    radarr_movie = find_radarr_movie(plex_film)
    return get_radarr_movie_size(radarr_movie)


def get_plex_tv_show_size(plex_tv_show):
    sonarr_series = find_sonarr_series(plex_tv_show)
    return get_sonarr_series_size(sonarr_series)


def get_plex_content_size(plex_content):
    if isinstance(plex_content, Movie):
        return get_plex_film_size(plex_content)
    elif isinstance(plex_content, Show):
        return get_plex_tv_show_size(plex_content)
    else:
        raise Exception(f'Unknown content type: {type(plex_content)}')

# Get content time since last played


def get_plex_content_added_at(plex_content):
    return plex_content.addedAt


def get_plex_content_time_since_last_played(plex_content):
    added_at = plex_content.addedAt
    # https://github.com/pkkid/python-plexapi/blob/7580fc84a973b4f1eb4e1d709dc4a83d53b6afbf/plexapi/server.py#L633-L664
    history = plex_content.history()
    # If the content has never been played we use its time since it was added
    if len(history) == 0:
        return datetime.now() - added_at, True
    # ...otherwise we look at when it was last played
    else:
        # https://python-plexapi.readthedocs.io/en/latest/modules/base.html#plexapi.base.PlexHistory
        last_played_at = max([x.viewedAt for x in history])
        # If the content was added after it was last played then we assume it
        # was removed and then added again so we use the added time
        if added_at > last_played_at:
            last_played_at = added_at
    return datetime.now() - last_played_at, False


def get_audience_score(plex_content):
    return plex_content.audienceRating


if __name__ == "__main__":
    print(f'===\nPLEX PRUNER: {datetime.now()}\n---')

    if not os.path.exists(diskspace_path):
        raise Exception(f"Disk space path '{diskspace_path}' does not exist.")

    size_bytes = 0
    for path, dirs, files in os.walk(diskspace_path):
        for f in files:
            fp = os.path.join(path, f)
            size_bytes += os.path.getsize(fp)

    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    size_gb = size_mb / 1024
    used_percent = (size_bytes / max_diskspace) * 100

    print(f'CURRENT USAGE: {size_gb} GB ({used_percent} %)')

    # We always aim to have at least 10% of free space:
    # https://archive.kernel.org/oldwiki/btrfs.wiki.kernel.org/index.php/SysadminGuide.html#Balancing
    # We calculate the amount of space we need to free by deducting the amount
    # of free space we have away from the amount of free space we want
    space_left = max_diskspace - size_bytes
    space_to_free = (0.10 * max_diskspace) - space_left
    space_to_free_gb = space_to_free / 1024 ** 3

    # If we do not need to free up any space then we are done...
    if space_to_free <= 0:
        print(f'SPACE REQUIRED: 0 GB\n===')
        print("\nWe already have enough free space! quitting...")
        quit()

    print(f'SPACE REQUIRED: {space_to_free_gb} GB\n===')

    # # ...otherwise we make sure to free up a minimum amount of space so that we are not wasting work
    minimum_space_to_free = 100 * 1024 * 1024 * 1024  # 100 GiB
    if space_to_free < minimum_space_to_free:
        space_to_free = minimum_space_to_free

    # Login to Plex and retrieve content
    plex_token = os.environ['PLEX_TOKEN']
    if not plex_token:
        raise Exception("Missing environment variable: PLEX_TOKEN")
    plex = PlexServer(plex_url, plex_token)
    plex_films = plex.library.section('Movies').all()
    plex_tv_shows = plex.library.section('TV Shows').all()

    # Retrieve Radarr movies
    radarr_movie_url = "{0}/movie".format(radarr_url)
    radarr_api_key = os.environ['RADARR_API_KEY']
    if not radarr_api_key:
        raise Exception("Missing environment variable: RADARR_API_KEY")
    r = requests.get(radarr_movie_url, headers={
                     "X-Api-Key": radarr_api_key}, timeout=default_timeout)
    r.raise_for_status()
    radarr_movies_list = r.json()

    # Retrieve Sonarr series
    sonarr_series_url = "{0}/series".format(sonarr_url)
    sonarr_api_key = os.environ['SONARR_API_KEY']
    if not radarr_api_key:
        raise Exception("Missing environment variable: SONARR_API_KEY")
    r = requests.get(sonarr_series_url, headers={
                     "X-Api-Key": sonarr_api_key}, timeout=default_timeout)
    r.raise_for_status()
    sonarr_series_list = r.json()

    # Verify that we are not about to prune more than half of all Plex content
    plex_space_used = 0
    for radarr_movie in radarr_movies_list:
        plex_space_used += get_radarr_movie_size(radarr_movie)
    for sonarr_series in sonarr_series_list:
        plex_space_used += get_sonarr_series_size(sonarr_series)
    if 2 * space_to_free >= plex_space_used:
        raise Exception(
            'We are trying to prune more than half of all Plex content!')

    # Combine Plex films and TV shows
    plex_content_list = plex_films + plex_tv_shows

    space_freed = 0
    finished = False
    saved_content_list = []
    plex_tv_shows.sort(
        key=get_plex_content_time_since_last_played, reverse=True)

    # Delete content until we have freed up enough space
    print('we will start with tv shows as they are by far the bulkiest')
    for plex_content in plex_tv_shows:
        lastPlayed, never = get_plex_content_time_since_last_played(
            plex_content)
        title = plex_content.title
        score = plex_content.audienceRating if plex_content.audienceRating is not None else 0
        if never:
            print(f'{title} has never been watched!')
        if score > 8.5:
            print(
                f'{title} has a score of {score}, keeping...'
            )
            saved_content_list.append(plex_content)
            continue
        if not never and lastPlayed < timedelta(weeks=2):
            print(
                f'{title} was played recently. Lets keep it around for a while so others have the chance to watch')
            saved_content_list.append(plex_content)
            continue
        if never:
            if lastPlayed < timedelta(weeks=3):
                print(
                    f'{title} was added less than three weeks ago. Were simply going to skip this...')
                continue
            if score > 8.0:
                print(
                    f'{title} has a score of {score}, keeping...')
                saved_content_list.append(plex_content)
                continue
            if score < 6.7:
                print(f'{title} has a score of {score}. removing...')
                delete_plex_content(plex_content)
                continue

        # ...otherwise delete the content
        try:
            plex_content_size = get_plex_content_size(plex_content)
            # If we cannot find the content in Radarr/Sonarr or cannot determine its
            # TMDB/TVDB ID then skip it
        except (MissingRadarrMovie, MissingSonarrSeries, MissingTMDBID, MissingTVDBID) as e:
            print(e)
            continue
        delete_plex_content(plex_content)
        # Increase the amount of space freed
        space_freed += plex_content_size
        # If we have freed up enough space then we are done...
        if space_freed >= space_to_free:
            print("Plex has been successfully pruned!")
            quit()

    plex_films.sort(
        key=get_plex_content_time_since_last_played, reverse=True)

    # Delete content until we have freed up enough space
    for plex_content in plex_films:
        lastPlayed, never = get_plex_content_time_since_last_played(
            plex_content)
        title = plex_content.title
        score = plex_content.audienceRating if plex_content.audienceRating is not None else 0
        if never:
            print(f'{title} has never been watched!')
        if score > 8.5:
            print(f'{title} has a score of {score} saving...')
            saved_content_list.append(plex_content)
            continue
        if not never and lastPlayed < timedelta(weeks=3):
            print(f'{title} was played recently. Keeping')
            saved_content_list.append(plex_content)
            continue
        if never:
            if lastPlayed < timedelta(weeks=3):
                print(
                    f'{title} was added less than three weeks ago. Were simply going to skip this...')
                continue
            if score > 8.0:
                print(f'{title} has a score of {score}, keep for now.')
                saved_content_list.append(plex_content)
                continue
            if score < 6.7:
                print(f'{title} has a score of {score}. removing...')
                delete_plex_content(plex_content)
                continue

        # ...otherwise delete the content
        try:
            plex_content_size = get_plex_content_size(plex_content)
            # If we cannot find the content in Radarr/Sonarr or cannot determine its
            # TMDB/TVDB ID then skip it
        except (MissingRadarrMovie, MissingSonarrSeries, MissingTMDBID, MissingTVDBID) as e:
            print(e)
            continue
        delete_plex_content(plex_content)
        # Increase the amount of space freed
        space_freed += plex_content_size
        # If we have freed up enough space then we are done...
        if space_freed >= space_to_free:
            print("Plex has been successfully pruned!")
            quit()

    saved_content_list.sort(
        key=lambda x: x.audienceRating if x.audienceRating is not None else 0,
        reverse=False
    )

    print(
        f'purged {space_freed} of {space_to_free} needed.'
    )

    print(
        'purging by audience score only.'
    )

    for plex_content in saved_content_list:
        # If we have freed up enough space then we are done...
        if space_freed >= space_to_free:
            print("Plex has been successfully pruned!")
            quit()

        title = plex_content.title
        score = plex_content.audienceRating if plex_content.audienceRating is not None else 0
        # ...otherwise delete the content
        try:
            plex_content_size = get_plex_content_size(plex_content)
        # If we cannot find the content in Radarr/Sonarr or cannot determine its
        # TMDB/TVDB ID then skip it
        except (MissingRadarrMovie, MissingSonarrSeries, MissingTMDBID, MissingTVDBID) as e:
            print(f"Error calculating size for {plex_content.title}: {e}")
            continue

        print(f'{title} has a score of {score}, removing...')
        delete_plex_content(plex_content)
        # Increase the amount of space freed
        space_freed += plex_content_size
