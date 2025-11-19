wavesongs.util.plot
===================

.. py:module:: wavesongs.util.plot

.. autoapi-nested-parse::

   A collection of functions to dsplay songs and results.



Attributes
----------

.. autoapisummary::

   wavesongs.util.plot._COLORES


Classes
-------

.. autoapisummary::

   wavesongs.util.plot.Base
   wavesongs.util.plot.Matplotlib
   wavesongs.util.plot.Plotly


Functions
---------

.. autoapisummary::

   wavesongs.util.plot.get_roi
   wavesongs.util.plot.set_plotter


Module Contents
---------------

.. py:class:: Base(*args, **kwargs)

   .. py:method:: _save_name(obj)


   .. py:method:: _suptitle(obj)

      :param obj: _description_
      :type obj: Syllable | Song

      :returns:

                title : str
                    Title template



   .. py:method:: alpha_beta(*args, **kwargs)
      :abstractmethod:



   .. py:method:: colored_line(x, y, c, ax, **lc_kwargs)

      Plot a line with a color specified along the line by a third value.

      It does this by creating a collection of line segments. Each line segment is
      made up of two straight lines each connecting the current (x, y) point to the
      midpoints of the lines connecting the current point with its two neighbors.
      This creates a smooth line with no gaps between the line segments.

      :param x: The horizontal and vertical coordinates of the data points.
      :type x: array-like
      :param y: The horizontal and vertical coordinates of the data points.
      :type y: array-like
      :param c: The color values, which should be the same size as x and y.
      :type c: array-like
      :param ax: Axis object on which to plot the colored line.
      :type ax: Axes
      :param \*\*lc_kwargs: Any additional arguments to pass to matplotlib.collections.LineCollection
                            constructor. This should not include the array keyword argument because
                            that is set to the color argument. If provided, it will be overridden.

      :returns: The generated line collection representing the colored line.
      :rtype: matplotlib.collections.LineCollection



   .. py:method:: klicker(fig, ax, settings = _CLICKER_DATA_SETTINGS, legend_bbox = (1.125, 0.975))

      :param fig: Matplotlib Figure object
      :type fig: Figure
      :param ax: Matplotlib Axes objects
      :type ax: Axes
      :param label:
      :type label: list[str]
      :param colors:
      :type colors: list[str]
      :param markers:
      :type markers: list[str]

      :returns:

                klicker_data : clicker
                    Clicker object with position of the data measured

      .. rubric:: Example

      >>>



   .. py:method:: metrics(*args, **kwargs)
      :abstractmethod:



   .. py:method:: physical_variables(*args, **kwargs)
      :abstractmethod:



   .. py:method:: pickable_legend(handles_labels, lines, fig, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=5, title='Elements:')


   .. py:method:: spectrogram(*args, **kwargs)
      :abstractmethod:



   .. py:method:: spectrum_comparison(*args, **kwargs)
      :abstractmethod:



   .. py:attribute:: _CLICKER_DATA_SETTINGS


   .. py:attribute:: _CLICKER_TIME_SETTINGS


   .. py:attribute:: _COLORS


   .. py:attribute:: _LABELS


   .. py:attribute:: args
      :value: ()



   .. py:attribute:: id
      :type:  str


   .. py:attribute:: kwargs


   .. py:attribute:: labels_font


   .. py:attribute:: over_sample_mg
      :type:  int
      :value: 100



   .. py:attribute:: title_font
      :type:  dict


   .. py:attribute:: unit
      :type:  Literal['Hz', 'kHz']
      :value: 'kHz'



   .. py:attribute:: unit_scalar
      :value: 0.001



