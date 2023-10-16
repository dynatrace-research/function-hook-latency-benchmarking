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
