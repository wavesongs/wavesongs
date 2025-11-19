    
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
