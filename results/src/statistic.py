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

from typing import Dict

import numpy as np
import pandas as pd
from IPython.core.display import display
from scipy import stats


def test_dataframe(
    df: pd.DataFrame,
    condition_names: Dict[str, str],
):
    """
    Per condition, perform a t-test for difference in means
    """

    result = []
    sample_size = None
    for condition in condition_names:
        condition_df = df.query("condition == @condition")
        with_hook_df = condition_df.query("hook == True").time
        without_hook_df = condition_df.query("hook == False").time

        sample_size = sample_size or len(with_hook_df)
        assert sample_size == len(with_hook_df) == len(without_hook_df)

        s1, s2 = with_hook_df.std(), without_hook_df.std()
        m1, m2 = with_hook_df.mean(), without_hook_df.mean()
        sp = np.sqrt((s1**2 + s2**2) / 2)

        test = stats.ttest_ind(with_hook_df, without_hook_df)
        result.append(
            {
                "condition": condition,
                "p-value": test.pvalue,
                "statistic": test.statistic,
                "n": sample_size,
                "sp": sp,
            }
        )

        # sanity check with our own calculation
        t = (m1 - m2) / (sp * np.sqrt(2 / sample_size))
        assert np.isclose(test.statistic, t), f"{test.statistic=} != {t=}"

    df = pd.DataFrame.from_dict(result)
    df.set_index("condition", inplace=True)

    same_cluster_local_ratio = df.loc["same-cluster", "sp"] / df.loc["local", "sp"]

    # fmt: off
    macros = []
    macros.append(f"\\newcommand{{\\TestMeasurementPeriodSize}}{{{sample_size:,d}}}")
    macros.append(f"\\newcommand{{\\TestResultLocalPValue}}{{{df.loc['local', 'p-value']:.4f}}}")
    macros.append(f"\\newcommand{{\\TestResultLocalStdPool}}{{{df.loc['local', 'sp']:.2f}}}")
    macros.append(f"\\newcommand{{\\TestResultKindPValue}}{{{df.loc['kind', 'p-value']:.4f}}}")
    macros.append(f"\\newcommand{{\\TestResultKindStdPool}}{{{df.loc['kind', 'sp']:.2f}}}")
    macros.append(f"\\newcommand{{\\TestResultSamePodPValue}}{{{df.loc['same-pod', 'p-value']:.4f}}}")
    macros.append(f"\\newcommand{{\\TestResultSamePodStdPool}}{{{df.loc['same-pod', 'sp']:.2f}}}")
    macros.append(f"\\newcommand{{\\TestResultSameClusterPValue}}{{{df.loc['same-cluster', 'p-value']:.4f}}}")
    macros.append(f"\\newcommand{{\\TestResultSameClusterStdPool}}{{{df.loc['same-cluster', 'sp']:.2f}}}")
    macros.append(f"\\newcommand{{\\TestResultDockerSameClusterStdPoolRate}}{{{same_cluster_local_ratio:.1f}}}")
    # fmt: on

    print("\n".join(macros))
    display(df)
