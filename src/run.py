#! /usr/bin/env python3

from muse import Muse
import settings


if __name__ == "__main__":

    m = Muse(settings.words_to_connect, settings.words_to_avoid)
    m.load_df()
    m.get_clues()
