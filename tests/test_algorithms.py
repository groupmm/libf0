"""
| Description: Tests for functions of libf0
| Contributors: Sebastian Rosenzweig, Meinard Müller
| License: The MIT license, https://opensource.org/licenses/MIT
| This file is part of libf0.
"""

import numpy as np
from scipy.signal import chirp
from scipy.interpolate import interp1d
from scipy.special import beta, comb
from scipy.stats import triang
import libf0


# Generate test audio 1: Sinusoid
Fs = 22050  # Sampling rate
dur_sec = 5  # Duration of generated audio
T_audio = np.arange(0, dur_sec*Fs) / Fs  # Audio time axis
F_sine = 440  # Frequency of sinusoid
x1 = np.sin(2*np.pi*F_sine*T_audio)  # Sinusoidal signal

# Generate test audio 2: Sweep
F_start_chirp = 220.0
F_end_chirp = 640.0
x2 = chirp(T_audio, F_start_chirp, dur_sec, F_end_chirp, method='logarithmic')

F0_chirp = F_start_chirp * (F_end_chirp / F_start_chirp) ** (T_audio / dur_sec)  # Ground truth F0
chirp_func = interp1d(T_audio, F0_chirp, kind='cubic')  # interpolation function to make outputs comparable

# Further (global) parameters
F_min = 55.0  # Minimum frequency
F_max = 1760.0  # Maximum frequency
N = 2048  # Window size
H = 256  # Hop size
atol_sine = 10  # absolute test tolerance for sine signal in cents, tolerance for chirp varies depending on algorithm


def test_hz_to_cents():
    F_cents = libf0.hz_to_cents(440, F_ref=55.0)
    assert F_cents == 3600


def test_cents_to_hz():
    F_hz = libf0.cents_to_hz(3600, F_ref=55.0)
    assert F_hz == 440


def test_yin():
    threshold = 0.15
    f0_yin_x1, t_yin_x1, conf_yin_x1 = libf0.yin(x1, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, threshold=threshold)
    f0_yin_x2, t_yin_x2, conf_yin_x2 = libf0.yin(x2, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, threshold=threshold)

    assert np.allclose(libf0.hz_to_cents(f0_yin_x1), libf0.hz_to_cents(F_sine), rtol=0, atol=atol_sine)
    assert np.allclose(libf0.hz_to_cents(f0_yin_x2), libf0.hz_to_cents(chirp_func(t_yin_x2)), rtol=0, atol=50)


def test_pyin():
    R = 10
    thrs = np.arange(0.01, 1, 0.01)
    betas = [1, 18]
    abs_min_prob = 0.01
    voicing_prob = 0.5
    f0_pyin_x1, t_pyin_x1, conf_pyin_x1 = libf0.pyin(x1, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, R=R,
                                                     thresholds=thrs, beta_params=betas,
                                                     absolute_min_prob=abs_min_prob, voicing_prob=voicing_prob)
    f0_pyin_x2, t_pyin_x2, conf_pyin_x2 = libf0.pyin(x2, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, R=R,
                                                     thresholds=thrs, beta_params=betas,
                                                     absolute_min_prob=abs_min_prob, voicing_prob=voicing_prob)

    # exclude first frame, since it is always 0
    assert np.allclose(libf0.hz_to_cents(f0_pyin_x1[1:]), libf0.hz_to_cents(F_sine), rtol=0, atol=atol_sine)
    assert np.allclose(libf0.hz_to_cents(f0_pyin_x2[1:]), libf0.hz_to_cents(chirp_func(t_pyin_x2[1:])), rtol=0, atol=20)


def test_pyin_viterbi_impls_match():
    R = 10
    thrs = np.arange(0.01, 1, 0.01)
    betas = [1, 18]
    abs_min_prob = 0.01
    voicing_prob = 0.5

    f0_legacy, t_legacy, conf_legacy = libf0.pyin(
        x1, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, R=R,
        thresholds=thrs, beta_params=betas,
        absolute_min_prob=abs_min_prob, voicing_prob=voicing_prob,
        viterbi_impl="legacy")
    f0_fast, t_fast, conf_fast = libf0.pyin(
        x1, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, R=R,
        thresholds=thrs, beta_params=betas,
        absolute_min_prob=abs_min_prob, voicing_prob=voicing_prob,
        viterbi_impl="fast")

    assert np.array_equal(f0_legacy, f0_fast)
    assert np.array_equal(t_legacy, t_fast)
    assert np.array_equal(conf_legacy, conf_fast)


