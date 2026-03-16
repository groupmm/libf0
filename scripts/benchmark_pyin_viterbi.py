#!/usr/bin/env python
import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.special import beta, comb
from scipy.stats import triang

import libf0


DEFAULT_AUDIO = Path("data/DCS_LI_QuartetB_Take03_S1_LRX_excerpt.wav")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", type=Path, default=DEFAULT_AUDIO)
    parser.add_argument("--repeat-audio", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--iters", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_audio(path: Path, repeat_audio: int) -> tuple[np.ndarray, int]:
    sample_rate, audio = wavfile.read(path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if np.issubdtype(audio.dtype, np.integer):
        audio = audio.astype(np.float32) / max(np.iinfo(audio.dtype).max, 1)
    else:
        audio = audio.astype(np.float32, copy=False)
    if repeat_audio > 1:
        audio = np.tile(audio, repeat_audio)
    return audio, int(sample_rate)


def time_call(fn, *, warmup: int, iters: int) -> float:
    for _ in range(warmup):
        fn()
    durations_ms = []
    for _ in range(iters):
        start = time.perf_counter()
        fn()
        durations_ms.append((time.perf_counter() - start) * 1000.0)
    durations_ms.sort()
    return durations_ms[len(durations_ms) // 2]


def prepare_pyin_state(x, Fs, N=2048, H=256, F_min=55.0, F_max=1760.0, R=10,
                       thresholds=np.arange(0.01, 1, 0.01), beta_params=(1, 18),
                       absolute_min_prob=0.01, voicing_prob=0.5):
    x_pad = np.concatenate((np.zeros(N // 2), x, np.zeros(N // 2)))
    thr_idxs = np.arange(len(thresholds))
    beta_distr = comb(len(thresholds), thr_idxs) * beta(
        thr_idxs + beta_params[0],
        len(thresholds) - thr_idxs + beta_params[1],
    ) / beta(beta_params[0], beta_params[1])

    B = int(np.log2(F_max / F_min) * (1200 / R))
    F_axis = F_min * np.power(2, np.arange(B) * R / 1200)
    O, rms, p_orig, val_orig = libf0.yin_multi_thr(
        x_pad,
        Fs=Fs,
        N=N,
        H=H,
        F_min=F_min,
        F_max=F_max,
        thresholds=thresholds,
        beta_distr=beta_distr,
        absolute_min_prob=absolute_min_prob,
        F_axis=F_axis,
        voicing_prob=voicing_prob,
    )
    max_step_cents = 50
    max_step = int(max_step_cents / R)
    triang_distr = triang.pdf(
        np.arange(-max_step, max_step + 1),
        0.5,
        scale=2 * max_step,
        loc=-max_step,
    )
    A = libf0.compute_transition_matrix(B, triang_distr)
    C = np.ones((2 * B, 1)) / (2 * B)
    source_idx, log_trans, counts = libf0.compute_transition_structure_from_matrix(A)
    return {
        "O": O,
        "A": A,
        "C": C,
        "source_idx": source_idx,
        "log_trans": log_trans,
        "counts": counts,
        "frames": int(O.shape[1]),
    }


def benchmark(args):
    audio, sample_rate = load_audio(args.audio, args.repeat_audio)
    state = prepare_pyin_state(audio, sample_rate)

    legacy_path = libf0.viterbi_log_likelihood(state["A"], state["C"].flatten(), state["O"])
    fast_path = libf0.viterbi_log_likelihood_fast(
        state["source_idx"],
        state["log_trans"],
        state["counts"],
        state["C"].flatten(),
        state["O"],
    )

    f0_legacy, t_legacy, conf_legacy = libf0.pyin(audio, Fs=sample_rate, viterbi_impl="legacy")
    f0_fast, t_fast, conf_fast = libf0.pyin(audio, Fs=sample_rate, viterbi_impl="fast")

    return {
        "audio": str(args.audio),
        "repeat_audio": args.repeat_audio,
        "frames": state["frames"],
        "decoder_path_parity_ok": bool(np.array_equal(legacy_path, fast_path)),
        "pyin_f0_parity_ok": bool(np.array_equal(f0_legacy, f0_fast)),
        "pyin_time_parity_ok": bool(np.array_equal(t_legacy, t_fast)),
        "pyin_conf_parity_ok": bool(np.array_equal(conf_legacy, conf_fast)),
        "viterbi_log_likelihood_legacy_ms": time_call(
            lambda: libf0.viterbi_log_likelihood(state["A"], state["C"].flatten(), state["O"]),
            warmup=args.warmup,
            iters=args.iters,
        ),
        "viterbi_log_likelihood_fast_ms": time_call(
            lambda: libf0.viterbi_log_likelihood_fast(
                state["source_idx"],
                state["log_trans"],
                state["counts"],
                state["C"].flatten(),
                state["O"],
            ),
            warmup=args.warmup,
            iters=args.iters,
        ),
        "pyin_legacy_ms": time_call(
            lambda: libf0.pyin(audio, Fs=sample_rate, viterbi_impl="legacy"),
            warmup=args.warmup,
            iters=args.iters,
        ),
        "pyin_fast_ms": time_call(
            lambda: libf0.pyin(audio, Fs=sample_rate, viterbi_impl="fast"),
            warmup=args.warmup,
            iters=args.iters,
        ),
    }


def render_markdown(result):
    core_speedup = result["viterbi_log_likelihood_legacy_ms"] / result["viterbi_log_likelihood_fast_ms"]
    pyin_speedup = result["pyin_legacy_ms"] / result["pyin_fast_ms"]
    lines = [
        "## libf0 pYIN Viterbi Benchmark",
        "",
        f"**Audio:** `{result['audio']}`",
        f"**Repeated:** `{result['repeat_audio']}`",
        f"**Frames:** `{result['frames']}`",
        "",
        "---",
        "",
        "## Decoder Core",
        "",
        "| Impl | Time |",
        "|:--|--:|",
        f"| `legacy` | **{result['viterbi_log_likelihood_legacy_ms']:.3f} ms** |",
        f"| `fast` | **{result['viterbi_log_likelihood_fast_ms']:.3f} ms** |",
        "",
        f"> ✅ **Core speedup:** `{core_speedup:.2f}x`",
        "",
        "---",
        "",
        "## Full pYIN",
        "",
        "| Impl | Time |",
        "|:--|--:|",
        f"| `legacy` | **{result['pyin_legacy_ms']:.3f} ms** |",
        f"| `fast` | **{result['pyin_fast_ms']:.3f} ms** |",
        "",
        f"> ✅ **End-to-end speedup:** `{pyin_speedup:.2f}x`",
        "",
        "## Parity",
        "",
        f"- decoder path parity: `{'ok' if result['decoder_path_parity_ok'] else 'mismatch'}`",
        f"- f0 parity: `{'ok' if result['pyin_f0_parity_ok'] else 'mismatch'}`",
        f"- time-axis parity: `{'ok' if result['pyin_time_parity_ok'] else 'mismatch'}`",
        f"- confidence parity: `{'ok' if result['pyin_conf_parity_ok'] else 'mismatch'}`",
    ]
    return "\n".join(lines)


def main():
    args = parse_args()
    result = benchmark(args)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(render_markdown(result))


if __name__ == "__main__":
    main()
