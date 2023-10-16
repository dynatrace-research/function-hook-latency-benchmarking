import numpy as np
import pandas as pd

AVAILABLE_CONDITIONS = ["local", "kind", "same-pod", "same-cluster"]


def generate_vector(condition: str, hook: bool, ncycles: int) -> np.ndarray:
    """
    Generates mocked latency values with warm-up, for a given setup

    :param condition: One of the available condition identifiers
    :param hook: Whether the hook is enabled or not
    :param ncycles: Number of cycles to generate
    :return: A vector of latency values
    """

    assert condition in AVAILABLE_CONDITIONS
    mus = {"local": 3, "kind": 3.5, "same-pod": 1.5, "same-cluster": 2.2}
    stds = {"local": 0.1, "kind": 0.2, "same-pod": 0.4, "same-cluster": 0.75}

    rng = np.random.Generator(np.random.PCG64(1337))
    mu, std = mus[condition] + (0.5 if hook else 0), stds[condition]
    x = rng.normal(mu, std, ncycles)

    # add exponential decay to the beginning of the vector
    warmup_strength, warmup_ratio = 0.7, 0.1
    warmup = np.linspace(0, 1, int(ncycles * warmup_ratio))
    warmup = 1.0 + np.exp(-5 * warmup) * (warmup_strength / stds[condition])
    x[: len(warmup)] *= warmup

    return x


def generate_dataframe(ncycles: int = 1_000) -> pd.DataFrame:
    """
    Generate a fake dataframe in wide format

    :param ncycles: Number of cycles per condition, defaults to 1_000
    :return: A dataframe with the generated data
    """

    dfs = []

    for condition in AVAILABLE_CONDITIONS:
        for hook in [True, False]:
            data = {
                "time": generate_vector(condition, hook, ncycles=ncycles),
                "condition": condition,
                "hook": hook,
            }

            vec_df = pd.DataFrame.from_dict(data)
            vec_df.reset_index(inplace=True)
            vec_df.rename(columns={"index": "iteration"}, inplace=True)
            dfs.append(vec_df)

    df = pd.concat(dfs, ignore_index=True)
    return df
