"""A video player class."""
import pywin32_bootstrap
from .video_library import VideoLibrary
from random import choice


class VideoPlayer:
    """A class used to represent a Video Player."""

    def __init__(self):
        global current_video, paused, playlistDB, playlist_case_map, flag_of_all_videos, error_messages
        current_video = False
        paused = False
        playlistDB = {}
        playlist_case_map = {}
        flag_of_all_videos = {}
        # some of the repeating error phases saved here.
        error_messages = {'no_vid': 'Video does not exist',
                          'no_vid_playing': "No video is currently playing",
                          'not_paused': 'Video is not paused',
                          'no_playlist': 'Playlist does not exist',
                          'playlist_exist': 'A playlist with the same name already exists',
                          'not_in_playlist': 'Video is not in playlist',
                          'already_flagged': f'Video is currently flagged (reason: %s)',
                          'already_added': 'Video already added',
                          'not_flagged': 'Video is not flagged'
                          }
        self._video_library = VideoLibrary()

    def is_id_real(self, video_id):
        """
        return video. If flagged, return the reason, too.
        :param video_id: The video_id in question.
        """
        video_in_question = self._video_library.get_video(video_id=video_id)
        if video_in_question is None:
            return False, False
        elif video_in_question in flag_of_all_videos:
            return video_in_question, flag_of_all_videos[video_in_question]
        else:
            return video_in_question, False

    def get_all_videos_not_flagged(self):
        return list(self._video_library.get_all_videos() - flag_of_all_videos.keys())

    def video_info_formatting(self, vid):
        """
        Show the video info
        :param vid: The video in question
        """
        tags = " ".join(list(vid.tags))
        output = f"{vid.title} ({vid.video_id}) [{tags}]"
        if vid in flag_of_all_videos:
            output += f' - FLAGGED (reason: {flag_of_all_videos[vid]})'
        return output

    def number_of_videos(self):
        num_videos = len(self._video_library.get_all_videos())
        print(f"{num_videos} videos in the library")

    def show_all_videos(self):
        """Returns all videos."""
        list_videos = self._video_library.get_all_videos()
        list_videos.sort(key=lambda _videos: _videos.title)
        print("Here's a list of all available videos:")
        for vid in list_videos:
            print(self.video_info_formatting(vid))

    def play_video(self, video_id):
        """Plays the respective video.

        Args:
            video_id: The video_id to be played.
        """
        global current_video, paused
        video, flag_reason = self.is_id_real(video_id)
        paused = False
        local_error_message = "Cannot play video: "

        # if video do not exist
        if video is False:
            print(local_error_message + error_messages['no_vid'])
        # if video is flagged
        elif flag_reason is not False:
            print(local_error_message + error_messages['already_flagged'] % flag_reason)
        else:
            if current_video is not False:
                print(f"Stopping video: {current_video.title}")
            current_video = video
            print(f"Playing video: {video.title}")

    def stop_video(self):
        """Stops the current video."""
        global current_video

        if current_video is not False:
            print(f"Stopping video: {current_video.title}")
            current_video = False
        else:
            print("Cannot stop video: " + error_messages['no_vid_playing'])

    def play_random_video(self):
        """Plays a random video from the video library."""
        list_playable_videos = self.get_all_videos_not_flagged()
        if len(list_playable_videos) == 0:
            print('No videos available')
        else:
            random_video = choice(list_playable_videos)
            self.play_video(random_video.video_id)

    def pause_video(self):
        """Pauses the current video."""
        global paused, current_video
        if current_video is False:
            print("Cannot pause video: " + error_messages['no_vid_playing'])
        elif paused:
            print(f"Video already paused: {current_video.title}")
        else:
            paused = True
            print(f"Pausing video: {current_video.title}")

    def continue_video(self):
        """Resumes playing the current video."""
        global paused, current_video
        if current_video is False:
            print("Cannot continue video: " + error_messages['no_vid_playing'])
        elif not paused:
            print(f"Cannot continue video: " + error_messages['not_paused'])
        else:
            paused = False
            print(f"Continuing video: {current_video.title}")

    def show_playing(self):
        """Displays video currently playing."""
        global paused, current_video
        if current_video is False:
            print("No video is currently playing")
        else:
            print("Currently playing: " + self.video_info_formatting(current_video) + '%s'
                  % (" - PAUSED" if paused else ""))

    def is_playlist_real(self, playlist_name):
        """Checks if the playlist already exist.
        if exists, return the original playlist name
        if not, return False

        Args:
            playlist_name: The playlist name.
        """
        if not playlist_name.lower() in playlist_case_map.keys():
            original_playlist_name = False
        else:
            original_playlist_name = playlist_case_map[playlist_name.lower()]
        return original_playlist_name

    def create_playlist(self, playlist_name):
        """Creates a playlist with a given name.

        Args:
            playlist_name: The playlist name.
        """
        if self.is_playlist_real(playlist_name) is False:
            playlist_case_map[playlist_name.lower()] = playlist_name
            playlistDB[playlist_name] = []
            print(f"Successfully created new playlist: {playlist_name}")
        else:
            print("Cannot create playlist: A playlist with the same name already exists")

    def add_to_playlist(self, playlist_name, video_id):
        """Adds a video to a playlist with a given name.

        Args:
            playlist_name: The playlist name.
            video_id: The video_id to be added.
        """
        add = False
        video, flag_reason = self.is_id_real(video_id)
        original_playlist_name = self.is_playlist_real(playlist_name)
        local_error_message = f"Cannot add video to {playlist_name}: "

        if original_playlist_name is False:
            print(local_error_message + error_messages['no_playlist'])

        elif video is False:
            print(local_error_message + error_messages['no_vid'])

        elif flag_reason is not False:
            print(local_error_message + error_messages['already_flagged'] % flag_reason)

        elif video in playlistDB[original_playlist_name]:
            print(local_error_message + error_messages['already_added'])
        else:
            add = True

        if add:
            playlistDB[original_playlist_name].append(video)
            print(f'Added video to {playlist_name}: {video.title}')

    def show_all_playlists(self):
        """Display all playlists."""
        playlistlist = sorted(list(playlistDB.keys()), key=str.lower)

        if len(playlistlist) is 0:
            print('No playlists exist yet')
        else:
            print('Showing all playlists:')
            for playlist in playlistlist:
                print(f'    {playlist}')

    def show_playlist(self, playlist_name):
        """Display all videos in a playlist with a given name.

        Args:
            playlist_name: The playlist name.
        """
        original_playlist_name = self.is_playlist_real(playlist_name)
        if original_playlist_name is False:
            print(f'Cannot show playlist {playlist_name}: ' + error_messages['no_playlist'])
        else:
            list_of_videos = playlistDB[original_playlist_name]

            print(f'Showing playlist: {playlist_name}')
            if len(list_of_videos) == 0:
                print('No videos here yet')
            else:
                for video in list_of_videos:
                    print(self.video_info_formatting(video))

    def remove_from_playlist(self, playlist_name, video_id):
        """Removes a video to a playlist with a given name.

        Args:
            playlist_name: The playlist name.
            video_id: The video_id to be removed.
        """
        remove = False
        video, _ = self.is_id_real(video_id)
        original_playlist_name = self.is_playlist_real(playlist_name)
        cannot_remove = f"Cannot remove video from {playlist_name}: "

        if original_playlist_name is False:
            print(cannot_remove + error_messages['no_playlist'])
        elif video is False:
            print(cannot_remove + error_messages['no_vid'])
        elif video not in playlistDB[original_playlist_name]:
            print(cannot_remove + error_messages['not_in_playlist'])
        else:
            remove = True

        if remove:
            playlistDB[original_playlist_name].remove(video)
            print(f'Removed video from {playlist_name}: {video.title}')

    def clear_playlist(self, playlist_name):
        """Removes all videos from a playlist with a given name.

        Args:
            playlist_name: The playlist name.
        """
        original_playlist_name = self.is_playlist_real(playlist_name)
        if original_playlist_name is False:
            print(f'Cannot clear playlist {playlist_name}: ' + error_messages['no_playlist'])
        else:
            playlistDB[original_playlist_name].clear()
            print(f'Successfully removed all videos from {playlist_name}')

    def delete_playlist(self, playlist_name):
        """Deletes a playlist with a given name.

        Args:
            playlist_name: The playlist name.
        """
        original_playlist_name = self.is_playlist_real(playlist_name)
        if original_playlist_name is False:
            print(f'Cannot delete playlist {playlist_name}: ' + error_messages['no_playlist'])
        else:
            del playlistDB[original_playlist_name]
            del playlist_case_map[original_playlist_name.lower()]
            print(f'Deleted playlist: {playlist_name}')

    def search_display(self, key_word, match_list):
        """Display search results using match list

        :param key_word: search term or video tag
        :param match_list: list of videos that match with the search
        :return:
        """
        if len(match_list) == 0:
            print(f'No search results for {key_word}')
        else:
            match_list.sort(key=lambda _videos: _videos.title)
            print(f'Here are the results for {key_word}:')
            for index, vid in enumerate(match_list):
                print(f'{index + 1}) ' + self.video_info_formatting(vid))

            print('Would you like to play any of the above? If yes, specify the number of the video.')
            print("If your answer is not a valid number, we will assume it's a no.")
            index_wanted_raw = input()
            try:
                index_wanted = int(index_wanted_raw) - 1
                self.play_video(match_list[index_wanted].video_id)
            except:
                pass

    def search_videos(self, search_term):
        """Display all the videos whose titles contain the search_term.

        Args:
            search_term: The query to be used in search.
        """
        match_list = [vid for vid in self.get_all_videos_not_flagged() if search_term.lower() in vid.title.lower()]
        self.search_display(search_term, match_list)

    def search_videos_tag(self, video_tag):
        """Display all videos whose tags contains the provided tag.

        Args:
            video_tag: The video tag to be used in search.
        """
        match_list = [vid for vid in self.get_all_videos_not_flagged() if video_tag.lower() in vid.tags]
        self.search_display(video_tag, match_list)

    def flag_video(self, video_id, flag_reason="Not supplied"):
        """Mark a video as flagged.

        Args:
            video_id: The video_id to be flagged.
            flag_reason: Reason for flagging the video.
        """
        global current_video
        video, flag_reason_old = self.is_id_real(video_id)
        if video is False:
            print('Cannot flag video: ' + error_messages['no_vid'])
        elif flag_reason_old is not False:
            print('Cannot flag video: Video is already flagged')
        else:
            flag_of_all_videos[video] = flag_reason
            if current_video == video:
                self.stop_video()
            print(f"Successfully flagged video: {video.title} (reason: {flag_reason})")

    def allow_video(self, video_id):
        """Removes a flag from a video.

        Args:
            video_id: The video_id to be allowed again.
        """
        video, flag_reason = self.is_id_real(video_id)

        if video is False:
            print('Cannot remove flag from video: ' + error_messages['no_vid'])
        elif flag_reason is False:
            print('Cannot remove flag from video: ' + error_messages['not_flagged'])
        else:
            del flag_of_all_videos[video]
            print(f'Successfully removed flag from video: {video.title}')
