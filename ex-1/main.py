import requests

## CONSTANTS
API_URL = "http://localhost:8000/api"
GRAPHQL_URL = "http://localhost:4000/graphql"
TRACKS_TABLE = "/tables/tracks/rows"
ARTISTS_TABLE = "/tables/artists/rows"
PLAYLISTS_TABLE = "/tables/playlists/rows"
PLAYLIST_TRACK_TABLE = "/tables/playlist_track/rows"
ALBUMS_TABLE = "/tables/albums/rows"

## HELPER FUNCTIONS
class Helper:
    def __init__(self) -> None:
        pass
    
    def get_properties(self, array, property):
        return [item[property] for item in array]
    
    def get_nested_properties(self, array, property):
        # nested list comprehension
        return [item[property] for sublist in array for item in sublist]

    # Filter dictionary to only include the keys specified
    def filter_dictionary(self, input, keys):
        result = []
        for dictionary in input:
            result.append({key: dictionary[key] for key in keys})
        return result

    # Concat 2 lists of dictionaries into 1 list of dictionaries by matching key, value
    def concat_dictionaries(self, list1, list2, key):
        result = []
        for item in list1:
            for item2 in list2:
                if item[key] == item2[key]:
                    result.append({**item, **item2})
        return result

    def change_key(self, input, key, new_key):
        result = []
        for dictionary in input:
            dictionary[new_key] = dictionary.pop(key)
            result.append(dictionary)
        return result

## REST API CLASSES
class RestAPI:
    def __init__(self) -> None:
        print("RestAPI: \n")

    def _get(self, url):
        return requests.get(url).json()["data"]

    def get_artist_info(self, artistid):
        return self._get(f"{API_URL}{ARTISTS_TABLE}?_filters=artistid:{artistid}")

    def get_artistid(self, artist):
        return self._get(f"{API_URL}{ARTISTS_TABLE}?_search={artist}")[0]["ArtistId"]

    def get_playlistsid(self, playlist):
        return self._get(f"{API_URL}{PLAYLISTS_TABLE}?_search={playlist}")[0][
            "PlaylistId"
        ]

    def get_albumsid(self, artistid):
        return self._get(f"{API_URL}{ALBUMS_TABLE}?_filters=artistid:{artistid}")

    # Automatically call get request until all results are found or until the 'next' is null
    def get_all_results(self, url, search_key, match_key):
        results = []
        while url:
            response = requests.get(url)
            data = response.json()
            for item in data["data"]:
                if item[search_key] in match_key:
                    results.append(item)
            if not data["next"]:
                break
            url = f'{API_URL}{data["next"]}'
        return results

## GRAPHQL CLASSES
class GraphQL:
    def __init__(self) -> None:
        print("\nGraphQL: \n")

    def query(self, query):
        return requests.post(
            GRAPHQL_URL,
            json={"query": query},
        ).json()["data"]

## MAIN
## REST API
REST_API = RestAPI()
Helper = Helper()

part1_aritstid = REST_API.get_artistid("Red Hot Chili Peppers")
part1_albums = REST_API.get_albumsid(part1_aritstid)
part1_answer = Helper.get_properties(part1_albums, "Title")
print('Part 1: Albums by the artist “Red Hot Chili Peppers.”:')
for album in part1_answer:
    print(album)

part2_aritstid = REST_API.get_artistid("u2")
part2_albums = REST_API.get_albumsid(part2_aritstid)
part2_albumsid = Helper.get_properties(part2_albums, "AlbumId")
part2_all = REST_API.get_all_results(
    f"{API_URL}{TRACKS_TABLE}?_filters=AlbumId:{part2_albumsid}&_extend=GenreId",
    "AlbumId",
    part2_albumsid,
)
part2_genreid_data = Helper.get_properties(part2_all, "GenreId_data")
part2_answer = list(set(Helper.get_properties(part2_genreid_data, "Name")))
print('\nPart 2: Genres associated with the artist “U2.”:')
for genre in part2_answer:
    print(genre)

part3_playlistid = REST_API.get_playlistsid("Grunge")
part3_tracks = REST_API.get_all_results(
    f"{API_URL}{PLAYLIST_TRACK_TABLE}?_filters=PlaylistId:{part3_playlistid}",
    "PlaylistId",
    [part3_playlistid],
)
part3_trackid = Helper.get_properties(part3_tracks, "TrackId")
part3_all_tracks = REST_API.get_all_results(
    f"{API_URL}{TRACKS_TABLE}?_filters=TrackId:{part3_trackid}&_extend=AlbumId",
    "TrackId",
    part3_trackid,
)
part3_filter_tracks = Helper.filter_dictionary(part3_all_tracks, ["Name", "AlbumId"])
part3_filter_tracks = Helper.change_key(part3_filter_tracks, "Name", "TrackName")
part3_album_id = list(set(Helper.get_properties(part3_filter_tracks, "AlbumId")))
part3_all_albums = REST_API.get_all_results(
    f"{API_URL}{ALBUMS_TABLE}?_filters=AlbumId:{part3_album_id}",
    "AlbumId",
    part3_album_id,
)
part3_aritst_id = list(set(Helper.get_properties(part3_all_albums, "ArtistId")))
part3_artist = REST_API.get_artist_info(part3_aritst_id)
part3_filter_albums = Helper.filter_dictionary(
    part3_all_albums, ["Title", "AlbumId", "ArtistId"]
)
part3_joined = Helper.concat_dictionaries(
    part3_filter_tracks, part3_filter_albums, "AlbumId"
)
part3_second_joined = Helper.concat_dictionaries(part3_joined, part3_artist, "ArtistId")
part3_answer = Helper.filter_dictionary(
    part3_second_joined, ["TrackName", "Title", "Name"]
)
print('\nPart 3: Names of tracks on the playlist “Grunge” and their associated artists and albums.')
for track in part3_answer:
    print(f'{track["TrackName"]}, {track["Name"]}, {track["Title"]}')

## GRAPHQL
GRAPH_QL = GraphQL()
part1_query = """
{
  artist(where: {name:"Red Hot Chili Peppers"})  {
    albums {
      title
    }
  }
}
"""
part1_query_res = GRAPH_QL.query(part1_query)
part1_answer = Helper.get_properties(part1_query_res["artist"]["albums"], "title")
print('Part 1: Albums by the artist “Red Hot Chili Peppers.”:')
for album in part1_answer:
    print(album)

part2_query = """
{
  artist(where: {name:"U2"})  {
    albums {
      tracks {
        genre {
          name
        }
      }
    }
  }
}
"""
part2_query_res = GRAPH_QL.query(part2_query)
part2_query_res = part2_query_res["artist"]["albums"]
part2_query_res = Helper.get_properties(part2_query_res, "tracks")
part2_flatten = Helper.get_nested_properties(part2_query_res, "genre")
part2_answer = list(set(Helper.get_properties(part2_flatten, "name")))
print('\nPart 2: Genres associated with the artist “U2.”:')
for genre in part2_answer:
    print(genre)

part3_query = """
{
  playlist(where: {name:"Grunge"})  {
    tracks {
      name
      album {
        title
        artist {
          name
        }
      }
    }
  }
}
"""
part3_query_res = GRAPH_QL.query(part3_query)
part3_answer = part3_query_res["playlist"]["tracks"]
print('\nPart 3: Names of tracks on the playlist “Grunge” and their associated artists and albums.')
for track in part3_answer:
    print(f'{track["name"]}, {track["album"]["artist"]["name"]}, {track["album"]["title"]}')