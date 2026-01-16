[![Python package](https://github.com/groupmm/libf0/actions/workflows/test_pip.yml/badge.svg)](https://github.com/groupmm/libf0/actions/workflows/test_pip.yml)


# libf0

This repository contains a Python package called libf0 which provides open-source implementations for four popular model-based F0-estimation approaches, YIN (Cheveigné & Kawahara, 2002), pYIN (Mauch & Dixon, 2014), an approach inspired by Melodia (Salamon & Gómez, 2012), and SWIPE (Camacho & Harris, 2008).

If you use the libf0 in your research, please consider the following references.

## References

Sebastian Rosenzweig, Simon Schwär, and Meinard Müller.
[libf0: A Python Library for Fundamental Frequency Estimation.](https://archives.ismir.net/ismir2022/latebreaking/000003.pdf)
In Late Breaking Demos of the International Society for Music Information Retrieval Conference (ISMIR), Bengaluru, India, 2022.

Alain de Cheveigné and Hideki Kawahara.
YIN, a fundamental frequency estimator for speech and music. Journal of the Acoustical Society of America (JASA), 111(4):1917–1930, 2002.

Matthias Mauch and Simon Dixon.
pYIN: A fundamental frequency estimator using probabilistic threshold distributions. In IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), pages 659–663, Florence, Italy, 2014.

Justin Salamon and Emilia Gómez.
Melody extraction from polyphonic music signals using pitch contour characteristics. IEEE Transactions on Audio, Speech, and Language Processing, 20(6):
1759–1770, 2012.

Arturo Camacho and John G. Harris.
A sawtooth waveform inspired pitch estimator for speech and music. The Journal of the Acoustical Society of America, 124(3):1638–1652, 2008.

Meinard Müller. Fundamentals of Music Processing – Using Python and Jupyter Notebooks. Springer Verlag, 2nd edition, 2021. ISBN 978-3-030-69807-2. doi: 10.1007/978-3-030-69808-9.


## Installing

To install libf0, please run

```
pip install libf0[dev,tests,docs]
```
with the following optional dependencies:
* `dev`: for development and running the demo notebook.
* `tests`: for running the unittests.
* `docs`: to build the API docs.

## Documentation
You can find the API documentation for libf0 here:

https://groupmm.github.io/libf0

## Contributing

We are happy for suggestions and contributions. We would be grateful for either directly contacting us via email (meinard.mueller@audiolabs-erlangen.de) or for creating an issue or pull request in our Github repository.

## Tests

We provide automated tests for each algorithm. To execute the test script, run

```
pytest tests
```

## Licence

The code for this toolbox is published under an MIT licence.

## Acknowledgements

This work was supported by the German Research Foundation (MU 2686/13-1, SCHE 280/20-1). We thank Edgar Suárez and Vojtěch Pešek for helping with the implementations. Furthermore, we thank Fatemeh Eftekhar and Maryam Pirmoradi for testing the toolbox. The International Audio Laboratories Erlangen are a joint institution of the Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU) and Fraunhofer Institute for Integrated Circuits IIS.