def test_pyin_viterbi_core_impls_match():
    R = 10
    thrs = np.arange(0.01, 1, 0.01)
    beta_params = [1, 18]
    absolute_min_prob = 0.01
    voicing_prob = 0.5
    x_pad = np.concatenate((np.zeros(N // 2), x2, np.zeros(N // 2)))

    thr_idxs = np.arange(len(thrs))
    beta_distr = comb(len(thrs), thr_idxs) * beta(
        thr_idxs + beta_params[0],
        len(thrs) - thr_idxs + beta_params[1],
    ) / beta(beta_params[0], beta_params[1])

    B = int(np.log2(F_max / F_min) * (1200 / R))
    F_axis = F_min * np.power(2, np.arange(B) * R / 1200)
    O, _, _, _ = libf0.yin_multi_thr(
        x_pad,
        Fs=Fs,
        N=N,
        H=H,
        F_min=F_min,
        F_max=F_max,
        thresholds=thrs,
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

    legacy = libf0.viterbi_log_likelihood(A, C.flatten(), O)
    source_idx_matrix, log_trans_matrix, counts_matrix = libf0.compute_transition_structure_from_matrix(A)
    source_idx_block, log_trans_block, counts_block = libf0.compute_transition_structure_pyin_block(B, triang_distr)

    assert np.array_equal(source_idx_matrix, source_idx_block)
    assert np.array_equal(log_trans_matrix, log_trans_block)
    assert np.array_equal(counts_matrix, counts_block)

    fast = libf0.viterbi_log_likelihood_fast(source_idx_block, log_trans_block, counts_block, C.flatten(), O)

    assert np.array_equal(legacy, fast)


def test_pyin_viterbi_impl_fail():
    try:
        libf0.pyin(x1, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max,
                   viterbi_impl="bogus")
    except ValueError:
        return
    raise AssertionError("Expected ValueError for invalid viterbi_impl")


def test_salience():
    R = 10
    n_harm = 10
    freq_smooth_len = 11
    alpha = 0.9
    gamma = 0.0
    tol = 5
    score_low = 0.01
    score_high = 1.0
    f0_sal_x1, t_sal_x1, conf_sal_x1 = libf0.salience(x1, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, R=R,
                                                      num_harm=n_harm, freq_smooth_len=freq_smooth_len, alpha=alpha,
                                                      gamma=gamma, constraint_region=None, tol=tol,
                                                      score_low=score_low, score_high=score_high)

    f0_sal_x2, t_sal_x2, conf_sal_x2 = libf0.salience(x2, Fs=Fs, N=N, H=H, F_min=F_min, F_max=F_max, R=R,
                                                      num_harm=n_harm, freq_smooth_len=freq_smooth_len, alpha=alpha,
                                                      gamma=gamma, constraint_region=None, tol=tol,
                                                      score_low=score_low, score_high=score_high)

    assert np.allclose(libf0.hz_to_cents(f0_sal_x1), libf0.hz_to_cents(F_sine), rtol=0, atol=atol_sine)
    assert np.allclose(libf0.hz_to_cents(f0_sal_x2), libf0.hz_to_cents(chirp_func(t_sal_x2)), rtol=0, atol=20)


def test_swipe():
    dlog2p = 1 / 96
    derbs = 0.1
    strength_threshold = 0
    f0_swipe_x1, t_swipe_x1, conf_swipe_x1 = libf0.swipe(x1, Fs=Fs, H=H, F_min=F_min, F_max=F_max, dlog2p=dlog2p,
                                                         derbs=derbs, strength_threshold=strength_threshold)
    f0_swipe_x2, t_swipe_x2, conf_swipe_x2 = libf0.swipe(x2, Fs=Fs, H=H, F_min=F_min, F_max=F_max, dlog2p=dlog2p,
                                                         derbs=derbs, strength_threshold=strength_threshold)

    # exclude first an last frame due to artifacts at signal edges
    assert np.allclose(libf0.hz_to_cents(f0_swipe_x1[1:-1]), libf0.hz_to_cents(F_sine), rtol=0, atol=atol_sine)
    assert np.allclose(libf0.hz_to_cents(f0_swipe_x2[1:-1]), libf0.hz_to_cents(chirp_func(t_swipe_x2[1:-1])), rtol=0,
                       atol=50)


def test_swipe_slim():
    R = 10
    strength_threshold = 0
    f0_swipes_x1, t_swipes_x1, conf_swipes_x1 = libf0.swipe_slim(x1, Fs=Fs, H=H, F_min=F_min, F_max=F_max, R=R,
                                                                 strength_threshold=strength_threshold)
    f0_swipes_x2, t_swipes_x2, conf_swipes_x2 = libf0.swipe_slim(x2, Fs=Fs, H=H, F_min=F_min, F_max=F_max, R=R,
                                                                 strength_threshold=strength_threshold)

    # exclude first an last frame due to artifacts at signal edges
    assert np.allclose(libf0.hz_to_cents(f0_swipes_x1[1:-1]), libf0.hz_to_cents(F_sine), rtol=0, atol=atol_sine)
    assert np.allclose(libf0.hz_to_cents(f0_swipes_x2[1:-1]), libf0.hz_to_cents(chirp_func(t_swipes_x2[1:-1])), rtol=0,
                       atol=20)
