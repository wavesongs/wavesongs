---
myst:
  html_meta:
    "description lang=en": |
      Top-level documentation for wavesongs, with links to the rest
      of the site..
html_theme.sidebar_secondary.remove: false
---

# Wavesongs

**WaveSongs**  is a Python package designed to generate synthetic songs (currently focused on birdsongs) from audio recordings.

```{eval-rst}
The package utilizes the `motor gestures model for birdsong <http://www.lsd.df.uba.ar/papers/simplemotorgestures.pdf>`_ developed by `Gabo Mindlin <https://scholar.google.com.ar/citations?user=gMzZPngAAAAJ&hl=en>`_ to generate synthetic birdsongs through numerical optimization :cite:p:`b-birdsongs_book,a-Amador2013`. By leveraging **fundamental frequency (FF)** and **spectral content index (SCI)** as key parameters. The package solves a minimization problem using `SciPy <https://docs.scipy.org/doc/scipy/tutorial/optimize.html>`_ :cite:p:`s-2020SciPy` and performs audio analysis with `librosa <https://librosa.org/>`_  :cite:p:`s-McFee2015librosa` and `scikit-maad <https://scikit-maad.github.io/>`_ :cite:p:`s-maad`.  This combination of tools enables the precise and realistic synthesis of birdsongs, achieving relative errors in fundamental frequency (FF) of less than 1%. [#f1]_
```

## ⚒️ Installation

There are two ways to install wavesongs: a single line code installation via pypi, or a manual installation to get the latest  developer version. Check the :ref:`️installation` guide for more details.  

Now, let’s dive into the package! Check out the :ref:`getting_started` guide to learn how to analyze recordings and create synthetic syllables. You can download recording samples from the :ref:`download_samples` guide.




## 🌱 Contribute

We welcome contributions! See our roadmap:


To report issues or suggest features, open a [GitHub Issue](https://github.com/wavesongs/wavesongs/issues). 

Do you need some other functionality? Let us know!

## 🔐 License

**WaveSongs** is licensed under the [GNU General Public License v3.0](https://github.com/wavesongs/wavesongs/blob/main/LICENSE).


## User Guide

Information about using, configuration, and customizing this theme.

```{toctree}
:maxdepth: 2

user_guide/index
```

## API

The content of the exposed `pydata_sphinx_theme` API.

```{toctree}
:maxdepth: 1

API <api/index>
```


## Examples 1

```{toctree}
:maxdepth: 2
:hidden:

auto_examples/index
```

## 📒 Citation

If this work contributes to your research, please cite:

```{code-block} bibtex
@software{san_wavesongs_2025,
      author = {Aguilera Novoa, Sebastian},
      title = {WaveSongs: Computational Birdsong Synthesis},
      year = {2025},
      publisher = {GitHub},
      journal = {GitHub Repository},
      url = {https://github.com/wavesongs/wavesongs}
}
```

## 📚 References

```{eval-rst}
.. rubric:: Articles

.. bibliography:: references/articles.bib
   :keyprefix: a-
   :labelprefix: A


.. rubric:: Books

.. bibliography:: references/references.bib
   :keyprefix: b-
   :labelprefix: B

.. rubric:: Software
   
.. bibliography:: references/software.bib
   :all:
   :keyprefix: s-
   :labelprefix: S

.. rubric:: Footnotes

.. [#f1] The model performance depends on the syllable quaility and type. Complex syllables may have higher errors. The best performance is obtained in simple syllables well defined without noise and not strong harmonics.

```
