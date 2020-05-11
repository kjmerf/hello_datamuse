#! /usr/bin/env python3

import numpy as np
import pandas as pd
import requests


class Muse:
    def __init__(self, words_to_connect, words_to_avoid):
        self.url = "https://api.datamuse.com/words?"
        self.words_to_connect = [
            dct["word"] for dct in words_to_connect if dct["is_active"]
        ]
        self.words_to_avoid = [
            dct["word"] for dct in words_to_avoid if dct["is_active"]
        ]
        self.df = pd.DataFrame()

    def get_data(self, parameter, query):

        response = requests.get(f"{self.url}{parameter}={query.lower()}")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.status_code)

    def load_df(self, parameter="rel_jjb"):

        # for valid parameters see: http://www.datamuse.com/api/

        lst = []
        for query in self.words_to_connect + self.words_to_avoid:
            dct = {}
            response_lst = self.get_data(parameter, query)
            for response_dct in response_lst:
                dct = {}
                score = response_dct["score"]
                word = response_dct["word"]
                dct["query_to_connect"] = (
                    f"{query}: {score}" if query in self.words_to_connect else ""
                )
                dct["is_query_to_connect"] = (
                    True if query in self.words_to_connect else False
                )
                dct["query_to_avoid"] = (
                    f"{query}: {score}" if query in self.words_to_avoid else ""
                )
                dct["is_query_to_avoid"] = (
                    True if query in self.words_to_avoid else False
                )
                dct["word"] = word
                dct["score"] = score
                lst.append(dct)

        self.df = pd.DataFrame(lst)

        return True

    def get_clues(self, number_of_clues=25, metric="sum"):

        queries_to_connect = self.df[self.df["is_query_to_connect"]]
        queries_to_connect = (
            queries_to_connect.groupby(["word"])["query_to_connect"]
            .apply(", ".join)
            .reset_index()
        )
        queries_to_avoid = self.df[self.df["is_query_to_avoid"]]
        queries_to_avoid = (
            queries_to_avoid.groupby(["word"])["query_to_avoid"]
            .apply(", ".join)
            .reset_index()
        )

        stats = self.df[self.df["is_query_to_connect"]]
        stats = stats.groupby(["word"]).agg({"score": [np.size, np.sum, np.prod]})
        out = pd.merge(stats, queries_to_connect, on="word")
        out = pd.merge(out, queries_to_avoid, on="word", how="left")
        out.columns = ["word", "count", "sum", "product", "connections", "risks"]

        return out.nlargest(number_of_clues, "product")