.. py:class:: Matplotlib(*args, **kwargs)

   Bases: :py:obj:`Base`


   .. py:method:: alpha_beta(obj, xlim = (-0.05, 0.2), ylim = (-0.2, 0.9), figsize = (10, 6), save = True, show = True)

      :param obj: Song or Syllable to be displayed
      :type obj: Syllabe|Song
      :param xlim: Time range
      :type xlim: tuple = (-0.05,.2)
      :param ylim: Frequency range
      :type ylim: tuple = (-0.2,0.9)
      :param figsize: Fogure size (width, height)
      :type figsize: tuple = (10,6)
      :param save: Enable save plot
      :type save: bool = True
      :param show: Enable display plot
      :type show: bool = True

      :returns: None

      .. rubric:: Example

      >>>



   .. py:method:: metrics(obj, obj_synth, figsize = (11, 8), ylim = (0, 10), save = True, grid = True, show = True)

      :param obj:
      :type obj: Syllable | Song
      :param obj_synth:
      :type obj_synth: Syllable | Song
      :param figsize: Size of the figure (width, height)
      :type figsize: tuple = (10,10)
      :param ylim: Frequnecy range
      :type ylim: tuple = ()
      :param save: Flag to save plot
      :type save: bool = True
      :param show: Flag to display plot
      :type show: bool = True

      :returns: None

      .. rubric:: Example

      >>>



   .. py:method:: physical_variables(obj, xlim = (0, 1000), figsize = (10, 6), save = False, show = True, grid = False, oversampling = 10)

      :param obj: Song or Syllable to be displayed
      :type obj: Syllabe|Song
      :param xlim: Time range
      :type xlim: tuple = (-0.05,.2)
      :param figsize: Fogure size (width, height)
      :type figsize: tuple = (10,6)
      :param save: Save plot
      :type save: bool = True
      :param show: Display plot
      :type show: bool = True

      :returns:

                files_names : list
                    List with the audios files names

      .. rubric:: Example

      >>>



   .. py:method:: segmentation(obj, harmonics = False, fundamental = False, alpha = 0.9, grid = False, colorbar = True, filters = True, figsize = (9, 7), label = 'syllables')

      _summary_

      :param obj: _description_
      :type obj: _type_
      :param harmonics: _description_. Defaults to False.
      :type harmonics: bool, optional
      :param fundamental: _description_. Defaults to False.
      :type fundamental: bool, optional
      :param alpha: _description_. Defaults to 0.9.
      :type alpha: float, optional
      :param grid: _description_. Defaults to False.
      :type grid: bool, optional
      :param colorbar: _description_. Defaults to True.
      :type colorbar: bool, optional
      :param filters: _description_. Defaults to True.
      :type filters: bool, optional
      :param figsize: _description_. Defaults to (9, 7).
      :type figsize: Tuple[float, float], optional
      :param label: _description_. Defaults to "syllables".
      :type label: Literal[&quot;segments&quot;, &quot;individual&quot;], optional

      :returns: _description_
      :rtype: Figure



   .. py:method:: spectrogram(obj, grid = True, mode = 'max', type = '2d', auxiliar = 'none', ff = False, click = 'none', waveforme = False, save = False, legend = False, figsize = (8, 6))

      



   .. py:attribute:: id
      :value: 'mtb'



.. py:class:: Plotly(height = 500, width = 700, percentage = 0, *args, **kwargs)

   Bases: :py:obj:`Base`


   .. py:method:: alpha_beta(obj, xlim = (-0.05, 0.2), ylim = (-0.2, 0.9), figsize = (8, 6), save = False, show = True)

      



   .. py:method:: metrics(obj, obj_synth, figsize = (9, 7), ylim = (0, 10), save = True, grid = True, show = True)


   .. py:method:: physical_variables(obj, xlim = (0, 1000), figsize = (1000, 600), save = False, show = True, grid = False, oversampling = 10)

      Plot physical model variables using Plotly.

      :param obj: Song or Syllable to be displayed
      :type obj: Syllabe|Song
      :param xlim: Time range
      :type xlim: tuple = (-0.05,.2)
      :param figsize: Figure size (width, height) in pixels
      :type figsize: tuple = (1000,600)
      :param save: Save plot as HTML
      :type save: bool = True
      :param show: Display plot
      :type show: bool = True

      :returns: None



   .. py:method:: segmentation(obj, harmonics = False, fundamental = False, alpha = 0.9, grid = False, colorbar = True, filters = True, figsize = (9, 7), label = 'syllables')

      Create a segmentation plot for the given object.

      :param obj: The object to plot.
      :param harmonics: Whether to include harmonics. Defaults to False.
      :type harmonics: bool, optional
      :param fundamental: Whether to include fundamental frequency. Defaults to False.
      :type fundamental: bool, optional
      :param alpha: The transparency level for the plots. Defaults to 0.9.
      :type alpha: float, optional
      :param grid: Whether to show grid lines. Defaults to False.
      :type grid: bool, optional
      :param colorbar: Whether to show colorbar. Defaults to True.
      :type colorbar: bool, optional
      :param filters: Whether to include filters. Defaults to True.
      :type filters: bool, optional
      :param figsize: The size of the figure. Defaults to (9, 7).
      :type figsize: Tuple[float, float], optional
      :param label: The label type. Defaults to "syllables".
      :type label: Literal["syllables", "vocalizations"], optional

      :returns: The created figure.
      :rtype: Figure



   .. py:method:: spectrogram(obj, type = '2d', auxiliar = 'none', mode = 'mean', waveforme = False, grid = True, ff = False, click = 'none', legend = False)

      Plot the spectrogram of a Syllable or Song object using Plotly.



   .. py:attribute:: height
      :value: 500



   .. py:attribute:: id
      :value: 'plotly'



   .. py:attribute:: percentage
      :value: 0



   .. py:attribute:: width
      :value: 700



.. py:function:: get_roi(klicker)

   :param klicker: Clicker object with position of the data measured
   :type klicker: clicker

   :returns:

             times : list[tuple[float], tuple[float]]
                 Times select from the spectrogram

   .. rubric:: Example

   >>>


.. py:function:: set_plotter(visualaizer = 'matplotlib', *args, **kwargs)

   Factory function to create a plotter instance based on the selected library.


.. py:data:: _COLORES

