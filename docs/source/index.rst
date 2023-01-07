.. libf0 documentation master file, created by
   sphinx-quickstart on Thu May 27 14:48:45 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

libf0
==================================
``libf0`` is a Python toolbox for fundamental frequency (F0) estimation in music recordings.

If you use this toolbox, please cite:

.. [#] Sebastian Rosenzweig, Simon Schwär, and Meinard Müller. libf0: A Python Library for Fundamental Frequency Estimation. In Late Breaking Demos of the International Society for Music Information Retrieval Conference (ISMIR), Bengaluru, India, 2022.


To reference the original algorithms implemented in this toolbox, please cite:

.. [#] Alain De Cheveigné and Hideki Kawahara: YIN, a fundamental frequency estimator for speech and music, The Journal of the Acoustical Society of America 111.4 (2002): 1917-1930.
.. [#] Matthias Mauch and Simon Dixon: PYIN: A fundamental frequency estimator using probabilistic threshold distributions, IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (2014): 659-663.
.. [#] Justin Salamon and Emilia Gómez: Melody Extraction From Polyphonic Music Signals Using Pitch Contour Characteristics, IEEE Transactions on Audio, Speech, and Language Processing, vol. 20, no. 6, pp. 1759–1770, 2012.
.. [#] Arturo Camacho and John G. Harris: A sawtooth waveform inspired pitch estimator for speech and music. The Journal of the Acoustical Society of America, vol. 124, no. 3, pp. 1638–1652, 2008
.. [#] Meinard Müller. Fundamentals of Music Processing – Using Python and Jupyter Notebooks. Springer Verlag, 2nd edition, 2021. ISBN 978-3-030-69807-2. doi: 10.1007/978-3-030-69808-9.


.. toctree::
    :hidden:

    getting_started



.. toctree::
    :caption: API Documentation
    :maxdepth: 1
    :hidden:

    index_yin
    index_pyin
    index_salience
    index_swipe
    index_swipe_slim
    index_utils
