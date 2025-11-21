#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A collection of functions to dsplay songs and results.
"""
import warnings

import numpy as np
import pandas as pd

from abc import abstractmethod

# matplotlib
import matplotlib.pyplot as plt

from matplotlib import cm, colors
from matplotlib.collections import LineCollection
from matplotlib.colorbar import ColorbarBase
import matplotlib.colors as mcolors

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.patches import Patch
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import (
    FuncFormatter,
    LinearLocator,
    NullFormatter
)
import ipywidgets as widgets

from mpl_point_clicker import clicker
from mpl_pan_zoom import PanManager, MouseButton

# plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# display
from IPython.display import display
from librosa.display import specshow as Specshow

# typing
from typing import Literal, Any
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from plotly.graph_objs import Figure as FigurePlotly

# ws objects
from wavesongs.object import Synthetic, Syllable, Song


# %%
def get_roi(klicker: clicker) -> list[tuple[float, float]]:
    """
    
    Parameters
    ----------
        klicker : clicker
            Clicker object with position of the data measured
    
    Return
    ------
        times : list[tuple[float], tuple[float]]
            Times select from the spectrogram
    Example
    -------
        >>>
    """
    tinis = klicker.get_positions()[r"$t_{ini}$"]
    tends = klicker.get_positions()[r"$t_{end}$"]
    
    if tinis.shape != tends.shape:
        print("Number of points selected are not even. Remember you have \
              to select the same number of initial times as end times")
        times = list(zip(tinis.flatten(), tends.flatten()))
    else:
        no_points = tinis.shape[0]
        if no_points > 1:
            times = [(tinis[i, 0], tends[i, 0]) for i in range(no_points)]
        else:
            times = [(tinis[0, 0], tends[0, 0])]
    return times

# %%
# def get_measures(klicker, obj, save=False, labels=_LABELS, csv_name="measures.csv"):
#     f_max_min = _shift_time(klicker.get_positions()[labels[0]], obj)
#     theme_ini = _shift_time(klicker.get_positions()[labels[1]], obj)
#     theme_end = _shift_time(klicker.get_positions()[labels[2]], obj)
#     trill_ini = _shift_time(klicker.get_positions()[labels[3]], obj)
#     trill_end = _shift_time(klicker.get_positions()[labels[4]], obj)

#     if f_max_min[0][1] > f_max_min[1][1]:
#       fmax = f_max_min[0][1]
#       fmin = f_max_min[1][1]
#     else:
#       fmax = f_max_min[1][1]
#       fmin = f_max_min[0][1]

#     # automatic syllable type computing
#     # type_themes = []
#     # for s in theme_syllables:
#     #     if (s[1][1]-s[0][1])*-1>0:
#     #     els "up":
#     # -------------------------------- theme --------------------------------
#     theme_syllables = [[theme_ini[i], theme_end[i]] for i in range(len(theme_ini))]
#     no_themes = len(theme_syllables)
#     theme_sep_times = [theme_syllables[i+1][0][0]-theme_syllables[i][1][0]
#                         for i in range(no_themes-1)]
#     theme_sep_freqs = [theme_syllables[i+1][0][1]-theme_syllables[i][1][1]
#                         for i in range(no_themes-1)]
#     theme_sep_time_means = np.mean(theme_sep_times)
#     theme_sep_freq_means = np.mean(theme_sep_freqs)

#     theme_slopes = [(s[1][1]-s[0][1])/(s[1][0]-s[0][0]) for s in theme_syllables]
#     theme_types = ["down" if s<0 else "up" for s in theme_slopes]
#     theme_len_times = [s[1][0]-s[0][0] for s in theme_syllables]
#     theme_len_freqs = [np.abs(s[1][1]-s[0][1]) for s in theme_syllables]

#     theme_avg_len_times = np.mean(theme_len_times)
#     theme_band_widths = np.mean(theme_len_freqs)

#     theme_sep_song_time_avg = theme_sep_time_means + theme_avg_len_times
#     theme_rates = 1 / theme_sep_song_time_avg

#     # -------------------------------- trill --------------------------------
#     trill_syllables = [[trill_ini[i], trill_end[i]]for i in range(len(trill_ini))]
#     no_trills = len(trill_syllables)
#     trill_sep_times = [trill_syllables[i+1][0][0]-trill_syllables[i][1][0]
#                         for i in range(no_trills-1)]
#     trill_sep_freqs = [trill_syllables[i+1][0][1]-trill_syllables[i][1][1]
#                         for i in range(no_trills-1)]
#     trill_sep_time_means = np.mean(trill_sep_times)
#     trill_sep_freq_means = np.mean(trill_sep_freqs)

#     trill_slopes = [(s[1][1]-s[0][1])/(s[1][0]-s[0][0]) for s in trill_syllables]
#     trill_types = ["down" if s<0 else "up" for s in trill_slopes]
#     trill_len_times = [s[1][0]-s[0][0] for s in trill_syllables] # rate
#     trill_len_freqs = [np.abs(s[1][1]-s[0][1]) for s in trill_syllables] # Band Width

#     trill_avg_len_times = np.mean(trill_len_times)
#     trill_band_widths = np.mean(trill_len_freqs) # trills_avg_len_freqs 

#     theme_trill_time_sep = trill_syllables[0][0][0]-trill_syllables[-1][1][0]

#     trill_sep_song_time_avg = trill_sep_time_means + trill_avg_len_times
#     trill_rates = 1 / trill_sep_song_time_avg

#     data_df = pd.DataFrame(
#       {
#         "fmax": fmax,
#         "fmin": fmin,
#         "theme_trill_time_sep": theme_trill_time_sep
#       } | {
#         "trill_bw": trill_band_widths,
#         "trill_rates": trill_rates,
#         "trill_len_times": str(trill_len_times),
#         "trill_len_freqs": str(trill_len_freqs),
#         "trill_slopes": str(trill_slopes),
#         "trill_tinis": str([t[0] for t in trill_ini]),
#         "trill_tends": str([t[1] for t in trill_ini]),
#         "trill_types": str(trill_types),
#         "trills_avg_len_time": trill_avg_len_times,
#         "trills_band_width": trill_band_widths,
#         "trill_sep_freq_means": trill_sep_freq_means,
#         "trill_sep_time_means": trill_sep_time_means,
#         "trill_sep_freqs": str(trill_sep_freqs),
#         "trill_sep_times": str(trill_sep_times),
#         "no_trills": no_trills
#       } | {
#       "theme_bw": theme_band_widths,
#         "theme_rates": theme_rates,
#         "theme_len_times": str(theme_len_times),
#         "theme_len_freqs": str(theme_len_freqs),
#         "theme_slopes": str(theme_slopes),
#         "theme_tinis": str([t[0] for t in theme_ini]),
#         "theme_tends": str([t[1] for t in theme_ini]),
#         "theme_types": str(theme_types),
#         "themes_avg_len_time": theme_avg_len_times,
#         "themes_band_width": theme_band_widths,
#         "theme_sep_freq_means": theme_sep_freq_means,
#         "theme_sep_time_means": theme_sep_time_means,
#         "theme_sep_freqs": str(theme_sep_freqs),
#         "theme_sep_times": str(theme_sep_times),
#         "no_themes": no_themes
#       }
#     , index=[0])

#     if save:
#         data_df.to_csv(csv_name, index=False)
        
#     return data_df





# --------------------------
_COLORES = {
    "Argentina": ["Blues", "lightblue", "blue"],
    "Bolivia": ["Purples", "plum", "purple"],
    "Brazil": ["Greys", "lightgray", "black"],
    "Chile": ["Oranges", "bisque", "chocolate"],
    "Colombia": ["Reds", "lightsalmon", "red"],
    "Costa Rica": ["cool", "paleturquoise", "teal"],
    "Ecuador": ["GnBu", "lightsteelblue", "steelblue"],
    "Peru": ["Greens", "darkseagreen", "darkgreen"],
    "Uruguay": ["copper", "peachpuff", "orange"],
    "Venezuela": ["RdPu", "lightpink", "mediumvioletred"],
}


class Base:
    # _CMAP = "viridis"
    unit: Literal["Hz", "kHz"] = "kHz"
  
    title_font: dict = {
        "size": 18,
        "weight": "bold",
        "familt": "",
    }

    labels_font ={
        "size": 14,
        "weight": "normal",
        "family": "",
    }

    id: str
    
    over_sample_mg: int = 100

    if unit == "kHz": unit_scalar = 1e-3
    else: unit_scalar = 1

    _COLORS = {
        "envelope": "#091c57",
        "waveforme": "#5c8eb4",
        "fundamental": "#000000",
        "freq_aux": "#ef503a",
        "time_aux": "#00ce96",
        "motor_gesture": "Blues",
        "spectrum": "Viridis",
        "spectrum1": "viridis",

        "sci_error": "purple",
        "ff_error": "black",
        "real_ff": "blue",
        "synth_ff": "green",
        "sci_real": "blue",
        "sci_synth": "green",
        "df": "orange",
        "skl": "purple",
        "correlation": "red",

        "threshold_1": "#BEA018",
        "threshold_2": "#7318BE",

        "syllable_labels": "nipy_spectral", 
    }

    _LABELS = {
        "ff" : "FF,\n" + r" $\overline{FF}$=" ,
        "sci" : "SCI,\n " + r"$\overline{SCI}$=",
        "lskl" : r"SKL, $\overline{SKL}$=",
        "lr" : r"$SCI_{real}$, $\overline{SCI}$=",
        "ls" : r"$SCI_{synth}$, $\overline{SCI}$=",
        "lh" : r"DF, $\overline{DF}$=",
        "lc" : r"cor, $\overline{corr}$=",
        "ff_real": "real FF",
        "ff_synth": "synth FF",

        "power": "Power (dB)"
    }
    

    _CLICKER_TIME_SETTINGS = {
        "labels": [
            r"$t_{ini}$",
            r"$t_{end}$"
        ],
        "colors": [
            "lightgray", "orange"
        ],
        "markers": [
            "v", "o"
        ]
    }

    _CLICKER_DATA_SETTINGS = {
    "labels": [
            r"$f_{max/min}$",
            r"$theme_{ini}$",
            r"$theme_{end}$",
            r"$trill_{ini}$",
            r"$trill_{end}$"
        ],
    "colors": [
        "cyan", "olivedrab", "darkgreen", "steelblue", "royalblue"
        ],
    "markers": [
        "p", "*", "*", "o", "o"
    ]
    }
    
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Base class for all plots.
        """
        self.args = args
        self.kwargs = kwargs

        # self.model = Model() if model is None else model
        
    @abstractmethod
    def alpha_beta(self, *args, **kwargs):
        pass

    @abstractmethod
    def physical_variables(self, *args, **kwargs):
        pass

    @abstractmethod
    def spectrogram(self, *args, **kwargs):
        pass

    @abstractmethod
    def metrics(self, *args, **kwargs):
        pass

    @abstractmethod
    def spectrum_comparison(self, *args, **kwargs):
        pass


    def _suptitle(self, obj) -> str:
        """

        Parameters
        ----------
            obj : Syllable | Song
                _description_

        Returns
        -------
            title : str
                Title template
        """    
        format = obj.file_name[-3:]
        file_name = obj.file_name[:-4].replace("synth_","")
        title = f"{file_name}-{obj.no_syllable}-{obj.type}.{format}" \
                    if obj.type!="" else f"{file_name}-{obj.no_syllable}.{format}"
        return title.replace(" ","")
    #%%
    def _save_name(self, obj) -> str:
        file_name = obj.file_name[:-4]
        img_text = f"{file_name}-{obj.no_syllable}-{obj.type}" \
                    if obj.type!="" else f"{file_name}-{obj.no_syllable}"
        return img_text.replace(" ","")

    def klicker(
        self,
        fig: Figure, 
        ax: Axes,
        settings: dict = _CLICKER_DATA_SETTINGS,
        legend_bbox: tuple[float, float] = (1.125, 0.975),
    ) -> clicker:
        """
        
        Parameters
        ----------
            fig : Figure
                Matplotlib Figure object
            ax : Axes
                Matplotlib Axes objects
            label : list[str]

            colors : list[str]

            markers : list[str]

        
        Return
        ------
            klicker_data : clicker
                Clicker object with position of the data measured
        
        Example
        -------
            >>>
        """
        pm = PanManager(fig, button=MouseButton.MIDDLE)
        klicker_data = clicker(
                        ax,
                        classes=settings["labels"],
                        # init_class=list(range(len(labels))), 
                        # labels=labels,
                        markers=settings["markers"],
                        colors=settings["colors"],
                        legend_bbox=legend_bbox
                        )

        # klicker_data._pm = pm
        setattr(klicker_data, "_pm", pm)
        return klicker_data
    
    def colored_line(self, x, y, c, ax, **lc_kwargs):
        """
        Plot a line with a color specified along the line by a third value.

        It does this by creating a collection of line segments. Each line segment is
        made up of two straight lines each connecting the current (x, y) point to the
        midpoints of the lines connecting the current point with its two neighbors.
        This creates a smooth line with no gaps between the line segments.

        Parameters
        ----------
        x, y : array-like
            The horizontal and vertical coordinates of the data points.
        c : array-like
            The color values, which should be the same size as x and y.
        ax : Axes
            Axis object on which to plot the colored line.
        **lc_kwargs
            Any additional arguments to pass to matplotlib.collections.LineCollection
            constructor. This should not include the array keyword argument because
            that is set to the color argument. If provided, it will be overridden.

        Returns
        -------
        matplotlib.collections.LineCollection
            The generated line collection representing the colored line.
        """
        if "array" in lc_kwargs:
            warnings.warn('The provided "array" keyword argument will be overridden')

        # Default the capstyle to butt so that the line segments smoothly line up
        default_kwargs = {"capstyle": "butt", "zorder": 2}
        default_kwargs.update(lc_kwargs)

        # Compute the midpoints of the line segments. Include the first and last points
        # twice so we don't need any special syntax later to handle them.
        x = np.asarray(x)
        y = np.asarray(y)
        x_midpts = np.hstack((x[0], 0.5 * (x[1:] + x[:-1]), x[-1]))
        y_midpts = np.hstack((y[0], 0.5 * (y[1:] + y[:-1]), y[-1]))

        # Determine the start, middle, and end coordinate pair of each line segment.
        # Use the reshape to add an extra dimension so each pair of points is in its
        # own list. Then concatenate them to create:
        # [
        #   [(x1_start, y1_start), (x1_mid, y1_mid), (x1_end, y1_end)],
        #   [(x2_start, y2_start), (x2_mid, y2_mid), (x2_end, y2_end)],
        #   ...
        # ]
        coord_start = np.column_stack((x_midpts[:-1], y_midpts[:-1]))[:, np.newaxis, :]
        coord_mid = np.column_stack((x, y))[:, np.newaxis, :]
        coord_end = np.column_stack((x_midpts[1:], y_midpts[1:]))[:, np.newaxis, :]
        segments = np.concatenate((coord_start, coord_mid, coord_end), axis=1)

        lc = LineCollection(segments.tolist(), **default_kwargs)
        lc.set_array(c)  # set the colors of each segment

        return ax.add_collection(lc)

    def pickable_legend(self, handles_labels, lines, fig,
        loc='lower center',
        bbox_to_anchor=(0.5, 0.),
        ncol=5, title="Elements:",
    ):
        handles = []
        labels = []
        for h, l in handles_labels:
            handles.extend(h)
            labels.extend(l)

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        unique_labels = []
        for h, l in zip(handles, labels):
            if l not in seen and l != "":
                unique.append(h)
                unique_labels.append(l)
                seen.add(l)

        

        map_legend_to_ax = {}  # Will map legend lines to original lines.
        pickradius = 10  # Points (Pt). How close the click needs to be to trigger an event.

        leg = fig.legend(
            unique,
            unique_labels,
            loc=loc,
            bbox_to_anchor=bbox_to_anchor,
            ncol=ncol,
            frameon=True,
            title=title,
            fontsize=10,
            title_fontproperties={'weight': 'bold', "size": 12,},
            fancybox=True, shadow=True,
        )

        # axs[2,0].add_artist(leg)
        for legend_line, ax_line in zip(leg.get_lines(), lines):
            legend_line.set_picker(pickradius)  # Enable picking on the legend line.
            map_legend_to_ax[legend_line] = ax_line


        def on_pick(event):
            # On the pick event, find the original line corresponding to the legend
            # proxy line, and toggle its visibility.
            legend_line = event.artist

            # Do nothing if the source of the event is not a legend line.
            if legend_line not in map_legend_to_ax:
                return

            ax_line = map_legend_to_ax[legend_line]
            visible = not ax_line.get_visible()
            ax_line.set_visible(visible)
            legend_line.set_alpha(1.0 if visible else 0.2)
            fig.canvas.draw()


        fig.canvas.mpl_connect('pick_event', on_pick)
        # Works even if the legend is draggable. This is independent from picking legend lines.
        leg.set_draggable(False)

        return leg
