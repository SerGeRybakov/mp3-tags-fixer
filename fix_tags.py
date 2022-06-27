"""MP3 tags fixer.

Fixes encoding of text tags for all non-ascii named files.
"""

import os
from argparse import ArgumentParser
from typing import Union

import music_tag
from music_tag import MetadataItem
from tqdm import tqdm


def recode_string_to_utf8(s: Union[str, MetadataItem]) -> Union[str, MetadataItem]:
    """Explicitly recodes string into UTF-8.

    :param s: any string or MetadataItem from an mp3-file.
    """
    if isinstance(s, MetadataItem):
        for idx, val in enumerate(s.values):
            encoded = val.encode('utf-8')
            s.values[idx] = encoded.decode('utf-8')
        return s
    s = s.encode('utf-8')
    return s.decode('utf-8')


def recode_one_file(file: music_tag.id3.Mp3File):
    """Recodes mp3 file text tags.

    :param file: opened MP3 file descriptor
    """
    try:
        for tag in ('tracktitle', 'artist', "album", 'albumartist', 'composer', 'genre', 'comment'):
            string: str = file.__getitem__(tag)
            recoded = recode_string_to_utf8(string)
            file.tag = recoded
        file.save()
    except Exception as e:
        # print(e)
        # continue
        raise


def recode_tags(base_path):
    """Changes file permissions to read/write and recodes all text tags in non-ascii named files into "UTF-8".

    :param base_path: absolute path to a root directory with mp3-collection
    """
    rus_files = []
    for r, d, files in os.walk(base_path):
        for f in files:
            if not f.isascii() and f.lower().endswith('.mp3'):
                rus_files.append(os.path.abspath(os.path.join(r, f)))

    for filename in tqdm(rus_files, desc="NON-ASCII FILES"):
        try:
            os.chmod(filename, 0o777)
            file: music_tag.id3.Mp3File = music_tag.load_file(filename)
            recode_one_file(file)
        except Exception as e:
            # print(e)
            # continue
            raise


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', help="absolute root mp3 directory path")
    args = parser.parse_args()
    abs_folder_path = args.path
    if not abs_folder_path:
        abs_folder_path = input("absolute root mp3 directory path: ")

    recode_tags(abs_folder_path)
