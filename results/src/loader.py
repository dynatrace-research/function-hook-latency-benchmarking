# Copyright 2023 Dynatrace LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Portions of this code, as identified in remarks, are provided under the
# Creative Commons BY-SA 4.0 or the MIT license, and are provided without
# any warranty. In each of the remarks, we have provided attribution to the
# original creators and other attribution parties, along with the title of
# the code (if known) a copyright notice and a link to the license, and a
# statement indicating whether or not we have modified the code.

import pathlib
from typing import Dict, Optional, Tuple

import pandas as pd


def load_dataframe(
    basepath: str,
    mapping: Dict[Tuple[str, bool], str],
) -> pd.DataFrame:
    """
    Load all dataframes from CSV files in a given path

    :param basepath: The path onto which the mapping is rooted
    :param mapping: A mapping from (condition, hook) to filename
    :return: A dataframe with the loaded data
    """
    basepath = pathlib.Path(basepath)
    dfs = []

    for (condition, hook), filename in mapping.items():
        vec = pd.read_csv(basepath.joinpath(filename))["response_time"]
        data = {
            "time": vec,
            "condition": condition,
            "hook": hook,
        }

        print(
            f"read {filename} for ({condition}, {hook}) "
            f"[{len(vec)=}, {vec.mean()=}, {vec.median()=}]"
        )

        vec_df = pd.DataFrame.from_dict(data)
        vec_df.reset_index(inplace=True)
        vec_df.rename(columns={"index": "iteration"}, inplace=True)
        dfs.append(vec_df)

    df = pd.concat(dfs, ignore_index=True)
    return df


def filter_dataframe(
    df: pd.DataFrame,
    start: Optional[int] = None,
    stop: Optional[int] = None,
) -> pd.DataFrame:
    """
    For each condition, remove the warm-up period
    by specifying a certain start iteration number
    and possibly also remove the tail of the dataframe
    by specifying a stop iteration number.

    :param df: The dataframe to filter
    :param start: Minimum iteration number to keep, defaults to None
    :param stop: Maximum iteration number to keep, defaults to None
    :return: The filtered dataframe
    """

    start = start or df.iteration.min()
    stop = stop or df.iteration.max()

    print(f"\\newcommand{{\\TestTotalSampleSize}}{{{df.iteration.nunique():,d}}}")
    print(f"\\newcommand{{\\TestWarmUpPeriodSize}}{{{start:,d}}}")

    return df.query("iteration >= @start and iteration <= @stop")