#%%
def set_plotter(
        visualaizer: Literal["matplotlib", "plotly"] = "matplotlib",
        *args, **kwargs
    ) -> Base: # Union[Matplotlib, Plotly]:
    """
    Factory function to create a plotter instance based on the selected library.
    """
    if visualaizer == "matplotlib":
        return Matplotlib(*args, **kwargs)
    elif visualaizer == "plotly":
        return Plotly(*args, **kwargs)
    else:
        raise Exception("visualaizer not available. Choose between 'matplotlib' and 'plotly'")

    
#%%
class Plotly(Base):
    
    def __init__(
            self,
            height: int = 500,
            width: int = 700,
            percentage: float = 0, 
            *args, **kwargs
        ):
        """
        Base class for all plotly plots.
        """
        self.height = height
        self.width = width
        self.percentage = percentage
        self.id = "plotly"
        # self.unit = unit

        if self.unit == "Hz":
            self.unit_scalar = 1
        elif self.unit == "kHz":
            self.unit_scalar = 1e-3
        super().__init__(*args, **kwargs)

    def spectrogram(
            self,
            obj: Any,
            type: Literal["2d", "3d"] = "2d",
            auxiliar: Literal["freq", "time", "both", "histogram", "none"] = "none",
            mode: Literal["max", "mean", "histogram"] = "mean",
            waveforme : bool = False,
            grid: bool = True,
            ff: bool = False,
            click: Literal["none", "t", "multiple"] = "none",
            legend: bool = False,
            ylim=None,
        ) -> FigurePlotly | Figure:
        """
        Plot the spectrogram of a Syllable or Song object using Plotly.
        """
        df = pd.DataFrame(data=obj.Sxx_dB, columns=obj.time+obj.t0, index=obj.freq*self.unit_scalar)
        
        zmin = df.values.min()
        zmax = df.values.max()
        
        # create figure
        fig = go.Figure()

        fig.update_layout(
            height = self.height,
            width = self.width,
            bargap = 0,
            hovermode = 'closest',
            showlegend = False,
            autosize=False,
            title = f"Spectrogram of {obj.file_id}",
            title_x = 0.5,
            title_y = 0.99,

            margin=dict(t=40, b=0, l=0, r=0),
            # template="plotly_white",
        )

        
        if type=="3d":
            # Fundamental Frequency
            if ff:
                fig.add_trace(
                    go.Scatter3d(
                        x = obj.time + obj.t0,
                        y = obj.ff*self.unit_scalar,
                        z = [0]*len(obj.ff),  # Set Z to a constant value for the markers
                        mode='markers',
                        marker=dict(symbol='circle', size=6, color='black'),
                        line=dict(color='black', width=1, dash='solid'),
                        hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Fundamental</b>: %{{y:.2f}} {self.unit}<extra></extra>",
                        legendgroup="fundamental",
                        name="Fundamental",
                    )
                )

            # Add surface trace
            fig.add_trace(
                go.Surface(
                    x=df.columns,
                    y=df.index,
                    z=df.values,
                    colorscale=self._COLORS["spectrum"],
                    colorbar=dict(title="dB SPL"),
                    showscale=True, #zmin=zmin, zmax=zmax,
                    hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Frequency</b>: %{{y:.2f}} {self.unit}<br><b>SPL (dB)</b>: %{{z:.2f}}<extra></extra>"
                )
            )
            fig.update_scenes(
                xaxis=dict(
                    title="Time (s)",
                    range=[df.columns.min(), df.columns.max()]
                ),
                yaxis=dict(
                    title=f"Frequency ({self.unit})",
                    range=[df.index.min(), df.index.max()]
                ),
                aspectratio=dict(x=1, y=1, z=0.6),
                aspectmode="manual",
                zaxis=dict(range=[zmin, zmax], autorange=False),
                camera=dict(
                    eye=dict(x=0.2, y=0.2, z=2),
                    up=dict(x=0, y=1, z=0)
                )
            )

            # Update plot sizing
            fig.update_layout(
                margin=dict(t=70, b=0, l=0, r=0),
                yaxis=dict(title=f"Frequency ({self.unit})"),
                xaxis=dict(
                    title="Time (s)",
                    range=[df.columns.min(), df.columns.max()]
                ),
                # zaxis=dict(title="SPL (dB)"),
                
                # Add dropdown
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        buttons=[
                            dict(
                                args=["type", "surface"],
                                label="3D Surface",
                                method="restyle"
                            ),
                            dict(
                                args=["type", "heatmap"],
                                label="Heatmap",
                                method="restyle"
                            ),
                        ],
                        pad={"l": 0, "t": 0},
                        showactive=True,
                        x=0,
                        xanchor="left",
                        y=1.15,
                        yanchor="top",
                    ),
                ],

                # Add annotation at top left, outside plot, aligned with menu
                annotations=[
                    dict(
                        text="Trace type:",
                        showarrow=False,
                        x=0,
                        y=1.15,
                        xref="paper",
                        yref="paper",
                        align="left",
                        yanchor="top",
                        xanchor="left",
                        font=dict(size=14)
                    )
                ]
            )

            # Update 3D scene options
            fig.update_scenes(
                aspectratio=dict(x=1, y=1, z=0.6),
                aspectmode="manual",
                zaxis=dict(range=[zmin, zmax], autorange=False),
                xaxis=dict(title="Time (s)", range=[df.columns.min(), df.columns.max()]),
                yaxis=dict(title=f"Frequency ({self.unit})", range=[df.index.min(), df.index.max()]),
                camera=dict(
                    eye=dict(x=0.2, y=0.2, z=2),
                    up=dict(x=0, y=1, z=0)
                )
            )

            return fig

        # 2d spectrogram"
        elif type=="2d":
            # Spectrum
            fig.add_trace(
                go.Heatmap(
                    x=df.columns,
                    y=df.index,
                    z=df.values,
                    colorscale=self._COLORS["spectrum"],
                    colorbar=dict(
                        title="SPL (dB)",
                        len=0.7,
                        y=0.5,
                        # x=-0.15,
                        # ticklabelposition="outside left",
                        # # ticklabelposition='inside',
                        # ticksuffix='     ',
                        # ticklabeloverflow='allow',
                        # tickfont_color='darkslategrey',
                        # ticks="outside",
                        # tickmode="auto",
                    ),
                    showscale=True,
                    hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Frequency</b>: %{{y:.2f}} {self.unit}<br><b>SPL</b>: %{{z:.2f}} dB<extra></extra>",
                    xaxis="x1",
                    yaxis="y1",
                )
            )
            
            try:
                threshold_2_plot  = go.Scatter(
                    x = obj.time_s + obj.t0,
                    y = obj.time_s.size*[obj.threshold_2],
                    yaxis = 'y2',
                    hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Threshold</b>: %{{y:.2f}} a.u.<extra></extra>",
                    legendgroup="threshold2",
                    name="Threshold_2",
                    line=dict(color=self._COLORS["threshold_2"], width=2, dash='dash'),
                )
            except AttributeError:
                warnings.warn("Threshold_2 not found in the object. Skipping threshold line.")
            # Mode to calculate the auxiliar plots
            if mode == "max":
                x = obj.Sxx_ff_max
                y = obj.Sxx_time_max
            elif mode == "mean":
                x = obj.Sxx_ff_max
                y = obj.Sxx_time_max
            elif mode == "histogram":
                pass
            else:
                raise Exception("Mode must be 'max', 'mean', or 'histogram'.")
            # Auxiliar plots
            if mode == "max" or mode == "mean":
                auxiliar_plots = [
                    go.Scatter(
                        y = df.index,
                        x = x,
                        xaxis = 'x2',
                        hovertemplate=f"<b>Frequency</b>: %{{y:.2f}} {self.unit}<br><b>Max Intensity</b>: %{{x:.2f}} dB<br><extra></extra>",
                        legendgroup="freq_max",
                        name="Frequency Max",  
                    ),
                    go.Scatter(
                        x = list(df.columns),
                        y = y,
                        yaxis = 'y2',
                        hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Max Intensity</b>: %{{y:.2f}} dB<br><extra></extra>",
                        legendgroup="time_max",
                        name="Time Max",
                    )
                ]
            elif mode == "histogram":
                # Count the occurrence (sum) for each frequency bin (over time)
                freq_hist = np.sum(obj.Sxx_dB, axis=1)   # shape: (n_freq,)
                # Count the occurrence (sum) for each time bin (over frequency)
                time_hist = np.sum(obj.Sxx_dB, axis=0)   # shape: (n_time,)

                auxiliar_plots = [
                    go.Bar(
                        y=obj.freqs,         # Frequency bins (vertical axis)
                        x=freq_hist,     # Sum of Sxx_dB for each frequency
                        orientation='h',
                        xaxis='x2',
                        name="Frequency Histogram",
                        marker_color='#EB89B5',
                        opacity=0.75,
                        hovertemplate=f"<b>Frequency</b>: %{{y:.2f}} {self.unit}<br><b>Sum</b>: %{{x:.2f}}<extra></extra>",
                    ),
                    go.Bar(
                        x=obj.times,         # Time bins (horizontal axis)
                        y=time_hist,     # Sum of Sxx_dB for each time
                        yaxis='y',       # Stick to the left margin (main y axis)
                        name="Time Histogram",
                        marker_color='#EB89B5',
                        opacity=0.75,
                        hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Sum</b>: %{{y:.2f}}<extra></extra>",
                    )
                ]

            # Grid
            xaxis1 = dict()
            yaxis1 = dict()
            xaxis2 = dict()
            yaxis2 = dict()
            xaxis3 = dict()
            yaxis3 = dict()
            
            # both
            if auxiliar == "both":
                fig.add_traces(auxiliar_plots)
                try:
                    fig.add_trace(threshold_2_plot)
                except UnboundLocalError:
                    warnings.warn("Threshold_2 not found in the object. Skipping threshold line.")

                xaxis1 = dict(
                    zeroline = False,
                    domain = [0,0.9],
                    showgrid = grid,
                    title="Time (s)"
                )
                xaxis2 = dict(
                    zeroline = False,
                    domain = [0.905,1],
                    showgrid = grid,
                    title="SPL (dB)"
                )

                if waveforme:
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,0.65],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
                    yaxis2 = dict(
                        zeroline = False,
                        domain = [0.655,0.75],
                        showgrid = False,
                        title="SPL (dB)"
                    )
                    yaxis3 = dict(
                        zeroline = False,
                        domain = [0.755,1],
                        showgrid = False,
                        title="Amplitude (a.u)",
                        title_standoff=0,
                        title_font=dict(size=12),
                        side="right"
                    )
                else:
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,0.85],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
                    yaxis2 = dict(
                        zeroline = False,
                        domain = [0.855,1],
                        showgrid = False
                    )
            # frequency
            elif auxiliar == "freq":
                fig.add_trace(auxiliar_plots[0])
                xaxis1 = dict(
                    zeroline = False,
                    domain = [0,0.9],
                    showgrid = grid,
                    title="Time (s)"
                )
                xaxis2 = dict(
                    zeroline = False,
                    domain = [0.905,1],
                    showgrid = grid,
                    title="SPL (dB)"
                )
                if waveforme:    
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,0.8],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
                    yaxis3 = dict(
                        zeroline = False,
                        domain = [0.805,1],
                        showgrid = False
                    )
                else:
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,1],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
            # time
            elif auxiliar == "time":
                fig.add_trace(auxiliar_plots[1])
                try:
                    fig.add_trace(threshold_2_plot)
                except UnboundLocalError:
                    warnings.warn("Threshold_2 not found in the object. Skipping threshold line.")

                xaxis1 = dict(
                        zeroline = False,
                        domain = [0,1],
                        showgrid = grid,
                        title="Time (s)"
                    )
                if waveforme:
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,0.65],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
                    yaxis2 = dict(
                        zeroline = False,
                        domain = [0.655,0.75],
                        showgrid = False
                    )
                    yaxis3 = dict(
                        zeroline = False,
                        domain = [0.755,1],
                        showgrid = False,
                        title="Amplitude (a.u)"
                    )

                else:
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,0.8],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
                    yaxis2 = dict(
                        zeroline = False,
                        domain = [0.805,1],
                        showgrid = False
                    )
            # None
            elif auxiliar == "none":
                xaxis1 = dict(
                    zeroline = False,
                    domain = [0,1],
                    showgrid = grid,
                    title="Time (s)"
                )

                if waveforme:
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,0.75],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
                    yaxis3 = dict(
                        zeroline = False,
                        domain = [0.755,1],
                        showgrid = False,
                        title="Amplitude (a.u)"
                    )
                else:
                    yaxis1 = dict(
                        zeroline = False,
                        domain = [0,1],
                        showgrid = grid,
                        title="Frequency (kHz)"
                    )
            else:
                raise Exception("You must select at least one auxiliar plot: 'freq', 'time' or 'both'.")
            
            if waveforme:
                fig.add_traces([
                        go.Scatter(
                            x = obj.time_s + obj.t0,
                            y = obj.s,
                            yaxis = 'y3',
                            hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Amplitude</b>: %{{y:.2f}} a.u.<extra></extra>",
                            legendgroup="waveform",
                            name="Waveform",
                            line=dict(color="#598db3", width=1, dash='solid'),
                        ),
                        go.Scatter(
                            x = obj.time_s + obj.t0,
                            y = obj.envelope,
                            yaxis = 'y3',
                            hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Envelope</b>: %{{y:.2f}} a.u.<extra></extra>",
                            legendgroup="envelope",
                            name="Envelope",
                            line=dict(color="#081D57", width=2, dash='solid'),
                        ),
                    ]
                )
                try:
                    fig.add_trace(
                        go.Scatter(
                            x = obj.time_s + obj.t0,
                            y = obj.time_s.size*[obj.threshold_1],
                            yaxis = 'y3',
                            hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Threshold</b>: %{{y:.2f}} a.u.<extra></extra>",
                            legendgroup="threshold1",
                            name="Threshold_1",
                            line=dict(color=self._COLORS["threshold_1"], width=2, dash='dash'),
                        ),
                    )
                except AttributeError:
                    warnings.warn("Threshold_1 not found in the object. Skipping threshold line.")
            # Fundamental Frequency
            if ff:
                fig.add_trace(
                    go.Scatter(
                        x = obj.time + obj.t0,
                        y = obj.ff*self.unit_scalar,
                        mode='markers',
                        marker=dict(symbol='circle', size=6, color='black'),
                        line=dict(color='black', width=1, dash='solid'),
                        hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Fundamental</b>: %{{y:.2f}} {self.unit}<extra></extra>",
                        legendgroup="fundamental",
                        name="Fundamental",
                    )
                )
            # Show only selected traces in the legend, place legend at the bottom
            fig.update_layout(
                showlegend=legend,
                legend=dict(
                    itemsizing='constant',
                    title="Elements:",
                    orientation="h",
                    yanchor="top",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    title_font=dict(
                        family="Arial",
                        # size=18,
                        color="black",
                        weight="bold"
                    )
                ),
            )
            
            range_freq = [df.index.min(), df.index.max()] if ylim is None else ylim
            offset = self.percentage*(obj.time[-1] - obj.time[0])
            fig.update_layout(
                autosize = False,
                xaxis1 = xaxis1,
                yaxis1 = yaxis1,
                xaxis2 = xaxis2,
                yaxis2 = yaxis2,
                xaxis3 = xaxis3,
                yaxis3 = yaxis3,
                xaxis=dict(
                    title="Time (s)",
                    range=[df.columns.min()-offset, df.columns.max()+offset]
                ),
                yaxis=dict(
                    title=f"Frequency ({self.unit})",
                    range=range_freq
                ),
            )

        fig.show()

        return fig
    #%%
    def alpha_beta(
        self,
        obj: Synthetic,
        xlim: tuple[float, float] = (-0.05, 0.2),
        ylim: tuple[float, float] = (-0.2, 0.9),
        figsize: tuple[float, float] = (8, 6),
        save: bool = False,
        show: bool = True,
        # cmap: str = "Blues",
        # self.over_sample_mg: int = 100,
    ):
        """
        """
        
        self.width = figsize[0]*100
        self.height = figsize[1]*100

        viridis = plt.get_cmap(self._COLORS["motor_gesture"])
        c = viridis(np.linspace(0.3, 1, np.size(obj.time_s)))
        c_hex = [mcolors.rgb2hex(rgba) for rgba in c]

        # Create subplots: 2 rows, 2 columns, with shared x/y axes where needed
        fig = make_subplots(
            rows=2, cols=2,
            column_widths=[0.5, 0.5],
            row_heights=[0.4, 0.6],
            specs=[
            [{}, {"rowspan": 2}],
            [{}, None]
            ],
            horizontal_spacing=0.05,
            vertical_spacing=0.1,
            subplot_titles=("Air-Sac Pressure", "Parameter Space", "Labial Tension", ""),
        )

        # Air-Sac Pressure (alpha) scatter
        fig.add_trace(
            go.Scatter(
                x=obj.time_s[::self.over_sample_mg], y=obj.alpha[::self.over_sample_mg],
                mode='markers',
                marker=dict(color=c_hex[::self.over_sample_mg]),
                name="alfa",
                showlegend=False,
                hovertemplate=f"<b>Air-Sac Pressure</b><br><b>  Time</b>: %{{x:.2f}} s<br><b>  Alpha</b>: %{{y:.2f}} a.u.<extra></extra>",
            ),
            row=1, col=1
        )

        # Labial Tension (beta) scatter
        fig.add_trace(
            go.Scatter(
                x=obj.time_s[::self.over_sample_mg], y=obj.beta[::self.over_sample_mg],
                mode='markers',
                # marker=dict(color=c_hex[::self.over_sample_mg]),
                name="beta",
                showlegend=False,
                hovertemplate=f"<b>Labial Tension</b><br><b>  Time</b>: %{{x:.2f}} s<br><b>  Beta</b>: %{{y:.2f}} a.u.<extra></extra>",
                marker=dict(
                    colorscale=self._COLORS["motor_gesture"],
                    cmin=0, cmax=obj.time_s[-1],
                    color=c_hex[::self.over_sample_mg],
                    showscale=True,
                    colorbar=dict(
                        title='Time (s)',
                        thickness=20,
                        len=0.515,
                        x=0.205,  # Centered under subplot (1,1)
                        xanchor='center',
                        y=-0.05,
                        yanchor='top',
                        orientation='h',
                        # outlinewidth=1,
                        # outlinecolor='black',
                        tickfont=dict(size=12, family="Arial"),
                        # titlefont=dict(size=14, family="Arial")
                        ypad=0, yref="paper"
                    ),
                ),
            ),
            row=2, col=1
        )

        # Parameter Space (bifurcation diagram)
        # Oscillation region
        mask = obj.mu1_curves[1] >= 0
        x_fill = np.concatenate([obj.mu1_curves[1][mask], obj.mu1_curves[1][mask][::-1]])
        y_fill = np.concatenate([obj.beta_bif[mask], np.full_like(obj.beta_bif[mask], ylim[1])])
        fig.add_trace(
            go.Scatter(
                x=x_fill,
                y=y_fill,
                fill='toself',
                fillcolor='rgba(128,128,128,0.2)',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=True,
                hovertemplate=f"<b>Oscillation Region</b><br><b>  Alpha</b>: %{{x:.2f}}<br><b>  Beta</b>: %{{y:.2f}}<extra></extra>",
                name="Oscillations Region"
            ),
            row=1, col=2
        )
        # Cuspid Point
        fig.add_trace(
            go.Scatter(
                x=[-1/27], y=[1/3],
                mode='markers',
                marker=dict(color='black', symbol='circle', size=10),
                name="Cuspid Point",
                hovertemplate=f"<b>Cuspid Point</b><br><b>  Alpha</b>: %{{x:.2f}}<br><b>  Beta</b>: %{{y:.2f}}<extra></extra>",
            ),
            row=1, col=2
        )
        # Hopf Bifurcation line
        fig.add_trace(
            go.Scatter(
                x=np.zeros(1000),
                y=np.linspace(ylim[0], ylim[1], 1000),
                mode='lines',
                line=dict(color='red', width=2, dash='dash'),
                name="Hopf Bifurcation",
                hovertemplate=f"<b>Hopf Bifurcation</b><br><b>  Alpha</b>: %{{x:.2f}}<br><b>  Beta</b>: %{{y:.2f}}<extra></extra>",
            ),
            row=1, col=2
        )
        # Motor Gesture (alpha, beta)
        fig.add_trace(
            go.Scatter(
                x=obj.alpha[::self.over_sample_mg], y=obj.beta[::self.over_sample_mg],
                mode='markers',
                marker=dict(color=c_hex[::self.over_sample_mg], size=10), # , symbol='line-ew'
                name="Motor Gesture",
                hovertemplate=f"<b>Motor Gesture</b><br><b>  Alpha</b>: %{{x:.2f}}<br><b>  Beta</b>: %{{y:.2f}}<extra></extra>",
            ),
            row=1, col=2
        )
        # Saddle-Node Bifurcation curves
        fig.add_trace(
            go.Scatter(
                x=obj.mu1_curves[0], y=obj.beta_bif,
                mode='lines',
                line=dict(color='green', width=2),
                name="SN Bifurcation 1",
                hovertemplate=f"<b>Saddle-Node</b><br><b>  Alpha</b>: %{{x:.2f}}<br><b>  Beta</b>: %{{y:.2f}}<extra></extra>",
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(
                x=obj.mu1_curves[1], y=obj.beta_bif,
                mode='lines',
                line=dict(color='green', width=2),
                name="SN Bifurcation 2",
                hovertemplate=f"<b>Saddle-Node</b><br><b>  Alpha</b>: %{{x:.2f}}<br><b>  Beta</b>: %{{y:.2f}}<extra></extra>",
            ),
            row=1, col=2
        )

        # Add colorbar as a separate trace (dummy scatter for colorbar)
        # fig.add_trace(
        # go.Scatter(
        #     x=[None], y=[None],
        #     mode='markers',
        #     marker=dict(
        #         colorscale=self._COLORS["motor_gesture"],
        #         cmin=obj.time_s[0], cmax=obj.time_s[-1],
        #         color=c_hex[::self.over_sample_mg],
        #         showscale=True,
        #         colorbar=dict(
        #             title='Time (s)',
        #             thickness=20,
        #             len=0.515,
        #             x=0.205,  # Centered under subplot (1,1)
        #             xanchor='center',
        #             y=-0.05,
        #             yanchor='top',
        #             orientation='h',
        #             # outlinewidth=1,
        #             # outlinecolor='black',
        #             tickfont=dict(size=12, family="Arial"),
        #             # titlefont=dict(size=14, family="Arial")
        #         ),
        #     ),
        #     showlegend=False,
        #     hoverinfo='skip'
        # ),
        # row=2, col=1
        # )


        # Add text annotations
        fig.add_annotation(x=0.01, y=0.4, text="Hopf", showarrow=False, font=dict(color="red", size=15), xref="x2", yref="y2", textangle=90)
        fig.add_annotation(x=-0.035, y=0.39, text="CP", showarrow=False, font=dict(color="black", size=15), xref="x2", yref="y2")
        fig.add_annotation(x=-0.025, y=0., text="SN", showarrow=False, font=dict(color="green", size=15), xref="x2", yref="y2")
        fig.add_annotation(x=0.1, y=0.005, text="SN", showarrow=False, font=dict(color="green", size=15), xref="x2", yref="y2")

        # Update axes and layout
        fig.update_xaxes(title_text="", row=2, col=1, matches='x1')
        fig.update_xaxes(title_text="α (a.u.)", row=1, col=2, range=xlim)
        fig.update_yaxes(title_text="α (a.u.)", row=1, col=1, range=xlim)
        fig.update_yaxes(title_text="β (a.u.)", row=2, col=1, range=ylim)
        fig.update_yaxes(
            title_text="β (a.u.)",
            row=1, col=2,
            range=ylim,
            side="right",
            ticks="outside",
            tickmode="auto",
            tickfont=dict(size=12, family="Arial"),
            title_font=dict(size=16, family="Arial"),
            showline=True,
        mirror=True
        )


        suptitle = (
            f"Motor Gesture Curves\n{self._suptitle(obj)}"
            if (obj.type != "")
            else f"Motor Gesture Curves: {self._suptitle(obj)}"
        )

        fig.update_layout(
            title=dict(text=suptitle, font=dict(size=24, family="Arial", color="black"),
                    y=0.98, x=0.5, xanchor='center', yanchor='top'),
            height=600, width=1000,
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    title="Data:", 
                    title_font=dict(
                                    family="Arial",
                                    # size=18,
                                    color="black",
                                    weight="bold"
                                ),
                    font=dict(size=12, family="Arial", color="black", 
                            weight="normal"),
                    # bgcolor="LightGray",
                    # bordercolor="Black",
                    # borderwidth=1
                ),
            margin=dict(t=80, l=80, r=30, b=80)
        )

        if save:
            save_name = f"{self._save_name(obj)}-mg_params.html"
            # fig.write_html(str(obj.proj_dirs.IMAGES / save_name))
            print(f"Image save at {save_name}")

        if show:
            fig.show()
    
        return fig
    #%%
    def metrics(
            self,
            obj: Syllable,
            obj_synth: Synthetic,
            figsize: tuple[float, float] = (9, 7),
            ylim: tuple[float, float] = (0, 10),
            save: bool = True,
            grid: bool = True,
            show: bool = True,
        ):
        # Create subplots: 3 rows, 1 column
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.25, 0.5, 0.25],
            subplot_titles=[],
            specs=[[{}], [{}], [{"secondary_y": True}]]
        )

        # 1. Relative Error subplot
        fig.add_trace(
            go.Scatter(
                x=obj_synth.time,
                y=100 * obj_synth.deltaSCI,
                mode='lines+markers',
                name=self._LABELS["sci"] + str(round(100 * obj_synth.deltaSCI_mean, 2)),
                marker=dict(symbol='star', color=self._COLORS["sci_error"], size=7),
                line=dict(color=self._COLORS["sci_error"], width=1),
                legend="legend1",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Relative Error SCI</b>: %{{y:.2f}} %<extra></extra>",
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=obj_synth.time,
                y=100 * obj_synth.deltaFF,
                mode='lines+markers',
                name=self._LABELS["ff"] + str(round(100 * obj_synth.deltaFF_mean, 2)),
                marker=dict(symbol='star', color=self._COLORS["ff_error"], size=7),
                line=dict(color=self._COLORS["ff_error"], width=1),
                legend="legend1",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Relative Error Fundamental</b>: %{{y:.2f}} %<extra></extra>",
            ),
            row=1, col=1
        )


        # 2. Spectrogram & FF subplot
        # Plot spectrogram as heatmap
        fig.add_trace(
            go.Heatmap(
                z=obj.Sxx_dB,
                x=obj.time,
                y=obj.freq,
                colorscale=self._COLORS["spectrum"],
                colorbar=dict(
                title=self._LABELS["power"],
                len=0.5,
                y=0.5,
                title_side='right',
                title_font=dict(size=14),
                ),
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Frequency</b>: %{{y:.2f}} {self.unit}<br><b>Intensity</b>: %{{z:.2f}} dB<extra></extra>",
                # legend="legend2",
            ),
            row=2, col=1
        )
        # Overlay FF curves
        fig.add_trace(
            go.Scatter(
                x=obj.time,
                y=obj.ff,
                mode='lines+markers',
                name=self._LABELS["ff_real"],
                marker=dict(symbol='star', color=self._COLORS["real_ff"], size=7),
                line=dict(color=self._COLORS["real_ff"], width=2),
                legend="legend2",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Fundamental</b>: %{{y:.2f}} {self.unit}<extra></extra>",
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=obj_synth.time,
                y=obj_synth.ff,
                mode='lines+markers',
                name=self._LABELS["ff_synth"],
                marker=dict(symbol='circle', color=self._COLORS["synth_ff"], size=5),
                line=dict(color=self._COLORS["synth_ff"], width=2),
                legend="legend2",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Fundamental</b>: %{{y:.2f}} {self.unit}<extra></extra>",
            ),
            row=2, col=1
        )

        # 3. SCI & Acoustical Features subplot
        fig.add_trace(
            go.Scatter(
                x=obj.time,
                y=obj.SCI,
                mode='lines+markers',
                name=self._LABELS["lr"] + str(round(obj.SCI.mean(), 2)),
                marker=dict(symbol='star', color=self._COLORS["sci_real"], size=7),
                line=dict(color=self._COLORS["sci_real"], width=2),
                legend="legend3",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>SCI</b>: %{{y:.2f}} dl<extra></extra>",
            ),
            row=3, col=1, secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                x=obj.time,
                y=obj_synth.SCI,
                mode='lines+markers',
                name=self._LABELS["ls"] + str(round(obj_synth.SCI.mean(), 2)),
                marker=dict(symbol='circle', color=self._COLORS["sci_synth"], size=5),
                line=dict(color=self._COLORS["sci_synth"], width=2),
                legend="legend3",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>SCI</b>: %{{y:.2f}} dl<extra></extra>",
            ),
            row=3, col=1, secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                x=obj.time,
                y=obj_synth.Df,
                mode='markers',
                name=self._LABELS["lh"] + str(round(obj_synth.Df.mean(), 2)),
                marker=dict(symbol='hexagram', color=self._COLORS["df"], size=6),
                legend="legend3",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Df</b>: %{{y:.2f}} dl<extra></extra>",
            ),
            row=3, col=1, secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=obj_synth.time,
                y=obj_synth.SKL,
                mode='markers',
                name=self._LABELS["lskl"] + str(round(obj_synth.SKL.mean(), 2)),
                marker=dict(symbol='square', color=self._COLORS["skl"], size=6),
                legend="legend3",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>SKL</b>: %{{y:.2f}} dl<extra></extra>",
            ),
            row=3, col=1, secondary_y=False,
        )

        correlation_synth = obj_synth.correlation.mean()
        fig.add_trace(
            go.Scatter(
                x=obj.time,
                y=obj_synth.correlation,
                mode='markers',
                name=self._LABELS["lc"] + str(round(correlation_synth, 2)),
                marker=dict(symbol='pentagon', color=self._COLORS["correlation"], size=6),
                legend="legend3",
                hovertemplate=f"<b>Time</b>: %{{x:.2f}} s<br><b>Correlation</b>: %{{y:.2f}} dl<extra></extra>",
            ),
            row=3, col=1, secondary_y=False,
        )

        fig.update_yaxes(range=[0, 1], row=3, col=1, secondary_y=False)
        fig.update_yaxes(range=[0, 10], row=3, col=1, secondary_y=True)
        # Update axes and layout
        fig.update_xaxes(title_text="Time (s)", row=3, col=1)
        fig.update_yaxes(title_text="Relative Error (%)", row=1, col=1)
        fig.update_yaxes(title_text="Frequency (Hz)", row=2, col=1)
        # fig.update_yaxes(title_text="SCI / Features", row=3, col=1)

        fig.update_yaxes(title_text="Similarity (dl)", secondary_y=False, row=3, col=1)
        fig.update_yaxes(title_text="SCI (dl)", secondary_y=True, title_standoff=20, row=3, col=1)

        suptitle = (
            f"Scoring Variables\n{self._suptitle(obj)}"
            if (obj.type != "")
            else f"Scoring Variables: {self._suptitle(obj)}"
        )
        fig.update_layout(
            height=figsize[1]*100,
            width=figsize[0]*100,
            title_text=suptitle,
            title_x=0.5,
            title_y=0.95,
            title_font=dict(size=22, family="Arial", color="black", weight="bold"),
            showlegend=True,

            legend=dict(
                title=dict(
                    text="Data:", 
                    font=dict(size=16, color='black', family='Arial', weight='bold'),
                ),
                xref="paper",
                yref="paper",
                y=0.99, x=1.05,
                # itemsizing='constant',
                # itemclick='toggleothers',
                bordercolor='lightgray',
                borderwidth=1,
            ),
            legend2=dict(
                title=dict(
                    text=""
                ),
                xref="paper",
                yref="paper",
                x=0.85, y=0.71,
                # itemsizing='constant',
                # itemclick='toggleothers',
                bordercolor='lightgray',
                borderwidth=1,
            ),
            legend3=dict(
                title=dict(
                    text="Elements:",
                    font=dict(size=16, color='black', family='Arial', weight='bold'),
                ),
                xref="paper",
                yref="paper",
                y=-0.125, x=0.5,
                # bgcolor="Gold"
                yanchor='bottom',
                orientation='h',
                xanchor='center',
                bordercolor='lightgray',
                borderwidth=1,
                bgcolor='rgba(255,255,255,0.95)',
                font=dict(size=14, color='black', family='Arial', shadow=2),
                # itemsizing='constant',
                # itemclick='toggleothers',
            ),
        )

        # Set the same x-axis limits for all subplots
        fig.update_xaxes(range=[obj.time[0], obj.time[-1]], row=1, col=1)
        fig.update_xaxes(range=[obj.time[0], obj.time[-1]], row=2, col=1)
        fig.update_xaxes(range=[obj.time[0], obj.time[-1]], row=3, col=1)

        fig.show()

        return fig

    #%%
    def segmentation(
        self,
        obj,
        harmonics: bool = False,
        fundamental: bool = False,
        alpha: float = 0.9,
        grid: bool = False,
        colorbar: bool = True,
        filters: bool = True,
        figsize: tuple[float, float] = (9, 7),
        label: Literal["syllables", "vocalizations"] = "syllables",
    ) -> FigurePlotly:
        """
        Create a segmentation plot for the given object.

        Args:
            obj: The object to plot.
            harmonics (bool, optional): Whether to include harmonics. Defaults to False.
            fundamental (bool, optional): Whether to include fundamental frequency. Defaults to False.
            alpha (float, optional): The transparency level for the plots. Defaults to 0.9.
            grid (bool, optional): Whether to show grid lines. Defaults to False.
            colorbar (bool, optional): Whether to show colorbar. Defaults to True.
            filters (bool, optional): Whether to include filters. Defaults to True.
            figsize (Tuple[float, float], optional): The size of the figure. Defaults to (9, 7).
            label (Literal["syllables", "vocalizations"], optional): The label type. Defaults to "syllables".

        Returns:
            Figure: The created figure.
        """

        shape = (3, 2) if filters else (3, 1)
        rows, cols = shape

        fig = make_subplots(
            rows=rows, cols=cols,
            shared_xaxes=True,
            shared_yaxes=True,
            horizontal_spacing=0.05,
            vertical_spacing=0.1,
            subplot_titles=[
                "Original Spectrogram (dB)",
                "Final Mask (Fundamental + Harmonics)",
                f"Labeled Vocalizations: {obj.num_vocalizations - 1}"
            ] if not filters else [
                "Original Spectrogram (dB)",
                "Median Clipping Filter",
                "Final Mask (Fundamental + Harmonics)",
                "Percentile Filter",
                f"Labeled Syllables: {obj.num_syllables - 1}",
                "Median Clipping AND Percentile Filter",
            ]
        )

        ax_spectrogram = (1, 1)
        ax_harmonics = (2, 1)
        ax_labels = (3, 1)
        if filters:
            ax_mask_1 = (1, 2)
            ax_mask_2 = (2, 2)
            ax_final_mask = (3, 2)
        else:
            ax_mask_1 = (1, 1)
            ax_mask_2 = (2, 1)
            ax_final_mask = (3, 1)

        # Spectrogram
        fig.add_trace(
            go.Heatmap(
                z=obj.Sxx_dB,
                x=obj.time + obj.t0,
                y=obj.freq * 1e-3,
                colorscale=self._COLORS["spectrum"],
                colorbar=dict(title="dB"),
                showscale=False,
                zsmooth='best',
                opacity=1.0,
                hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f} kHz<br>SPL: %{z:.2f} dB<extra></extra>"
            ),
            row=ax_spectrogram[0], col=ax_spectrogram[1]
        )
        fig.update_xaxes(range=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0], row=ax_spectrogram[0], col=ax_spectrogram[1])
        fig.update_yaxes(range=[obj.freq[0] * 1e-3, obj.freq[-1] * 1e-3], row=ax_spectrogram[0], col=ax_spectrogram[1])

        cmap = plt.get_cmap(self._COLORS["syllable_labels"])
        # Harmonics Mask
        fig.add_traces([
            go.Heatmap(
                # z=obj.harmonics_rois.astype(int),
                z=1*obj.harmonics_rois.astype(int), # all_mask,
                x=obj.time + obj.t0,
                y=obj.freq * 1e-3,
                name="Harmonics",
                colorscale=self._COLORS["spectrum"],
                opacity=0.8,
                showscale=False,
                showlegend=False,
                hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f}kHz<br>Label: %{z}<extra></extra>"
            ),
            go.Heatmap(
                # z=obj.harmonics_rois.astype(int),
                z=2*obj.mask.astype(int), # all_mask,
                x=obj.time + obj.t0,
                y=obj.freq * 1e-3,
                name="Fundamental",
                colorscale=self._COLORS["spectrum"],
                showscale=False,
                showlegend=False,
                opacity=0.7,
                hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f}kHz<br>Label: %{z}<extra></extra>"
            )],
            rows=ax_harmonics[0], cols=ax_harmonics[1]
        )


        if fundamental:
            fig.add_trace(
                go.Scatter(
                    x=obj.time + obj.t0,
                    y=obj.ff_sp * 1e-3,
                    mode='markers',
                    marker=dict(color='red', symbol='pentagon', size=5),
                    name="Fundamental",
                    showlegend=False,
                    hovertemplate="Time: %{x:.2f} s<br>Fundamental Frequency: %{y:.2f} kHz<extra></extra>"
                ),
                row=ax_harmonics[0], col=ax_harmonics[1]
            )
        if harmonics:
            for i in range(len(obj.harmonics)):
                fig.add_trace(
                    go.Scatter(
                        x=obj.time + obj.t0,
                        y=obj.harmonics[i] * 1e-3,
                        mode='markers',
                        marker=dict(
                            color=f'rgba({int(255*i/(len(obj.harmonics)-1))},0,255,1)' if len(obj.harmonics) > 1 else "rgba(0,0,255,1)",
                            symbol='pentagon',
                            size=5
                        ),
                        name=f"Harmonic {i+1}",
                        showlegend=False,
                        hovertemplate=f"Time: %{{x:.2f}} s<br>Harmonic {i+1} Frequency: %{{y:.2f}} kHz<extra></extra>"
                    ),
                    row=ax_harmonics[0], col=ax_harmonics[1]
                )

        def colors_array(N):
            bvals = np.arange(0, N + 1)  # Create a range from 0 to N
            colors = [
                'rgb({}, {}, {})'.format(*(np.array(cmap(i / N))[:3] * 255).astype(int)) for i in range(N)
            ]
            # colors[-1] = 'rgb(255, 0, 0)'  # Ensure the last color is black for the last segment
            bvals = sorted(bvals)     
            nvals = [(v-bvals[0])/(bvals[-1]-bvals[0]) for v in bvals]  #normalized values

            dcolorscale = [] #discrete colorscale
            for k in range(len(colors)):
                dcolorscale.extend([[nvals[k], colors[k]], [nvals[k+1], colors[k]]])
                
            return dcolorscale

        dcolorscale = colors_array(obj.num_vocalizations)
        dcolorscale_ff = colors_array(obj.num_syllables)   

        labels = obj.syllables if label == "syllables" else obj.vocalizations
        num_vocalizations = obj.num_syllables if label == "syllables" else obj.num_vocalizations
        print("Num features ", num_vocalizations)

        def ColorBar(num_features, colorbar):
            return dict(
                    title=dict(
                        text="Label: ",
                        font=dict(weight="bold")
                    ),
                    tickvals=list(range(num_features + 1)),
                    ticktext=[str(i) for i in range(num_features + 1)],
                    orientation='h',
                    x=0.5,
                    y=-0.1,
                    xanchor='center',
                    yanchor='top',
                    len=0.85,
                    thickness=20,
                    # Divide the colorbar into equal segments for each label
                    tickmode='array',
                    nticks=num_features + 1
                ) if colorbar else dict()

        fig.add_traces([
            go.Heatmap(
                z=obj.Sxx_dB,
                x=obj.time + obj.t0,
                y=obj.freq * 1e-3,
                colorscale='greys',
                colorbar=dict(title="dB"),
                showscale=False,
                # zsmooth='best',
                opacity=1,
                hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f} kHz<br>SPL: %{z:.2f} dB<extra></extra>"
            ),
            go.Heatmap(
                z=labels,
                x=obj.time + obj.t0,
                y=obj.freq * 1e-3,
                colorscale=dcolorscale_ff if label == "syllables" else dcolorscale,
                showscale=colorbar,
                opacity=0.5,
                colorbar=ColorBar(num_vocalizations, colorbar),
                hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f} kHz<br>Label: %{z}<extra></extra>"
            )
            ],
            rows=ax_labels[0], cols=ax_labels[1]
        )

        # Show filters masks
        if filters:
            fig.add_trace(
                go.Heatmap(
                    z=obj.mask_1,
                    x=obj.time + obj.t0,
                    y=obj.freq * 1e-3,
                    colorscale=self._COLORS["spectrum"],
                    showscale=False,
                    opacity=alpha,
                    hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f} kHz<br>Mask 1: %{z}<extra></extra>"
                ),
                row=ax_mask_1[0], col=ax_mask_1[1]
            )
            fig.add_trace(
                go.Heatmap(
                    z=obj.mask_2,
                    x=obj.time + obj.t0,
                    y=obj.freq * 1e-3,
                    colorscale=self._COLORS["spectrum"],
                    showscale=False,
                    opacity=alpha,
                    hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f} kHz<br>Mask 2: %{z}<extra></extra>"
                ),
                row=ax_mask_2[0], col=ax_mask_2[1]
            )
            fig.add_trace(
                go.Heatmap(
                    z=obj.mask_pre_proc,
                    x=obj.time + obj.t0,
                    y=obj.freq * 1e-3,
                    colorscale=self._COLORS["spectrum"],
                    showscale=False,
                    opacity=alpha,
                    hovertemplate="Time: %{x:.2f} s<br>Frequency: %{y:.2f} kHz<br>Preproc Mask: %{z}<extra></extra>"
                ),
                row=ax_final_mask[0], col=ax_final_mask[1]
            )
            

        fig.update_layout(
            title=dict(
                text=f"Image Processing Segmentation of {obj.file_id} ({obj.tlim[0]}s - {obj.tlim[1]}s)",
                x=0.5,
                xanchor='center'
            ),
            height=figsize[1]*100,
            width=figsize[0]*100,
            showlegend=True
        )

        fig.update_yaxes(title_text="Frequency (kHz)", row=2, col=1)
        fig.update_xaxes(title_text="Time (s)", row=ax_labels[0], col=ax_labels[1])
        fig.update_xaxes(title_text="Time (s)", row=ax_final_mask[0], col=ax_final_mask[1])
        fig.update_xaxes(matches='x')
        fig.update_yaxes(matches='y')

        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                fig.update_xaxes(showgrid=grid, gridwidth=1, gridcolor='white', row=r, col=c)
                fig.update_yaxes(showgrid=grid, gridwidth=1, gridcolor='white', row=r, col=c)



        filters_variables = [obj.mask_1, obj.mask_2, obj.mask_pre_proc] if filters else [] 
        # Update the correct annotation index and axis layout depending on filters
        label_annotation_idx = 4 if filters else 2
        label_axis = {"xaxis": "x5", "yaxis": "y5"} if filters else {"xaxis": "x3", "yaxis": "y3"}
        label_y = fig.layout.annotations[label_annotation_idx]['y'] if filters else fig.layout.annotations[label_annotation_idx]['y'] # type: ignore


        def make_annotations(label_type):
            # Copy all annotation objects except the label annotation
            annotations = [a for i, a in enumerate(fig.layout.annotations) if i != label_annotation_idx]  # type: ignore
            # Add the updated label annotation at the correct index
            label_text = f"Labeled Syllables: {obj.num_syllables - 1}" if label_type == "syllables" else  f"Labeled Vocalizations: {obj.num_vocalizations - 1}"
            label_anno = dict(
                text=label_text,
                x=fig.layout.annotations[label_annotation_idx]['x'],  # type: ignore
                y=label_y,
                xref='paper',
                yref='paper',
                showarrow=False,
                font=dict(size=16),
                xanchor='center',
                yanchor='bottom'
            )
            annotations.insert(label_annotation_idx, label_anno)
            return annotations

        fig.update_layout(
            updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=-0.1,
                y=1.2,
                xanchor="left",
                yanchor="top",
                buttons=[
                dict(
                    label="syllables",
                    method="update",
                    args=[
                    {
                        # Ensure the spectrogram always uses the same colorscale and opacity
                        "z": [obj.Sxx_dB, 1*obj.harmonics_rois.astype(int), 2*obj.mask.astype(int), obj.Sxx_dB*-1, obj.syllables] + filters_variables,
                        "colorscale": [self._COLORS["spectrum"]]*3 + ['Greys', dcolorscale_ff] + [self._COLORS["spectrum"]]*len(filters_variables),
                        "showscale": [False, False, False, False, colorbar] + [False]*len(filters_variables),
                        "opacity": [1.0, 0.8, 0.7, 0.9, 0.45] + [alpha]*len(filters_variables),
                        "colorbar": [dict(title="dB"), dict(), dict(), dict(title="dB"), ColorBar(obj.num_syllables, colorbar)] + [dict()]*len(filters_variables)
                    },
                    {"annotations": make_annotations("syllables")},
                    label_axis
                    ]
                ),
                dict(
                    label="vocalizations",
                    method="update",
                    args=[
                    {
                        # Ensure the spectrogram always uses the same colorscale and opacity
                        "z": [obj.Sxx_dB, 1*obj.harmonics_rois.astype(int), 2*obj.mask.astype(int), obj.Sxx_dB*-1, obj.vocalizations] + filters_variables,
                        "colorscale": [self._COLORS["spectrum"]]*3 + ['Greys', dcolorscale] + [self._COLORS["spectrum"]]*len(filters_variables),
                        "showscale": [False, False, False, False, colorbar] + [False]*len(filters_variables),
                        "opacity": [1.0, 0.8, 0.7, 0.9, 0.45] + [alpha]*len(filters_variables),
                        "colorbar": [dict(title="dB"), dict(), dict(), dict(title="dB"), ColorBar(obj.num_vocalizations, colorbar)] + [dict()]*len(filters_variables)
                    },
                    {"annotations": make_annotations("vocalizations")},
                    label_axis
                    ]
                )
                ],
                showactive=True
            )
            ]
        )

        fig.show()

        return fig
    #%%
    def physical_variables(
        self,
        obj: Synthetic,
        xlim: tuple[float, float] = (0, 1000),
        figsize: tuple[float, float] = (1000, 600),
        save: bool = False,
        show: bool = True,
        grid: bool = False,
        oversampling: int = 10,
    ) -> FigurePlotly:
        """
        Plot physical model variables using Plotly.

        Parameters
        ----------
            obj : Syllabe|Song
                Song or Syllable to be displayed
            xlim : tuple = (-0.05,.2)
                Time range
            figsize : tuple = (1000,600)
                Figure size (width, height) in pixels
            save : bool = True
                Save plot as HTML
            show : bool = True
                Display plot

        Return
        ------
            None
        """
        if not "synth" in obj.id:
            raise Exception("This is not a synthetic syllable, remember to create"
                            + " a synthetic file using the function bs.Solve().")

        
        fig = make_subplots(
        rows=2, cols=2,
        shared_xaxes="all",  # type: ignore
        subplot_titles=[
            "Labial Walls Displacement",
            "Trachea Input Pressure",
            "Labial Walls Velocity",
            "Trachea Output Pressure"
        ],
        vertical_spacing=0.1,
        horizontal_spacing=0.1,
        )

        # Labial Walls Displacement
        fig.add_trace(
        go.Scatter(
            x=obj.times_vs[::oversampling],
            y=obj.vs[::oversampling, 0],
            mode='lines',
            line=dict(color='red'),
            name="Displacement",
            hovertemplate="Time: %{x:.4f}s<br>Displacement: %{y:.4e}<extra></extra>"
        ),
        row=1, col=1
        )
        # Trachea Input Pressure
        fig.add_trace(
        go.Scatter(
            x=obj.times_vs[::oversampling],
            y=obj.vs[::oversampling, 1],
            mode='lines',
            line=dict(color='green'),
            name="Input Pressure",
            hovertemplate="Time: %{x:.4f}s<br>Input Pressure: %{y:.4e}<extra></extra>"
        ),
        row=1, col=2
        )
        # Labial Walls Velocity
        fig.add_trace(
        go.Scatter(
            x=obj.times_vs[::oversampling],
            y=obj.vs[::oversampling, 0],
            mode='lines',
            line=dict(color='magenta'),
            name="Velocity",
            hovertemplate="Time: %{x:.4f}s<br>Velocity: %{y:.4e}<extra></extra>"
        ),
        row=2, col=1
        )
        # Trachea Output Pressure
        fig.add_trace(
        go.Scatter(
            x=obj.times_vs[::oversampling],
            y=obj.vs[::oversampling, 4],
            mode='lines',
            line=dict(color='blue'),
            name="Output Pressure",
            hovertemplate="Time: %{x:.4f}s<br>Output Pressure: %{y:.4e}<extra></extra>"
        ),
        row=2, col=2
        )

        fig.update_xaxes(title_text="Time (s)", range=xlim, row=2, col=1)
        fig.update_xaxes(title_text="Time (s)", range=xlim, row=2, col=2)

        fig.update_yaxes(title_text="$x(t)$", row=1, col=1)
        fig.update_yaxes(title_text="$p_{in}$", row=1, col=2)
        fig.update_yaxes(title_text="$y(t)$", row=2, col=1)
        fig.update_yaxes(title_text="$p_{out}$", row=2, col=2)

        if grid:
            fig.update_xaxes(showgrid=True)
            fig.update_yaxes(showgrid=True)

        if obj.type != "":
            suptitle = f"Physical Model Variables<br>{self._suptitle(obj)}"
        else:
            suptitle = f"Physical Model Variables: {self._suptitle(obj)}"

        fig.update_layout(
        title=dict(
            text=suptitle,
            font=dict(size=self.title_font["size"], family=None, color=None),
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font_color='black',
            font_family=None,
            font_size=self.title_font["size"],
            font_weight=self.title_font["weight"],
        ),
        height=figsize[1],
        width=figsize[0],
        showlegend=True,
        legend=dict(
            title="Elements: ",
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title_font=dict(size=14, color="black", family=None, weight="bold"),
            # bgcolor="white",
            # bordercolor="black",
            # borderwidth=2,
        )
        )

        if save:
            image_text = f"{self._save_name(obj)}-PhysicalVariables.html"
            fig.write_html(str(obj.proj_dirs.images / image_text))
            print(f"Plot saved at {image_text}")

        if show:
            fig.show()

        return fig
# %%
class Matplotlib(Base):
    
    def __init__(self, *args, **kwargs):
        """
        Base class for all matplotlib plots.
        """
        super().__init__(*args, **kwargs)
        self.id = "mtb"

    #%%
    def spectrogram(
            self,
            obj: Synthetic | Syllable,
            grid: bool = True,
            mode: Literal["max", "mean"] = "max",
            type: Literal["3d", "2d"] = "2d" ,
            auxiliar: Literal["freq", "time", "both", "none"] = "none",
            ff: bool = False,
            click: Literal["time", "multiple", "custom", "none"] = "none",
            waveforme: bool = False,
            save: bool = False,
            legend: bool = False,
            figsize: tuple[float, float] = (8, 6),
            ylim: None | tuple[float, float] = None
        ) -> FigurePlotly | Figure | clicker | None:
        """
        """

        if type == "3d":
            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

            # Plot the surface.
            surf = ax.plot_surface(
                obj.time+obj.t0, obj.freqs*self.unit_scalar, obj.Sxx_dB,
                cmap=self._COLORS["spectrum1"], linewidth=0, antialiased=False
            )
            # plt.scatter(obj.time+obj.t0, obj.ff)

            if ff:
                ax.scatter(
                    obj.time + obj.t0, obj.ff*self.unit_scalar, [0]*len(obj.time),
                    color='black', label='Fundamental (3D)'
                )

            # Customize the z axis.
            ax.set_zlim(obj.Sxx_dB.min(), obj.Sxx_dB.max())
            ax.zaxis.set_major_locator(LinearLocator(10))
            # A StrMethodFormatter is used automatically
            ax.zaxis.set_major_formatter('{x:.0f}')

            ax.set_xlabel('Time (s)')
            ax.set_ylabel(f'Frequency ({self.unit})')
            ax.set_zlabel('SLP (dB)')

            cax = plt.axes((0.9, 0.25, 0.035, 0.6))
            cax.set_title("SLP (dB)", fontsize=10, pad=10, loc='center', x=0.75)
            fig.colorbar(
                surf,
                ax=ax,  # apply to all rows of the first column (spectrogram + waveform)
                # label="SLP (dB)",
                # location='right',
                # pad=0.02,
                # aspect=30,
                # fraction=0.07,
                cax=cax
            )

            fig.subplots_adjust(left=0.01, right=0.95, top=0.9, bottom=0.1)
            plt.show()

        elif type == "2d":
            # Set the width and height ratios based on the auxiliar parameter
            if auxiliar == "freq":
                width_ratios = [6, 1]
                height_ratios = [2, 6] if waveforme else [1]
                shape = (2, 2) if waveforme else (1, 2)

            elif auxiliar == "time":
                width_ratios = [1]
                height_ratios = [3, 1, 6] if waveforme else [1, 6]
                shape = (3, 1) if waveforme else (2, 1)

            elif auxiliar == "none":
                width_ratios = [1]
                height_ratios = [2, 6] if waveforme else [1]
                shape = (2, 1) if waveforme else (1, 1)

            elif auxiliar == "both":
                width_ratios = [6, 1]
                height_ratios = [3, 1, 6] if waveforme else [1, 6]
                shape = (3, 2) if waveforme else (2, 2)

            fig, axs = plt.subplots(
                ncols=shape[1], nrows=shape[0],
                figsize=figsize,
                gridspec_kw={'width_ratios': width_ratios, 'height_ratios': height_ratios}
            )

            ax_colorbar = axs  # apply to all rows of the first column (spectrogram + waveform)
            colorbar_pos = (0.9, 0.4, 0.035, 0.5)
            if auxiliar == "freq":
                ax_spectrogram = axs[1, 0] if waveforme else axs[0]
                ax_waveforme = axs[0, 0] if waveforme else axs[0] # dudas
                ax_freq_aux = axs[1, 1] if waveforme else axs[1]
                ax_time_aux = axs[0]
                ax_colorbar = axs
                # colorbar_pos = (0.9, 0.25, 0.035, 0.5) if waveforme else (0.9, 0.25, 0.035, 0.5)

                if waveforme:
                  axs[0, 1].axis('off')
                  axs[0, 1].set_frame_on(False)
                

            elif auxiliar == "time":
                ax_spectrogram = axs[2] if waveforme else axs[1]
                ax_waveforme = axs[0]
                ax_freq_aux = axs[0]
                ax_time_aux = axs[1] if waveforme else axs[0]

            elif auxiliar == "both":
                ax_spectrogram = axs[2, 0] if waveforme else axs[1, 0]
                ax_waveforme = axs[0, 0] if waveforme else axs[0, 0] # dudas
                ax_freq_aux = axs[2, 1] if waveforme else axs[1, 1]
                ax_time_aux = axs[1, 0] if waveforme else axs[0, 0]
                ax_colorbar = axs[:, 0]

                if waveforme:
                  axs[0, 1].axis('off')
                  axs[1, 1].axis('off')
                  axs[1, 1].set_frame_on(False)
                else:
                    axs[0, 1].axis('off')
                    axs[0, 1].set_frame_on(False)
                
            elif auxiliar == "none":
                ax_spectrogram = axs[1] if waveforme else axs
                ax_waveforme = axs[0] if waveforme else axs
                ax_freq_aux = axs
                ax_time_aux = axs


            # ax_spectrogram = axs[2, 0]
            im = ax_spectrogram.imshow(
                obj.Sxx_dB,
                aspect='auto',
                origin='lower',
                extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                        obj.freq[0]*self.unit_scalar, obj.freq[-1]*self.unit_scalar]
            )

            ax_spectrogram.set_xlabel("Time (s)")
            ax_spectrogram.set_ylabel(f"Frequency ({self.unit})")
            plt.setp(ax_spectrogram.get_xticklabels(), visible=True)
            ax_spectrogram.set_xlim(obj.time[0]+obj.t0, obj.time[-1]+obj.t0)
            ax_spectrogram.set_ylim(ylim if ylim else (obj.freq[0]*self.unit_scalar, obj.freq[-1]*self.unit_scalar))
            
            lines = []
            handles_labels = []

            if ff:
                (line7, ) = ax_spectrogram.plot(
                    obj.time+obj.t0, obj.ff*self.unit_scalar, 
                    label="Fundamental", 
                    color=self._COLORS["fundamental"], 
                    marker='o', 
                    markersize=4, 
                    linestyle='None'
                )
                
                lines.append(line7)
                handles_labels.append(ax_spectrogram.get_legend_handles_labels())

            if mode == "max":
                x = obj.Sxx_ff_max
                y = obj.Sxx_time_max
            elif mode == "mean":
                x = obj.Sxx_ff_mean
                y = obj.Sxx_time_mean
            else:
                raise Exception("Mode must be 'max' or 'mean'.")

            
            if waveforme:
                (line1, ) = ax_waveforme.plot(obj.time_s+obj.t0, obj.s, label="Waveform", color=self._COLORS["waveforme"])
                (line2, ) = ax_waveforme.plot(obj.time_s+obj.t0, obj.envelope, label="Envelope", color=self._COLORS["envelope"])

                lines.append(line1)
                lines.append(line2)
                handles_labels.append(ax_waveforme.get_legend_handles_labels())

                try:
                    (line3, ) = ax_waveforme.plot(obj.time_s+obj.t0, obj.time_s.size*[obj.threshold_1], label="Threshold 1", color=self._COLORS["threshold_1"], linestyle='--')
                    lines.append(line3)
                    handles_labels.append(ax_waveforme.get_legend_handles_labels())
                except AttributeError:
                    warnings.warn("Threshold_1 not found in the object. Skipping threshold line.")

                ax_waveforme.set_ylabel("Amplitude\n(a.u.)")
                ax_waveforme.set_frame_on(False)
                plt.setp(ax_waveforme.get_xticklabels(), visible=False)
                ax_waveforme.sharex(ax_spectrogram)
            
            if auxiliar == "freq":
                (line6, ) = ax_freq_aux.plot(x, obj.freq*self.unit_scalar, label=f"Frequency {mode.capitalize()}", color=self._COLORS["freq_aux"])
                
                lines.append(line6)
                handles_labels.append(ax_freq_aux.get_legend_handles_labels())

                ax_freq_aux.set_frame_on(False)
                ax_freq_aux.set_xlabel("SPL (dB)")
                ax_freq_aux.sharey(ax_spectrogram)
                plt.setp(ax_freq_aux.get_yticklabels(), visible=False)

            elif auxiliar == "time":
                try:
                    (line4, ) = ax_time_aux.plot(
                        obj.time_s+obj.t0,
                        obj.time_s.size*[obj.threshold_2],
                        label="Threshold 2",
                        color=self._COLORS["threshold_2"],
                        linestyle='--'
                    )
                    lines.append(line4)
                    handles_labels.append(ax_time_aux.get_legend_handles_labels())
                except AttributeError:
                    pass
                
                (line5, ) = ax_time_aux.plot(obj.time+obj.t0, y, label=f"Time {mode.capitalize()}", color=self._COLORS["time_aux"])
                
                lines.append(line5)
                handles_labels.append(ax_time_aux.get_legend_handles_labels())

                ax_time_aux.set_frame_on(False)
                ax_time_aux.set_ylabel("SPL (dB)")
                ax_time_aux.sharex(ax_spectrogram)
                plt.setp(ax_time_aux.get_xticklabels(), visible=False)

                # if waveforme:
                #     ax_waveforme.yaxis.set_label_position("right")
                #     ax_waveforme.yaxis.tick_right()
            elif auxiliar == "both":
                (line6, ) = ax_freq_aux.plot(x, obj.freq*self.unit_scalar, label=f"Frequency {mode.capitalize()}", color=self._COLORS["freq_aux"])
                
                lines.append(line6)
                handles_labels.append(ax_freq_aux.get_legend_handles_labels())
            
                ax_freq_aux.set_frame_on(False)
                ax_freq_aux.set_xlabel("SPL (dB)")
                ax_freq_aux.sharey(ax_spectrogram)
                plt.setp(ax_freq_aux.get_yticklabels(), visible=False)

                try:
                    (line4, ) = ax_time_aux.plot(
                        obj.time_s+obj.t0,
                        obj.time_s.size*[obj.threshold_2],
                        label="Threshold 2",
                        color=self._COLORS["threshold_2"],
                        linestyle='--'
                    )
                    lines.append(line4)
                except AttributeError:
                    pass
                
                (line5, ) = ax_time_aux.plot(obj.time+obj.t0, y, label=f"Time {mode.capitalize()}", color=self._COLORS["time_aux"])
                
                lines.append(line5)
                handles_labels.append(ax_time_aux.get_legend_handles_labels())

                ax_time_aux.set_frame_on(False)
                ax_time_aux.set_ylabel("SPL (dB)")
                ax_time_aux.sharex(ax_spectrogram)
                plt.setp(ax_time_aux.get_xticklabels(), visible=False)
                
            # fig.colorbar(im, ax=axs[2, 0], label="Amplitude")
            # Place the colorbar outside the plots, on the right side
            # (left, bottom, width, height)
            cax = plt.axes(colorbar_pos)
            cax.set_title("SLP (dB)", fontsize=10, pad=10, loc='center', x=0.75)
            fig.colorbar(
                im,
                ax=ax_colorbar,
                # label="SLP (dB)",
                # location='right',
                # pad=0.02,
                # aspect=30,
                # fraction=0.07,
                cax=cax
            )

            # Hide the border and ticks of the axes at position (0, 1)
            
            # ax_freq_aux.set_yticks([])
            ax_flaten = axs.flat if isinstance(axs, np.ndarray) else [axs]
            for ax in ax_flaten:
                ax.grid(grid, linestyle='--', alpha=0.5)

            
            #  pickable labels
            # try:
            #     lines = [line1, line2, line3, line5, line6]
            # except:
            #     lines = [line1, line2, line5, line6]
            # try:
            #     lines.insert(3, line4)
            # except: pass

            # if ff:
            #     lines.insert(4, line7)
            
            # handles_labels = [ax.get_legend_handles_labels() for ax in axs.flat]            
            leg = self.pickable_legend(handles_labels, lines, fig)

            plt.suptitle(f"Spectrogram of {obj.file_id}", x=0.6, y=0.99, fontsize=12)
            fig.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.2, wspace=0.1, hspace=0.1)
            
            if click == "time":
                ax20 = ax_spectrogram.twinx()
                ax20.set_yticks([])
                clicker = self.klicker(fig, ax20, legend_bbox=(1.3, 0.35), settings=self._CLICKER_TIME_SETTINGS)
                clicker._leg.set_title("Clicker: ", prop={'weight': 'bold', "size": 10})

                leg.set_bbox_to_anchor((0.5, 0.0))

                return clicker
            elif click == "multiple":
                ax20 = ax_spectrogram.twinx()
                ax20.set_yticks([])
                clicker = self.klicker(fig, ax20, legend_bbox=(1.25, 0.45), settings=self._CLICKER_DATA_SETTINGS)
                clicker._leg.set_title("Clicker: ", prop={'weight': 'bold', "size": 10})

                leg.set_bbox_to_anchor((0.5, 0.0))
                fig.subplots_adjust(right=0.825)

                return clicker
            elif click == "custom":
                pass
            elif click == "none":
                pass
            else:
                raise Exception("Possible options: time, multiple, custom or none.")
            
            if not(legend):
                leg.remove()
            # fig.tight_layout()
            plt.show()

            return fig
    #%%
    def metrics(
        self,
        obj: Syllable,  # Union[Syllable,Song],
        obj_synth: Synthetic,  # Union[Syllable,Song],
        figsize: tuple[float, float] = (11, 8),
        ylim: tuple[float, float] = (0, 10),
        save: bool = True,
        grid: bool = True,
        show: bool = True,
    ) -> Figure:
        """


        Parameters
        ----------
            obj : Syllable | Song

            obj_synth : Syllable | Song

            figsize : tuple = (10,10)
                Size of the figure (width, height)
            ylim : tuple = ()
                Frequnecy range
            save : bool = True
                Flag to save plot
            show : bool = True
                Flag to display plot

        Return
        ------
            None

        Example
        -------
            >>>
        """
        plt.close()

        ticks = FuncFormatter(lambda x, pos: f"{x*1e-3:g}")
        ticks_x = FuncFormatter(lambda x, pos: f"{x:.2g}")

        fig: Figure = plt.figure(constrained_layout=False, figsize=figsize)
        gs = fig.add_gridspec(
            nrows=7,
            ncols=5,
            wspace=0.1,
            hspace=0.3,
            left=0.06,
            top=0.925,
            right=0.85,
            bottom=0.15,
        )
        # vmin, vmax = obj.Sxx_dB.min(), obj.Sxx_dB.max()
        # --------------- scores: FF and SCI ---------------------------------
        max_error = 100 * max(obj_synth.deltaFF.max(), obj_synth.deltaSCI.max())

        ax1: Axes = fig.add_subplot(gs[:2, :])
        (line1, ) = ax1.plot(
            obj_synth.time,
            100 * obj_synth.deltaFF,
            "*-",
            color="k",
            ms=5,
            lw=1,
            alpha=0.8,
            label=self._LABELS["ff"] + str(round(100 * obj_synth.deltaFF_mean, 2)),
        )
        (line2, ) = ax1.plot(
            obj_synth.time,
            100 * obj_synth.deltaSCI,
            "*-",
            color="purple",
            ms=5,
            lw=1,
            alpha=0.8,
            label=self._LABELS["sci"] + str(round(100 * obj_synth.deltaSCI_mean, 2)),
        )
        # ax1.legend(bbox_to_anchor=(1.235, 1.05), borderpad=0.6, labelspacing=0.7)
        ax1.xaxis.set_major_formatter(ticks_x)
        ax1.set_xlim((obj_synth.time[0], obj_synth.time[-1]))
        ax1.set_ylabel("Relative Error (%)")
        ax1.set_xlabel("")
        ax1.set_ylim((0, 1.25 * max_error))

        handles_labels = [ax1.get_legend_handles_labels()]
        leg0 = self.pickable_legend(handles_labels, [line1, line2], fig, ncol = 1,
                                   bbox_to_anchor=(1.0, 0.9), loc="upper right", title="Data:")

        # ------------------ spectrum ---------------
        ax2: Axes = fig.add_subplot(gs[2:5, :], sharex=ax1)

        img = Specshow(
            obj.Sxx_dB,
            x_axis="s",
            y_axis="linear",
            sr=obj.sr,
            hop_length=obj.hop_length,
            ax=ax2,
            cmap=self._COLORS["spectrum1"],
        )
        
        (line3, ) = ax2.plot(obj.time, obj.ff, "b*-", label=r"real", ms=7)
        (line4, ) = ax2.plot(obj_synth.time, obj_synth.ff, "go-", label=r"synth", ms=3)

        handles_labels = [ax2.get_legend_handles_labels()]
        leg1 = self.pickable_legend(handles_labels, [line3, line4], fig, ncol = 1,
                                   bbox_to_anchor=(0.85, 0.695), loc="upper right", title="")
        
        # ax2.legend(borderpad=0.6, labelspacing=0.7)
        ax2.yaxis.set_major_formatter(ticks)
        ax2.xaxis.set_major_formatter(ticks_x)
        ax2.set_xlim((obj.time[0], obj.time[-1]))
        ax2.set_ylim(obj.flim)
        ax2.set_ylabel("Frequency (kHz)")
        ax2.set_xlabel("")
        # ------------------ SCI -------------------------
        ax31: Axes = fig.add_subplot(gs[5:7, :], sharex=ax2)
        ax31.set_ylabel(r"Similarity (dl)")
        ax31.set_xlabel("Time (s)")
        # --------------- acousitcal features ----------------------
        ax32 = ax31.twinx()
        assert isinstance(ax32, Axes)
        lr = ax32.plot(
            obj.time,
            obj.SCI,
            "b*-",
            ms=7,
            label=self._LABELS["lr"] + str(round(obj.SCI.mean(), 2)),
        )
        ls = ax32.plot(
            obj.time,
            obj_synth.SCI,
            "go-",
            ms=5,
            alpha=0.8,
            label=self._LABELS["ls"] + str(round(obj_synth.SCI.mean(), 2)),
        )
        lh = ax31.plot(
            obj.time,
            obj_synth.Df,
            "H",
            ms=3,
            label=self._LABELS["lh"] + str(round(obj_synth.Df.mean(), 2)),
        )
        lskl = ax31.plot(
            obj.time,
            obj_synth.SKL,
            "s",
            color="purple",
            ms=3,
            label=self._LABELS["lskl"] + str(round(obj_synth.SKL.mean(), 2)),
        )
        correlation_synth = obj_synth.correlation.mean()
        lc = ax31.plot(
            obj.time,
            obj_synth.correlation,
            "p",
            ms=3,
            label=self._LABELS["lc"] + str(round(correlation_synth, 2)),
        )
        lns = lr + ls + lh + lskl + lc
        # labs = [l.get_label() for l in lns]
        handles_labels = [ax.get_legend_handles_labels() for ax in [ax32, ax31]]
        leg2 = self.pickable_legend(handles_labels, lns, fig)
        # ax32.legend(
        #     lns,
        #     labs,
        #     bbox_to_anchor=(1.3, 1),
        #     title="Acoustical Features",
        #     title_fontproperties={"weight": "bold"},
        # )
        ax32.set_ylabel("SCI (dl)")
        ax32.set_ylim((0, 5))

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax32.get_xticklabels(), visible=True)

        cbar_ax = fig.add_axes([0.875, 0.38, 0.02, 0.315]) # type: ignore
        clb = fig.colorbar(img, cax=cbar_ax)
        clb.set_label(self._LABELS["power"], labelpad=10, y=0.5, fontsize=10, rotation=90)
        
        for ax in [ax1, ax2, ax31, ax32]:
            ax.grid(grid, linestyle='--', alpha=0.5)

        # fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.25, wspace=0.1, hspace=0.1)

        if obj.type!="":
            suptitle = f"Scoring Variables\n{self._suptitle(obj)}"
            gs.update(top=0.9)
        else:
            suptitle = f"Scoring Variables: {self._suptitle(obj)}"

        fig.suptitle(
            suptitle,
            fontsize=self.title_font["size"],
            y=0.99,
            fontweight="bold",
        )

        if save:
            img_name = f"{self._save_name(obj)}-ScoringVariables.png"
            fig.savefig(
                obj.proj_dirs.images / img_name,
                transparent=True,
                bbox_inches="tight",
            )
            print(f"Image save at {img_name}")

        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    #%%
    def alpha_beta(
        self,
        obj: Synthetic,
        xlim: tuple[float, float] = (-0.05, 0.2),
        ylim: tuple[float, float] = (-0.2, 0.9),
        figsize: tuple[float, float] = (10, 6),
        save: bool = True,
        show: bool = True,
        # over_sample_mg: int = 100,
    ) -> Figure:
        """


        Parameters
        ----------
            obj : Syllabe|Song
                Song or Syllable to be displayed
            xlim : tuple = (-0.05,.2)
                Time range
            ylim : tuple = (-0.2,0.9)
                Frequency range
            figsize : tuple = (10,6)
                Fogure size (width, height)
            save : bool = True
                Enable save plot
            show : bool = True
                Enable display plot 

        Return
        ------
            None

        Example
        -------
            >>>
        """
        # if not "synth" in obj.id:
        #     raise Exception("This  is not a synthetic syllable, remember create"
        #                     + " a synthetic file using the funcion bs.Solve().")
        
        plt.close()

        if obj.alpha.max() > 0.2: xlim = (-0.05, 1.1 * obj.alpha.max())
        if obj.beta.max() > 0.9: ylim = (-0.2, 1.1 * obj.beta.max())

        tlim = (obj.time_s[0], obj.time_s[-1])
        t_tick = np.linspace(round(obj.time_s[0],1), round(obj.time_s[-1],1), 7)
        color = np.linspace(obj.time_s[0], obj.time_s[-1], round(obj.time_s.shape[0],1)//self.over_sample_mg)

        # viridis = mpl.colormaps[cmap]
        # c = viridis(np.linspace(0.3, 1, np.size(obj.time_s[::self.over_sample_mg])))

        fig = plt.figure(figsize=figsize)
        gs = GridSpec(2, 2, figure=fig, width_ratios=[1, 1.3], height_ratios=[1.2, 2])

        # fig.tight_layout(pad=3.0)
        gs.update(left=0.075, right=0.935, top=0.875, bottom=0.2,
                    wspace=0.1, hspace=0.3)

        # alpha axis
        ax_alpha = fig.add_subplot(gs[0, 0])
        # ax_alpha.scatter(obj.time_s[::self.over_sample_mg], obj.alpha[::self.over_sample_mg], c=c, label="alfa")
        _ = self.colored_line(obj.time_s[::self.over_sample_mg], obj.alpha[::self.over_sample_mg],
                             color, ax_alpha, linewidth=5, cmap=self._COLORS["motor_gesture"], label="alpha")
        ax_alpha.set_title("Air-Sac Pressure")
        ax_alpha.set_ylabel("α (a.u.)")
        ax_alpha.set_ylim(xlim)
        ax_alpha.set_xticks(t_tick)
        ax_alpha.set_xticklabels([f"{tick:.2f}" for tick in t_tick])
        ax_alpha.set_xlim(tlim)
        ax_alpha.grid()

        # beta axis
        ax_beta = fig.add_subplot(gs[1:, 0])
        # ax_beta.scatter(obj.time_s[::self.over_sample_mg], obj.beta[::self.over_sample_mg], c=c, label="beta")
        _ = self.colored_line(obj.time_s[::self.over_sample_mg], obj.beta[::self.over_sample_mg], color, ax_beta,
                             linewidth=5, cmap=self._COLORS["motor_gesture"], label="beta")
        ax_beta.set_title("Labial Tension")
        # ax_beta.set_xlabel("Time (s)")
        ax_beta.set_ylabel("β (a.u.)")
        ax_beta.set_ylim(ylim)
        ax_alpha.set_xlim(tlim)
        ax_beta.sharex(ax_alpha)
        ax_beta.set_xticks(t_tick)
        ax_beta.set_xticklabels([f"{tick:.2f}" for tick in t_tick])
        ax_beta.grid()

        # ------------- Bogdanov–Takens bifurcation ------------------
        ax_mg = fig.add_subplot(gs[:, 1])
        line1 = ax_mg.plot(-1 / 27, 1 / 3, "ko", label="Cuspid Point")
        line2 = ax_mg.axvline(0, color="red", lw=1, linestyle="--", label="Hopf")  # , label="Hopf Bifurcation")
        # ax_mg.scatter(obj.alpha[::self.over_sample_mg], obj.beta[::self.over_sample_mg], c=c, marker="_", label="Motor Gesture")
        line3 = self.colored_line(obj.alpha[::self.over_sample_mg], obj.beta[::self.over_sample_mg], color, ax_mg,
                             linewidth=5, cmap=self._COLORS["motor_gesture"], label="motor gesture")
        # label="Saddle-Noddle\nBifurcation"
        line4 = ax_mg.plot(obj.mu1_curves[0], obj.beta_bif, "-g", lw=1, label="SN curve 1")
        line5 = ax_mg.plot(obj.mu1_curves[1], obj.beta_bif, "-g", lw=1, label="SN curve 2")
        _ = ax_mg.fill_between(
            obj.mu1_curves[1],
            obj.beta_bif,
            10,
            where=obj.mu1_curves[1] > 0,
            color="gray",
            alpha=0.2,
        )
        
        ax_mg.text(-0.01, 0.6, "Hopf", rotation=90, color="r")
        ax_mg.text(-0.0425, 0.37, "CP", rotation=0, color="k")
        ax_mg.text(-0.0275, 0.15, "SN", rotation=0, color="g")
        ax_mg.text(0.1, 0.005, "SN", rotation=0, color="g")
        ax_mg.set_ylabel("β (a.u.)")
        ax_mg.set_xlabel("α (a.u.)")
        ax_mg.set_title("Parameter Space")
        ax_mg.yaxis.tick_right()
        ax_mg.yaxis.set_label_position("right")
        ax_mg.set_xlim(xlim)
        ax_mg.set_ylim(ylim)
        # ax_mg.sharey(ax_beta)
        # ax_mg.legend()

        # Add a colorbar below the plot at position (1, 0)
        divider = make_axes_locatable(ax_beta)
        cax = divider.append_axes("bottom", size="8%", pad=0.4, anchor='C')
        cb = fig.colorbar(line3, cax=cax, orientation='horizontal')
        cb.set_label("Time (s)")

        
        # Collect all handles and labels from all axes
        handles_labels = [ax_mg.get_legend_handles_labels()]
        lines = line1 + [line2] + [line3] + line4 + line5
        leg = self.pickable_legend(handles_labels, lines, fig)
        
        
        suptitle = (
            f"Motor Gesture Curves\n{self._suptitle(obj)}"
            if (obj.type != "")
            else f"Motor Gesture Curves: {self._suptitle(obj)}"
        )
        # fig.tight_layout()
        plt.suptitle(
            suptitle,
            fontsize=self.title_font["size"],
            y=0.99,
            fontweight="bold",
        )
        
        if save:
            save_name = f"{self._save_name(obj)}-mg_params.png"
            fig.savefig(
                obj.proj_dirs.images / save_name,
                transparent=True,
                bbox_inches="tight",
            )
            print(f"Image save at {save_name}")

        if show:
            plt.show()
        else: plt.close()

        return fig

    #%%
    def segmentation(
        self,
        obj,
        harmonics: bool = False,
        fundamental: bool = False,
        alpha: float = 0.9,
        grid: bool = False,
        colorbar: bool = True,
        filters: bool = True,
        figsize: tuple[float, float] = (9, 7),
        label: Literal["syllables", "vocalizations"] = "syllables",
    ) -> Figure:
        """_summary_

        Args:
            obj (_type_): _description_
            harmonics (bool, optional): _description_. Defaults to False.
            fundamental (bool, optional): _description_. Defaults to False.
            alpha (float, optional): _description_. Defaults to 0.9.
            grid (bool, optional): _description_. Defaults to False.
            colorbar (bool, optional): _description_. Defaults to True.
            filters (bool, optional): _description_. Defaults to True.
            figsize (Tuple[float, float], optional): _description_. Defaults to (9, 7).
            label (Literal[&quot;segments&quot;, &quot;individual&quot;], optional): _description_. Defaults to "syllables".

        Returns:
            Figure: _description_
        """
        plt.close()

        shape = (2,3) if filters else (1,3)
        fig, axs = plt.subplots(
            ncols=shape[0], nrows=shape[1],
            figsize=figsize,
            sharex=True,
            sharey=True,
            # gridspec_kw={'width_ratios': [6, 1], 'height_ratios': [3, 1, 6]}
        )
        plt.subplots_adjust(hspace=0.2, wspace=0.05, top=0.88, left=0.07, right=1, bottom=0.15)

        if filters:
            ax_spectrogram = axs[0, 0]
            ax_harmonics = axs[1, 0]
            ax_labels = axs[2, 0]
            ax_mask_1 = axs[0, 1]
            ax_mask_2 = axs[1, 1]
            ax_final_mask = axs[2, 1]
            
        else:
            ax_spectrogram = axs[0]
            ax_harmonics = axs[1]
            ax_labels = axs[2]
            ax_mask_1 = axs[0]
            ax_mask_2 = axs[1]
            ax_final_mask = axs[1]
            plt.subplots_adjust(hspace=0.3)
        # Original spectrogram
        im0 = ax_spectrogram.imshow(
            obj.Sxx_dB,
            aspect='auto',
            origin='lower',
            extent=[
                obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                obj.freq[0]*1e-3, obj.freq[-1]*1e-3
            ],
        )
        ax_spectrogram.set_title("Original Spectrogram (dB)")
        # ax_spectrogram.set_ylabel("Frequency (kHz)")
        ax_spectrogram.set_xlim(obj.time[0]+obj.t0, obj.time[-1]+obj.t0)
        ax_spectrogram.set_ylim(obj.freq[0]*1e-3, obj.freq[-1]*1e-3)

        # Harmonic Mask
        im1 = ax_harmonics.imshow(
            2*obj.harmonics_rois.astype(int), # all_mask, # harmonics_rois,
            aspect='auto',
            origin='lower',
            # label="Harmonics Mask",
            alpha=0.8,
            extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                    obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
        )

        im11 = ax_harmonics.imshow(
            obj.mask.astype(int), # harmonics_rois,
            aspect='auto',
            origin='lower',
            alpha=0.7,
            # label="Fundamental Mask",
            extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                    obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
        )
        # Add legend to the plot at the right top corner
        handles = [
            Patch(facecolor='goldenrod', edgecolor='goldenrod', alpha=0.7, label='Harmonics'),
            Patch(facecolor='gold', edgecolor='gold', alpha=0.8, label='Fundamental')
        ]

        # leg = self.pickable_legend(self, handles, lines, fig,
        #     loc='lower center',
        #     bbox_to_anchor=(0.5, 0.),
        #     ncol=5, title="Elements:",
        # )
        ax_harmonics.legend(handles=handles, loc='upper right', fontsize=8, frameon=True)

        if fundamental:
            ax_harmonics.scatter(
            obj.time+obj.t0,
            obj.ff_sp*1e-3,
            color='red',
            label="Fundamental",
            marker="p",
            s=5,  # Marker size
            )
        if harmonics:
            for i in range(len(obj.harmonics)):
                ax_harmonics.scatter(
                    obj.time+obj.t0,
                    obj.harmonics[i]*1e-3,
                    color=str(i / (len(obj.harmonics)-1)) if len(obj.harmonics) > 1 else "0.0",
                    marker="p",
                    s=5,  # Marker size
                    label=f"Harmonic {i+1}"
                )
        ax_harmonics.set_ylabel("Frequency (kHz)")
        ax_harmonics.set_title("Final Mask (Fundamental + Harmonics)")

        # Harmonic Mask Final
        cmap = plt.get_cmap(self._COLORS["syllable_labels"])  # define the colormap
        cmap_grayscale = plt.get_cmap('Grays')  # define the colormap
        labels = obj.syllables if label == "syllables" else obj.vocalizations
        
        im31 = ax_labels.imshow(
            obj.Sxx_dB,
            # obj.harmonic_mask_final,
            aspect='auto',
            origin='lower',
            cmap=cmap_grayscale,
            alpha=0.9,
            extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                    obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
        )
        im3 = ax_labels.imshow(
            labels, # labels, #
            # obj.harmonic_mask_final,
            aspect='auto',
            origin='lower',
            cmap=cmap,
            alpha=0.4,
            extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                    obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
        )

        # # divider = make_axes_locatable(ax_labels)
        global cax
        cax = None

        if colorbar:
            num_features = obj.num_syllables if label == "syllables" else obj.vocalizations
            
            cmaplist = [cmap(i) for i in range(cmap.N)]
            # cmaplist[-1] = [1, 0, 0, 1] # convert to red

            cmaplist[0] = (.5, .5, .5, 1.0)

            bounds = np.arange(0, num_features + 1)  # linspace(0, 20, 21)
            norm_cb = colors.BoundaryNorm(bounds, cmap.N)

            cmap = colors.LinearSegmentedColormap.from_list('Custom cmap', cmaplist, cmap.N)
            colorbar_axis = [0.2, 0.03, 0.7, 0.02]
            cax = fig.add_axes(colorbar_axis)  # type: ignore

            # Remove the custom cax and add the colorbar to the bottom of the figure
            cbar = ColorbarBase(cax, cmap=cmap, norm=norm_cb,
                                spacing='proportional',
                                ticks=bounds, boundaries=bounds,
                                orientation='horizontal',
                                label='Label')  # Set the label for the colorbar

            cbar.set_label('Label:', labelpad=-27, x=-0.05, y=-0.9, va='top', weight='bold')
        # legend_elements = [
        #     Patch(facecolor='blue', edgecolor='blue', alpha=0.9, label='Harmonic Mask'),
        #     Patch(facecolor='orange', edgecolor='orange', alpha=0.9, label='Harmonic Margin Mask')
        # ]
        # ax_labels.legend(handles=legend_elements, loc='upper right')


        ax_labels.set_title(f"Labeled Vocalizations: {obj.num_vocalizations - 1}")
        # ax_labels.set_ylabel("Frequency (kHz)")
        ax_labels.set_xlabel("Time (s)")

        if filters:
            # Median clipping filter
            im4 = ax_mask_1 = axs[0, 1].imshow(
                obj.mask_1,
                aspect='auto',
                origin='lower',
                extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                                    obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
            )
            ax_mask_1 = axs[0, 1].set_title("Median Clipping Filter")

            # Percentile filter
            im5 = ax_mask_2.imshow(
                obj.mask_2,
                aspect='auto',
                origin='lower',
                extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                                    obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
            )
            ax_mask_2.set_title("Percentile Filter")


            # Post Processing
            im6 = ax_final_mask.imshow(
                obj.mask_pre_proc, # mask, # * obj.Sxx_dB,
                aspect='auto',
                origin='lower',
                extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                        obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
            )
            # ax_final_mask.plot(obj.time+obj.t0, obj.ff*1e-3, color='black', lw=1, label="Fundamental Frequency")
            ax_final_mask.set_xlabel("Time (s)")

            ax_final_mask.set_title("Median Clipping Filter AND Percentile Filter")
        else:
            # ax_labels.set_xlabel("Time (s)", x=0.9, y=0.1)
            pass

        def update_label(change):
            global cax
            # global label, ax_labels, cbar, cax, fig, grid
            label = change['new']
            ax_labels.clear()
            cmap = plt.get_cmap(self._COLORS["syllable_labels"])
            
            labels_data = obj.syllables if label == "syllables" else obj.vocalizations
            
            im31 = ax_labels.imshow(
                obj.Sxx_dB,
                aspect='auto',
                origin='lower',
                cmap=cmap_grayscale,
                alpha=0.95,
                extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                        obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
            )
            im3 = ax_labels.imshow(
                labels_data, # labels, #
                aspect='auto',
                origin='lower',
                cmap=cmap,
                alpha=0.4,
                extent=[obj.time[0]+obj.t0, obj.time[-1]+obj.t0,
                        obj.freq[0]*1e-3, obj.freq[-1]*1e-3]
            )

            ax_labels.set_title(f"Labeled Vocalizations: {obj.num_vocalizations}" if label == "vocalizations" else f"Labeled Syllables: {obj.num_syllables}")
            ax_labels.set_xlabel("Time (s)")
            ax_labels.grid(grid)
            # Recalculate colorbar
            num_features = obj.num_syllables if label == "syllables" else obj.num_vocalizations
            # num_features += 1
            
            cmaplist = [cmap(i) for i in range(cmap.N+1)]
            
            # cmaplist[-1] = [1, 0, 0, 1] # convert to red
            cmaplist[0] = (.5, .5, .5, 1.0)
            bounds = np.arange(0, num_features + 1)
            norm_cb = colors.BoundaryNorm(bounds, cmap.N+1)
            # cmap_new = colors.LinearSegmentedColormap.from_list('Custom cmap', cmaplist, cmap.N)
            # Remove previous colorbar if exists
            
            if cax is not None and cax in fig.axes:
                fig.delaxes(cax)

            cax = fig.add_axes(colorbar_axis)  # type: ignore
            # Remove the custom cax and add the colorbar to the bottom of the figure
            cbar = ColorbarBase(cax, cmap=cmap, norm=norm_cb,
                                spacing='proportional',
                                ticks=bounds, boundaries=bounds,
                                orientation='horizontal',
                                label='Label')  # Set the label for the colorbar

            cbar.set_label('Label:', labelpad=-27, x=-0.05, y=-0.9, va='top', weight='bold')
            # fig.canvas.draw_idle()
            # display(fig)

        if not fundamental and not harmonics:
            label_selector = widgets.ToggleButtons(
                options=['syllables', "vocalizations"],
                value=label,
                # description='Label type:',
                disabled=False,
                button_style='',
                layout=widgets.Layout(justify_content='flex-start', width='auto')
            )
            label_selector.style.button_width = '120px'
            label_selector.style.description_width = '70px'
            label_selector.style.flex_flow = 'row'
            label_selector.style.align_items = 'center'
            label_selector.style.display = 'flex'
            label_selector.style.margin = '0 0 0 0'

            container = widgets.HBox(
                [
                    widgets.HTML("<b>Labaling:</b>", layout=widgets.Layout(width='80px')),
                    label_selector
                ],
                layout=widgets.Layout(align_items='center'))

            display(container)
            label_selector.observe(update_label, names='value')

        for ax in axs.flat:
            ax.grid(grid)

        fig.suptitle(f"Image Processing Segmentation of {obj.file_id} ({obj.tlim[0]}s - {obj.tlim[1]}s)", fontsize=16, fontweight='bold')

        # fig.show()

        return fig
    #%%
    def physical_variables(
        self,
        obj: Synthetic,
        xlim: tuple[float, float] = (0, 1000),
        figsize: tuple[float, float] = (10, 6),
        save: bool = False,
        show: bool = True,
        grid: bool = False,
        oversampling: int = 10,
    ) -> Figure:
        """


        Parameters
        ----------
            obj : Syllabe|Song
                Song or Syllable to be displayed
            xlim : tuple = (-0.05,.2)
                Time range
            figsize : tuple = (10,6)
                Fogure size (width, height)
            save : bool = True
                Save plot
            show : bool = True
                Display plot

        Return
        ------
            files_names : list
                List with the audios files names

        Example
        -------
            >>>
        """
        if not "synth" in obj.id:
            raise Exception("This  is not a synthetic syllable, remember create"
                            + " a synthetic file using the funcion bs.Solve().")
        
        plt.close()

        fig, axs = plt.subplots(2, 2, figsize=figsize, sharex=True)

        plt.subplots_adjust(
            hspace=0.25, wspace=0.2, top=0.825, bottom=0.2, left=0.075, right=0.99
        )

        ax_labial_displacement = axs[0, 0]
        ax_trachea_input = axs[0, 1]
        ax_trachea_output = axs[1, 1]
        ax_labial_velocity = axs[1, 0]

        (line1, ) = ax_labial_displacement.plot(obj.times_vs[::oversampling], obj.vs[::oversampling, 0], color="r", label="Labia Displacement")
        ax_labial_displacement.set_title(r"Labial Walls Displacement")
        ax_labial_displacement.set_ylabel("$x(t)$")
        ax_labial_displacement.set_xlim(xlim)

        (line2, ) = ax_trachea_input.plot(obj.times_vs[::oversampling], obj.vs[::oversampling, 1], color="g", label="Trachea Input")
        ax_trachea_input.set_ylabel("$p_{in}$")
        ax_trachea_input.set_title(r"Trachea Input Pressure")

        (line3, ) = ax_labial_velocity.plot(obj.times_vs[::oversampling], obj.vs[::oversampling, 0], color="m", label="Labia Velocity")
        ax_labial_velocity.set_ylabel("$y(t)$")
        ax_labial_velocity.set_title(r"Labial Walls Velocity")
        ax_labial_velocity.set_xlabel("Time (s)")

        (line4, ) = ax_trachea_output.plot(obj.times_vs[::oversampling], obj.vs[::oversampling, 4], color="b", label="Trachea Output")
        ax_trachea_output.set_ylabel("$p_{out}$")
        ax_trachea_output.set_title(r"Trachea Output Pressure")
        ax_trachea_output.set_xlabel("Time (s)")

        lines = [line1, line2, line3, line4]
        handles_labels = [ax.get_legend_handles_labels() for ax in axs.flat]
        leg = self.pickable_legend(handles_labels, lines, fig)

        leg.set_bbox_to_anchor((0.5, 0.0))

        if obj.type!="":
            plt.subplots_adjust(top=0.8)
            suptitle = f"Physical Model Variables\n{self._suptitle(obj)}"
        else:
            suptitle = f"Physical Model Variables: {self._suptitle(obj)}"

        fig.suptitle(
            suptitle,
            fontsize=self.title_font["size"],
            y=0.99,
            fontweight=self.title_font["weight"],
        )
        # fig.tight_layout()
        for ax in axs.flat:
            ax.grid(grid)
            ax.ticklabel_format(axis="y", style="scientific", scilimits=(-1, 1))
            # ax.set_xlim(xlim)

        if save:
            image_text = f"{self._save_name(obj)}-PhysicalVariables.png"
            fig.savefig(
                obj.proj_dirs.images / image_text,
                transparent=True,
                bbox_inches="tight",
            )
            print(f"Image save at {image_text}")
        if show:
            plt.show

        return fig
# # %%
# def spectrogram_data(
#     syllable: Syllable,
#     ff_on: bool = False,
#     tlim: Optional[Tuple[float, float]] = None,
#     figsize: Tuple[float, float] = (10, 6),
#     ms: int = 7,
#     labels: List[str] =_LABELS,
#     colors: List[str] =_COLORS,
#     markers: List[str] =_MARKERS,
# ) -> clicker:
#     """


#     Parameters
#     ----------
#         obj : Syllabe|Song
#             Song or Syllable to be displayed
#         syllable: Syllable|None = None,

#         chunck: Any|None = None,

#         ff_on: bool =False,

#         select_time: bool = False,

#         tlim : tuple = (-0.05,.2)
#             Time range
#         figsize : tuple = (10,6)
#             Fogure size (width, height)
#         save : bool = True
#             Save plot
#         show : bool = True
#             Display plot
#         ms : int = 7
#             Marker size

#     Return
#     ------
#         klicker : cliker
#             Clicker object with the points selected

#     Example
#     -------
#         >>>
#     """
#     ticks = FuncFormatter(lambda x, pos: f"{x*1e-3:g}")
#     ticks_x = FuncFormatter(lambda x, pos: f"{x+syllable.t0_bs:.2f}")

#     if tlim is None:
#         tlim = (syllable.time[0], syllable.time[-1])
#     else:
#         tlim = (tlim[0] - syllable.t0_bs, tlim[1] - syllable.t0_bs)

#     plt.close()
#     fig, ax = plt.subplots(1, 1, figsize=figsize)

#     img = Specshow(
#         syllable.Sxx_dB,
#         x_axis="s",
#         y_axis="linear",
#         sr=syllable.sr,
#         hop_length=syllable.hop_length,
#         ax=ax,
#         cmap=_CMAP,
#     )
#     ax.yaxis.set_major_formatter(ticks)
#     ax.xaxis.set_major_formatter(ticks_x)

#     if ff_on:
#         if syllable.ff_method in ("yin", "pyin", "imgpro"):
#             ax.plot(
#                 syllable.time, syllable.ff, "co", ms=ms, label=r"FF$_{yin}$"
#             )
#         elif syllable.ff_method == "both":
#             ax.plot(syllable.time, syllable.ff, "co", ms=ms, label=r"FF$_{pyin}$")
#             ax.plot(syllable.time, syllable.ff2, "b*", ms=ms, label=r"FF$_{yin}$")

#     ax.set_ylim(syllable.flim)
#     ax.set_xlim(tlim)
#     ax.set_ylabel("Frequency (kHz)")
#     ax.set_xlabel("Time (s)")
    
#     fig.suptitle(
#         "Waveform and Spectrogram",
#         fontsize=self.title_font["size"],
#         y=0.99,
#         fontweight="bold",
#     )
    
#     fig.tight_layout()
#     plt.subplots_adjust(
#             top=0.9, bottom=0.075, left=0.075, right=0.86
#     )

#     return klicker_multiple(fig, ax, 
#                             labels=labels,
#                             colors=colors,
#                             markers=markers)
# # %%
# def spectrogram_waveform(
#     obj: Any,  # Union[Syllable,Song],
#     syllable: Any | None = None,  # Optional[Syllable] = None,
#     chunck: Any | None = None,  # Optional[Syllable] = None,
#     ff_on: bool = False,
#     select_time: bool = False,
#     tlim: Optional[Tuple[float, float]] = None,
#     figsize: Tuple[float, float] = (10, 6),
#     save: bool = True,
#     show: bool = True,
#     ms: int = 7,
# ) -> clicker:
#     """


#     Parameters
#     ----------
#         obj : Syllabe|Song
#             Song or Syllable to be displayed
#         syllable: Syllable|None = None,

#         chunck: Any|None = None,

#         ff_on: bool =False,

#         select_time: bool = False,

#         tlim : tuple = (-0.05,.2)
#             Time range
#         figsize : tuple = (10,6)
#             Fogure size (width, height)
#         save : bool = True
#             Save plot
#         show : bool = True
#             Display plot
#         ms : int = 7
#             Marker size

#     Return
#     ------
#         klicker : cliker
#             Clicker object with the points selected

#     Example
#     -------
#         >>>
#     """
#     ticks = FuncFormatter(lambda x, pos: f"{x*1e-3:g}")
#     ticks_x = FuncFormatter(lambda x, pos: f"{x+obj.t0_bs:.2f}")

#     if tlim is None:
#         tlim = (obj.time[0], obj.time[-1])
#     else:
#         tlim = (tlim[0] - obj.t0_bs, tlim[1] - obj.t0_bs)

#     if syllable is None:
#         syllable_on = 0
#         ratios = [3, 8]
#     else:
#         syllable_on = 1
#         ratios = [1, 2, 1]
#         figsize = (10, 7)

#     plt.close()
#     # ----------------------- song -----------------------
#     if "song" == obj.metadata["id"]:
#         fig, ax = plt.subplots(
#             2 + int(syllable_on),
#             1,
#             gridspec_kw={"height_ratios": ratios},
#             figsize=figsize,
#             sharex=True,
#         )

#         syllables_array = np.ones(obj.time_s.size) * obj.umbral_FF

#         ax[0].plot(obj.time_s, obj.s, "k", label="waveform")
#         ax[0].plot(obj.time_s, syllables_array, "--", label="umbral")
#         ax[0].plot(obj.time_s, obj.envelope, label="envelope")
#         ax[0].legend(bbox_to_anchor=(1.01, 1.0))
#         ax[0].xaxis.set_major_formatter(ticks_x)
#         ax[0].set_ylabel("Amplitude (a.u)")
#         ax[0].set_xlabel("")

#         img = Specshow(
#             obj.Sxx_dB,
#             x_axis="s",
#             y_axis="linear",
#             sr=obj.sr,
#             hop_length=obj.hop_length,
#             ax=ax[1],
#             cmap=_CMAP,
#         )
#         if ff_on:
#             if obj.ff_method in ("yin", "pyin", "mmanual"):
#                 ax[1].plot(
#                     obj.time,
#                     obj.ff,
#                     "bo",
#                     ms=ms + 1,
#                     label=rf"FF$_{{obj.ff_method}}$",
#                 )
#             elif obj.ff_method == "both":
#                 ax[1].plot(
#                     obj.time, obj.ff, "co", ms=ms + 1, label=r"FF$_{pyin}$"
#                 )
#                 ax[1].plot(
#                     obj.time, obj.ff2, "b*", ms=ms + 1, label=r"FF$_{yin}$"
#                 )
#             ax[1].legend(bbox_to_anchor=(1.135, 1.02))

#         ax[1].set_ylim(obj.flim)
#         ax[1].set_xlim(tlim)
#         ax[1].yaxis.set_major_formatter(ticks)
#         ax[1].xaxis.set_major_formatter(ticks_x)
#         ax[1].set_ylabel("Frequency (kHz)")
#         ax[1].set_xlabel("Time (s)")

#         if syllable != None:
#             ax[1].plot(
#                 syllable.time + syllable.t0,
#                 syllable.ff,
#                 "b+",
#                 label="Syllable".format(syllable.sr),
#                 ms=6,
#             )

#             img = Specshow(
#                 syllable.Sxx_dB,
#                 x_axis="s",
#                 y_axis="linear",
#                 sr=syllable.sr,
#                 ax=ax[2],
#                 cmap=_CMAP,
#                 hop_length=syllable.hop_length,
#             )

#             syllable_info = f"{syllable.file_name}-{syllable.no_syllable}"
#             ax2_title = f"Single Syllable Spectrum\n{syllable_info}"
#             ax[2].plot(
#                 syllable.time, syllable.ff, "b+", label="Syllable", ms=15
#             )
#             ax[2].set_ylim(obj.flim)
#             ax[2].legend(loc="upper right", title="FF")
#             ax[2].set_xlabel("Time (s)")
#             ax[2].set_ylabel("f (khz)")
#             ax[2].set_title(ax2_title)
#             ax[2].yaxis.set_major_formatter(ticks)
#             ax[2].xaxis.set_major_formatter(ticks_x)

#             ax[1].legend(loc="upper right", title="FF")

#             img_text = f"{_save_name(obj)}SongAndSyllables.png"
#             path_save = obj.proj_dirs.IMAGES / img_text

#         else:
#             name = f"{obj.file_name[:-4]}-Song.png".replace(" ", "")
#             path_save = obj.proj_dirs.IMAGES / name

#         fig.suptitle(
#             f"Waveform and Spectrogram\n{obj.file_name}",
#             fontsize=self.title_font["size"],
#             y=0.99,
#             fontweight="bold",
#         )
#         plt.subplots_adjust(
#             wspace=0.1, hspace=0.1, top=0.875, bottom=0.075, left=0.075, right=0.85
#         )
#     # ----------------------------- syllable -----------------------------
#     elif "syllable" == obj.metadata["id"]:
#         fig, ax = plt.subplots(
#             2, 1,
#             gridspec_kw={"height_ratios": [3, 8]},
#             figsize=figsize,
#             sharex=True,
#         )

#         ax[0].plot(obj.time_s, obj.s, "k", label="waveform")
#         ax[0].plot(obj.time_s, obj.envelope, label="envelope")
#         ax[0].legend(bbox_to_anchor=(1.18, 1.0))
#         ax[0].xaxis.set_major_formatter(ticks_x)
#         ax[0].set_ylabel("Amplitude (a.u)")

#         img = Specshow(
#             obj.Sxx_dB,
#             x_axis="s",
#             y_axis="linear",
#             sr=obj.sr,
#             hop_length=obj.hop_length,
#             ax=ax[1],
#             cmap=_CMAP,
#         )
#         ax[1].yaxis.set_major_formatter(ticks)
#         ax[1].xaxis.set_major_formatter(ticks_x)

#         if ff_on:
#             if obj.ff_method in ("yin", "pyin", "manual"):
#                 ax[1].plot(
#                     obj.time, obj.ff, "co", ms=ms, label=r"FF$_{yin}$"
#                 )  # .format(obj.ff_method))
#             elif obj.ff_method == "both":
#                 ax[1].plot(obj.time, obj.ff, "co", ms=ms, label=r"FF$_{pyin}$")
#                 ax[1].plot(obj.time, obj.ff2, "b*", ms=ms, label=r"FF$_{yin}$")
#             if select_time is False:
#                 ax[1].legend(bbox_to_anchor=(1.135, 1.))
#         ax[1].set_ylim(obj.flim)
#         ax[1].set_xlim(tlim)
#         ax[1].set_ylabel("Frequency (kHz)")
#         ax[1].set_xlabel("Time (s)")

#         plt.subplots_adjust(
#             wspace=0.1, hspace=0.1, top=0.9, bottom=0.05, left=0.05, right=0.85
#         )

#         if obj.type!="":
#             plt.subplots_adjust(top=0.85)
#             suptitle = f"Waveform and Spectrogram\n{_suptitle(obj)}"
#         else:
#             suptitle = f"Waveform and Spectrogram: {_suptitle(obj)}"
            
#         fig.suptitle(
#             suptitle,
#             fontsize=self.title_font["size"],
#             y=0.99,
#             fontweight="bold",
#         )
#         path_save = obj.proj_dirs.IMAGES / _save_name(obj)

#     else:
#         raise Exception("Wrong object.")
#     # fig.tight_layout()
    

#     if save:
#         fig.savefig(path_save,
#                     transparent=True,
#                     bbox_inches="tight")
#         print(f"Image save at {path_save}")

#     if select_time:
#         clicker = klicker_time(fig, ax[1])
    
#     if show:
#         plt.show()
#         if select_time:
#             return clicker
#     else:
#         plt.close()

        
# # %%
# def syllables(
#     obj: Any,  # Union[Syllable,Song],
#     obj_synth: Any,  # Union[Syllable,Song],
#     ff_on: bool = False,
#     figsize: Tuple[float, float] = (11, 6),
#     save: bool = True,
#     show: bool = True,
# ) -> None:
#     """


#     Parameters
#     ----------
#         obj : Syllable | Song

#         obj : Syllable | Song

#         ff_on : bool = False
#             Falg to enable fundamental frequency visualization
#         save : bool = True
#             Flag to save plot
#         show : bool = True
#             Flag to display plot

#     Return
#     ------
#         None

#     Example
#     -------
#         >>>
#     """
#     plt.close()

#     ticks = FuncFormatter(lambda x, pos: f"{x*1e-3:g}")
#     fig, ax = plt.subplots(2, 2, figsize=figsize, sharex=True)

#     img = Specshow(
#         obj.Sxx_dB,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj.sr,
#         hop_length=obj.hop_length,
#         ax=ax[0, 0],
#         cmap=_CMAP,
#     )

#     ax[0, 0].set_title("Real", fontweight="bold")
#     ax[0, 0].yaxis.set_major_formatter(ticks)
#     ax[0, 0].set_ylim(obj.flim)
#     ax[0, 0].set_ylabel("Frequency (kHz)")
#     ax[0, 0].set_xlabel("")

#     img = Specshow(
#         obj_synth.Sxx_dB,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj_synth.sr,
#         hop_length=obj_synth.hop_length,
#         ax=ax[0, 1],
#         cmap=_CMAP,
#     )

#     cbar_ax = fig.add_axes((0.95, 0.445, 0.015, 0.36))
    
#     clb = fig.colorbar(img, cax=cbar_ax, format="%+2.f")
#     clb.set_label("Power\n(dB)", labelpad=-25, y=1.2, rotation=0)

#     ax[0, 1].yaxis.set_major_formatter(ticks)
#     ax[0, 1].set_title("Synthetic", fontweight="bold")
#     ax[0, 1].set_ylim(obj.flim)
#     ax[0, 1].set_ylabel("")
#     ax[0, 1].set_xlabel("")

#     if ff_on:
#         ax[0, 0].plot(obj.time, obj.ff, "bo-", lw=2, label="FF")
#         ax[0, 0].legend(bbox_to_anchor=(0.975, 0.975))

#         ax[0, 1].plot(obj_synth.time, obj_synth.ff, "go-", lw=2, label="FF")
#         ax[0, 1].legend(bbox_to_anchor=(0.975, 0.975))

#     t_end = obj.time[-1] + obj.time[-1] - obj.time[-2]
#     ax[1, 0].plot(obj.time_s, obj.s, label="waveform", c="b")
#     ax[1, 0].set_xlim((obj.time_s[0], t_end))
#     ax[1, 0].plot(obj.time_s, obj.envelope, label="envelope", c="darkblue")
#     ax[1, 0].set_ylabel("Amplitud (a.u.)")
#     ax[1, 0].set_xlabel("Time (s)")
#     ax[1, 0].legend()

#     ax[1, 1].plot(obj_synth.time_s, obj_synth.s, label="waveform", c="g")
#     ax[1, 1].plot(
#         obj_synth.time_s, obj_synth.envelope, label="envelope", c="darkgreen"
#     )
#     ax[1, 1].set_xlabel("Time (s)")
#     ax[1, 1].set_ylabel("")
#     ax[1, 1].legend()

#     # removing y ticks labels
#     ax[1, 1].yaxis.set_major_formatter(NullFormatter())
#     ax[0, 1].yaxis.set_major_formatter(NullFormatter())

#     plt.subplots_adjust(
#         wspace=0.05, hspace=0.075, left=0.07, top=0.85, right=0.93, bottom=0.07
#     )
#     if obj.type!="":
#         plt.subplots_adjust(top=0.8)
#         suptitle = f"Comparing Syllables\n{_suptitle(obj)}"
#     else:
#         suptitle = f"Comparing Syllables: {_suptitle(obj)}"

#     fig.suptitle(
#         suptitle,
#         y=0.99,
#         fontsize=self.title_font["size"],
#         fontweight="bold",
#     )

#     if save:
#         img_name = f"{_save_name(obj)}-SoundAndSpectros.png"
#         fig.savefig(
#             obj.proj_dirs.IMAGES / img_name,
#             transparent=True,
#             bbox_inches="tight",
#         )
#         print(f"Image save at {img_name}")
#     # return fig, ax
#     if show: 
#         plt.show()
#     else:
#         plt.close()
# # %%

        
# # %%
# def spectrum_comparison(
#     obj: Any,  # Union[Syllable,Song],
#     obj_synth: Any,  # Union[Syllable,Song],
#     cmap: str = "afmhot_r",
#     figsize: Tuple[float, float] = (11, 6),
#     sharey: bool = True,
#     save: bool = True,
#     show: bool = True,
# ) -> None:
#     """


#     Parameters
#     ----------
#         obj : Syllable | Song

#         obj_synth : Syllable | Song

#         figsize : tuple = (10,10)
#             Size of the figure (width, height)
#         sharey: bool = True,
#             Enable share y axis
#         save : bool = True
#             Flag to save plot
#         show : bool = True
#             Flag to display plot

#     Return
#     ------
#         None

#     Example
#     -------
#         >>>
#     """
#     if cmap is not None:
#         _CMAP = cmap
#     labelrotation = 90 if obj.time[-1] < 1 else 0
#     _fontproperties = {"size": 12, "weight": "bold"}

#     plt.close()
    
#     ticks = FuncFormatter(lambda x, pos: f"{x*1e-3:g}")

#     fig = plt.figure(figsize=figsize)

#     gs = fig.add_gridspec(
#         nrows=2,
#         ncols=3,
#         hspace=0.35,
#         wspace=0.2,
#         top=0.825,
#         bottom=0.15,
#         left=0.05,
#         right=0.95,
#     )
#     vmin = obj.Sxx_dB.min()
#     vmax = obj.Sxx_dB.max()

#     # ------------------ spectrogams ----------------------------
#     ax1 = fig.add_subplot(gs[0, 0])

#     img = Specshow(
#         obj.Sxx_dB,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj.sr,
#         hop_length=obj.hop_length,
#         ax=ax1,
#         cmap=_CMAP,
#     )

#     clb = fig.colorbar(img, ax=ax1)
#     clb.set_label("Power\n(dB)", labelpad=-16, y=1.25, rotation=0)

#     ax1.tick_params(axis="x", which="both", labelrotation=labelrotation)
#     ax1.set_title("Real", fontproperties=_fontproperties)
#     ax1.set_xlim((obj.time[0], obj.time[-1]))
#     ax1.yaxis.set_major_formatter(ticks)
#     ax1.set_ylim(obj.flim)
#     ax1.set_ylabel("")
#     ax1.set_xlabel("")

#     if sharey:
#         ax2 = fig.add_subplot(gs[0, 1], sharex=ax1, sharey=ax1)
#     else:
#         ax2 = fig.add_subplot(gs[0, 1], sharex=ax1)

#     img = Specshow(
#         obj_synth.Sxx_dB,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj_synth.sr,
#         hop_length=obj_synth.hop_length,
#         ax=ax2,
#         cmap=_CMAP,
#     )

#     clb = fig.colorbar(img, ax=ax2)
#     clb.set_label("Power\n(dB)", labelpad=-16, y=1.25, rotation=0)

#     ax2.tick_params(axis="x", which="both", labelrotation=labelrotation)
#     ax2.set_title("Synthetic", fontproperties=_fontproperties)
#     ax2.yaxis.set_major_formatter(ticks)
#     ax2.set_ylim(obj.flim)
#     ax2.set_ylabel("")
#     ax2.set_xlabel("")

#     # ------------------ Mel spectgrograms ------------------
#     if sharey:
#         ax3 = fig.add_subplot(gs[1, 0], sharex=ax1, sharey=ax1)
#     else:
#         ax3 = fig.add_subplot(gs[1, 0], sharex=ax1)

#     img = Specshow(
#         obj.ff_coef,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj.sr,
#         hop_length=obj.hop_length,
#         ax=ax3,
#         cmap=_CMAP,
#         vmin=0,
#         vmax=100,
#     )

#     clb = fig.colorbar(img, ax=ax3)

#     ax3.tick_params(axis="x", which="both", labelrotation=labelrotation)
#     ax3.yaxis.set_major_formatter(ticks)
#     ax3.set_ylabel(" " * 65 + "Frequency (kHz)", loc="center", labelpad=10)
#     ax3.set_xlabel("")
#     ax3.set_ylim(obj.flim)

#     if sharey:
#         ax4 = fig.add_subplot(gs[1, 1], sharex=ax1, sharey=ax1)
#     else:
#         ax4 = fig.add_subplot(gs[1, 1], sharex=ax1)

#     img = Specshow(
#         obj_synth.ff_coef,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj.sr,
#         cmap=_CMAP,
#         vmin=0,
#         vmax=100,
#         hop_length=obj_synth.hop_length,
#         ax=ax4,
#     )

#     clb = fig.colorbar(img, ax=ax4)

#     ax4.tick_params(axis="x", which="both", labelrotation=labelrotation)
#     ax4.yaxis.set_major_formatter(ticks)
#     ax4.set_xlabel("Time (s)", labelpad=10)
#     ax4.set_ylim(obj.flim)
#     ax4.set_ylabel("")

#     # ------------------ Delta Sxx - Mel ------------------------
#     if sharey:
#         ax5 = fig.add_subplot(gs[0, 2], sharex=ax1, sharey=ax1)
#     else:
#         ax5 = fig.add_subplot(gs[0, 2], sharex=ax1)

#     img = Specshow(
#         obj_synth.deltaSxx,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj.sr,
#         vmin=0,
#         vmax=1,
#         ax=ax5,
#         cmap=_CMAP,
#         hop_length=obj_synth.hop_length,
#     )

#     ax5.set_title(r"Difference ($\Delta$)", fontproperties=_fontproperties)
#     ax5.tick_params(axis="x", which="both", labelrotation=labelrotation)
#     ax5.yaxis.set_major_formatter(ticks)
#     ax5.set_ylim(obj.flim)
#     ax5.set_ylabel("")
#     ax5.set_xlabel("")

#     clb = fig.colorbar(img, ax=ax5)
#     clb.set_label("Power\n(dB)", labelpad=-16, y=1.25, rotation=0)

#     if sharey:
#         ax6 = fig.add_subplot(gs[1, 2], sharex=ax1, sharey=ax1)
#     else:
#         ax6 = fig.add_subplot(gs[1, 2], sharex=ax1)

#     img = Specshow(
#         obj_synth.deltaMel,
#         x_axis="s",
#         y_axis="linear",
#         sr=obj.sr,
#         hop_length=obj_synth.hop_length,
#         ax=ax6,
#         cmap=_CMAP,
#     )

#     ax6.tick_params(axis="x", which="both", labelrotation=labelrotation)
#     ax6.yaxis.set_major_formatter(ticks)
#     ax6.set_ylim(obj.flim)
#     ax6.set_ylabel("")
#     ax6.set_xlabel("")
#     # ax6.yaxis.set_major_formatter(NullFormatter())

#     plt.text(0.04, 6e3, "MEL", rotation=90, fontproperties=_fontproperties)
#     plt.text(
#         0.04, 3.5e4, "Linear", rotation=90, fontproperties=_fontproperties
#     )

#     fig.colorbar(img, ax=ax6)

#     if obj.type!="":
#         plt.subplots_adjust(top=0.8)
#         suptitle = f"Comparing Spectral Content\n{_suptitle(obj)}"
#     else:
#         suptitle = f"Comparing Spectral Content: {_suptitle(obj)}"

#     fig.suptitle(
#         suptitle,
#         fontsize=self.title_font["size"],
#         y=0.99,
#         fontweight="bold",
#     )
#     if save:
#         img_name = f"{_save_name(obj)}-ComparingSpectros.png"
#         fig.savefig(
#             obj.proj_dirs.IMAGES / img_name,
#             transparent=True,
#             bbox_inches="tight",
#         )
#         print(f"Image save at {img_name}")
#     # return fig, gs
#     if show: 
#         plt.show()
#     else:
#         plt.close()