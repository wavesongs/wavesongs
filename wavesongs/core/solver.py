from matplotlib import pyplot as plt
import numpy as np
import time
import pandas as pd
from pathlib import Path

from scipy.optimize import curve_fit
from numpy.polynomial import Polynomial
from sklearn.metrics import r2_score, mean_squared_error
from scipy.interpolate import interp1d

from wavesongs.object import Syllable, Synthetic

from wavesongs.utils.math import sinusoidal, fitting, gaussian
from IPython.display import display


#%%
def transform_composition(params0, time, random_per=10, no_params=2):
    # Make some random linear quadratic transformation to the beta curve
    a0_shift = random_per/100 * params0[-1] # 10% of the last coefficient p0
    a0 = np.random.uniform(-a0_shift, a0_shift)
    a1 = 1 + np.random.uniform(-random_per/100, random_per/100)
    a = np.random.uniform(-random_per/100, random_per/100, size=params0.size-2)
    params_noisy = np.concatenate(([a0, a1], a))[:no_params]
    # print(params0, params_noisy)
    noisy_curve = np.polyval(params0, time)
    # a0 + a1 * noisy_curve + a2 * noisy_curve**2
    noisy_curve_compose = np.polyval(params_noisy[::-1], noisy_curve)
    
    return noisy_curve_compose, params_noisy
#%%
def transform_fitting(params0, time, random_per=1, no_params=4):
    # vayring the fitting coefficients
    random_percent = 1 + np.random.uniform(-random_per/100, random_per/100, size=params0.shape)
    random_percent = np.concatenate((np.ones(params0.shape[0]-no_params), random_percent[-no_params:]))
    params_noisy = params0 * random_percent
    noisy_curve = np.polyval(params_noisy, time)
    
    return noisy_curve, params_noisy
#%%
def augmente_data(syllable, model, metadata, alpha_0=1e-5, mode="fitting", 
                  N=1, beta_N=10, poly_deg_beta=5, random_per=5, no_params=2,
                  umbral_FF=1.4, n_fft=512, ff_method="yin",
                  verbose=True, plot=True, save_audio=True, save_df=True):
    df = pd.DataFrame()
    # Compute the optimal beta curve fitting for the syllable
    _, beta_fit = optimal_beta_curve(syllable, model, alpha_0=alpha_0, # beta_opt
                                     beta_N=beta_N, plot=plot, poly_deg=poly_deg_beta)
    
    start_time = time.perf_counter()
    times = metadata["times"]
    for index in range(len(times)):
        print(f"Syllable {index}: {metadata['times'][index]} - Type: {metadata['type'][index]}")
        metadata_indx = {key: metadata[key][index] for key in metadata}
        syllable = Syllable(file_id=syllable.file_name, tlim=times[index], proj_dirs=syllable.proj_dirs, metadata=metadata_indx) 
        syllable.acoustical_features(umbral_FF=umbral_FF, n_fft=n_fft, ff_method=ff_method)
        
        # Resample optimal beta curve to match the time vector of the syllable
        beta_curve_interp = interp1d(syllable.time, beta_fit(syllable.ff), kind='linear', fill_value='extrapolate')
        beta_optimal_rs = beta_curve_interp(syllable.time_s)
        
        # Vary beta around the optimal curve to generate synthetic syllables
        syllables_df_synth = augmente_beta(syllable, model, beta_optimal_rs, alpha_0=alpha_0,
                                           mode=mode, N=N, random_per=random_per, no_params=no_params,
                                           plot=plot, save_audio=save_audio, save_df=False, verbose=verbose)
        # Append to the main dataframe
        df = pd.concat([df, syllables_df_synth], ignore_index=True)

    # Save the dataframe with all syllables and metadata
    if save_df:
        original_name = syllable.file_name.split(" ")[0]
        path = Path(syllable.proj_dirs.augmented_audios / original_name)
        df.to_csv(path / f"{original_name}_{times[0][0]}-{times[-1][1]}.csv", index=False)
    # Display dataframe
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    if verbose:
        display(df)
        print(f"Computation time for augmenting data: {elapsed_time/60:.2f} min ",
              f"for {len(times)} syllables fo the audio file {syllable.file_name} ", f"generating {N} samples per each syllable. Method used {mode}. Random percentage {random_per}% varying {no_params} parameters.")

    return df
#%%
def augmente_beta(
    syllable, model,
    beta, alpha_0=0.5,## plot=True, beta
    N=10, random_per=1, mode="composition", # mode params
    poly_deg=5, no_params=4, 
    umbral_FF=1.0, n_fft=512, ff_method="yin",
    verbose=True, plot=True, legend=True,
    save_audio=True, save_df=True, save_img=False
) -> pd.DataFrame:
    
    # Create empty DataFrame with defined columns
    metadata_cols = ["type", "class_type", "no_syllable", "times"]
    columns = ['ME (%)', 'RMSE (Hz)', 'params', 'alpha', 'id', 'file_name', "mode", "name"] + metadata_cols
    results_df = pd.DataFrame(columns=columns)
    
    # Create folder to save augmented audios
    original_name = syllable.file_name.split(" ")[0]
    if verbose:
        print(f"Original song: {original_name} - No. Syllable: {syllable.no_syllable} - Type: {syllable.type}")
    if save_audio:
        path = Path(syllable.proj_dirs.augmented_audios / original_name)
        path.mkdir(parents=True, exist_ok=True)
    
    # Create a synthetic object
    duration = syllable.time_s[-1]
    synthetic = Synthetic(duration=duration, proj_dirs=syllable.proj_dirs, sr=syllable.sr)
    synthetic.initialize()

    # Create the optimal synthetized syllable using alpha and beta
    alpha = gaussian(synthetic.time_s, alpha_0, duration/2, sigma=0.1)
    synthetized = model.motor_gesture(synthetic, curves=[alpha, beta])
    synthetized.acoustical_features(umbral_FF=1.0, n_fft=512, ff_method="yin")

    # ------------------ ---- ------------------
    relative_error = 100 *np.abs(synthetized.ff - syllable.ff) / np.abs(syllable.ff)
    mse = np.mean((synthetized.ff - syllable.ff)**2)
    # fit_beta_final = Polynomial.fit(time_grid_4_ff, beta_curve_rs, deg=poly_deg)
    fit_beta_final = Polynomial.fit(synthetized.time_s, synthetized.beta, deg=poly_deg)
    params0 = fit_beta_final.convert().coef[::-1]

    # Compute for the optimal a0* and b0* parameters
    alpha = gaussian(synthetic.time_s, alpha_0, duration/2, sigma=0.1, a1=-0.1*alpha_0) # alpha 
    synthetized = model.motor_gesture(synthetic, [alpha, synthetized.beta])
    synthetized.acoustical_features(umbral_FF=umbral_FF, n_fft=n_fft, ff_method=ff_method)
    # Add first row (original)
    synthetized.file_name = f"{syllable.metadata['no_syllable']}_s0.wav"
    if save_audio:
        synthetized.write_audio(path=path / synthetized.file_name, verbose=verbose)
    results_df.loc[len(results_df)] = [np.mean(relative_error), np.sqrt(mse), params0, alpha_0, synthetized.file_name[:-4], synthetized.file_name, mode, original_name] + [syllable.metadata[col] for col in metadata_cols]

    if mode=="composition": transform = transform_composition
    elif mode=="fitting":   transform = transform_fitting

    ## plot
    colors_array = plt.cm.tab20(np.linspace(0, 1, N))
    colors_array[:, 3] = 0.5
    colors_array = np.vstack([np.array([0,0,0,1]), colors_array])
    fig, axs = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

    axs[0].plot(synthetized.time, synthetized.ff, "-", color=colors_array[0], label="Opt")
    axs[1].plot(synthetized.time_s, beta, color=colors_array[0], label="Opt")
    axs[2].plot(synthetized.time, relative_error, "-", color=colors_array[0], label="Opt")
    
    # Compute for the augmented parameters, varying
    for i in range(N):
        beta_noisy_curve, params_noisy = transform(params0, synthetized.time_s, random_per, no_params)
        alpha = gaussian(synthetic.time_s, alpha_0, duration/2, sigma=0.1, a1=-0.1*alpha_0)
        
        synthetized = model.motor_gesture(synthetic, [alpha, beta_noisy_curve]) # gera error
        synthetized.acoustical_features(umbral_FF=umbral_FF, n_fft=n_fft, ff_method=ff_method)
        
        synthetized.file_name = f"{syllable.metadata['no_syllable']}_s{i+1}.wav"
        if save_audio:
            synthetized.write_audio(path=path / synthetized.file_name, verbose=verbose)
        # Store metrics
        relative_error = 100 *np.abs(synthetized.ff - syllable.ff) / np.abs(syllable.ff)
        mse = np.mean((synthetized.ff - syllable.ff)**2)
        # Add new row to DataFrame
        results_df.loc[len(results_df)] = [np.mean(relative_error), np.sqrt(mse), params_noisy, alpha_0, synthetized.file_name[:-4], synthetized.file_name, mode, original_name] + [syllable.metadata[col] for col in metadata_cols]

        ## plot
        axs[0].plot(synthetized.time, synthetized.ff, "-", color=colors_array[i+1], label=i)
        axs[1].plot(synthetized.time_s, beta_noisy_curve, color=colors_array[i+1], label=i)
        axs[2].plot(synthetized.time, relative_error, "-", color=colors_array[i+1], label=i)

    if legend and N<10: axs[1].legend(loc='upper left', bbox_to_anchor=(1, 1))
    axs[0].set_ylabel("FF (Hz)")

    axs[1].set_ylabel(r"Control Parameter ($\beta$)")

    # axs[2].set_xlim(0-0.1, duration+0.1)
    axs[2].set_xlabel("Time (s)")
    axs[2].set_ylabel("Relative Error (%)")

    plt.subplots_adjust(hspace=0.1, top=0.925, right=0.85)
    plt.suptitle(rf"{syllable.file_name} - {syllable.no_syllable}"+"\n"+fr"$\alpha={alpha_0}$ - Fit Degree: {poly_deg} - N={N} - Randomness: {random_per} %")
    
    if plot: plt.show()

    if save_df: 
        results_df.to_csv(path / f"{syllable.metadata['no_syllable']}.csv", index=False)
    if verbose: display(results_df)
    
    return results_df
#%%
def optimal_beta_curve(syllable, model,
                        alpha_0=1e-5, beta_max=2, beta_N=50,
                        duration=0.1, sr=44100,
                        umbral_FF=1.4, n_fft=512, ff_method="yin",
                        poly_deg=2, verbose=True, plot=True,
                        # mode="best"
                        ) -> np.ndarray: # other mode is "fitted"
    """
    Find the bifurcation curve for a given model and alpha_0 value.
    Returns the minimum beta value for oscillation. The grid is computed by creating
    lines of the control parameters and generating synthetic syllables.

    Parameters:
    model : Model
        The bird vocalization model.
    alpha_0 : float
        The alpha parameter value. Small values produce less harmonics.
    beta_max : float
        The maximum beta value to consider.
    beta_N : int
        The number of beta values to evaluate.
    duration : float
        Duration of the synthetic syllable in seconds.
    sr : int
        Sampling rate for the synthetic syllable.
    verbose : bool
        If True, prints computation time.
    """

    time_s = np.linspace(0, duration, int(sr*duration)) # time vector

    # Compute minimum beta value for given alpha_0
    beta_bif, mu1_curves, _, _ = model.bifurcation_ode()
    beta_0 = beta_bif[(np.abs(mu1_curves[1] - alpha_0)).argmin() + 1]

    # Create grid to compute the values of beta
    beta_grid = np.linspace(beta_0, beta_max, beta_N)
    ff_grid = np.zeros(beta_N)

    # Compute the FF for points in the grid
    start_time = time.perf_counter()
    # Create synthetic syllable
    synthetic = Synthetic(duration=duration, proj_dirs=syllable.proj_dirs, sr=sr)
    synthetic.initialize()

    # fit_sin, params = fitting(btv_0, function="sinusoidal", verbose=False) # Get parameters from custom fitting
    # Compute and store the mean ff for act alpha and a beta thinkede a short constant line.
    for i in range(beta_N):
        # Define the control parameters
        # aplha = gaussian(time_s, 0.05, duration/2, sigma=0.1, a1=-0.01), # alpha
        alpha = alpha_0 * np.ones_like(time_s)          # alpha constant
        beta = beta_grid[i] * np.ones_like(time_s)      # beta constant
        # compute the generated syllable using the curves and synthetic sample
        synthetized = model.motor_gesture(synthetic, [alpha, beta])
        synthetized.acoustical_features(umbral_FF=umbral_FF, n_fft=n_fft, ff_method=ff_method)

        ff_grid[i] = np.mean(synthetized.ff)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    if verbose:
        print(f"Computation time for beta vs ff curve: {elapsed_time:.3f} s = {elapsed_time/60:.2f} min" )

    # --------------------- Fit beta vs ff - find beta(ff) --------------------- #
    # ff_grid_ext = np.linspace(0, 20000, time_s.shape[0]) # fmin, fmax, create the ff grid
    beta_fit = Polynomial.fit(ff_grid, beta_grid, deg=poly_deg)
    params_beta_ff = beta_fit.coef
    r2_beta_ff = r2_score(beta_grid, beta_fit(ff_grid))
    rmse_beta_ff = np.sqrt(mean_squared_error(beta_grid, beta_fit(ff_grid)))
    scores_beta_ff = [r2_beta_ff, rmse_beta_ff]

    # Reesampling beta bc ff has different size than beta
    ff_grid_ext_rs = np.linspace(min(syllable.ff), max(syllable.ff), time_s.shape[0])
    beta_curve_rs = beta_fit(ff_grid_ext_rs)

    # Interpolate beta_fit(syllable.ff) to synthetic.time_s shape
    beta_curve_interp = interp1d(syllable.time, beta_fit(syllable.ff), kind='linear', fill_value='extrapolate')
    beta_curve_resampled = beta_curve_interp(syllable.time_s)

    if plot:
        plt.figure()
        plt.plot(ff_grid, beta_grid, "x", label="Data")
        plt.plot(ff_grid, beta_fit(ff_grid), "k-", label="Fit")
        plt.plot(ff_grid_ext_rs, beta_curve_rs, "--", label="Beta Curve")
        # plt.plot(syllable.time_s, beta_curve_resampled, "--", label="Beta Curve")
        plt.ylabel(r"Beta Control Parameter ($\beta$)")
        plt.xlabel("Fundamental Frequency (Hz)")
        plt.title(fr"$\alpha_0={alpha_0}$ $\beta_0={beta_0:.4f}$" +"\n"+f"Bifurcation Curve - R2={r2_beta_ff:.3f}, RMSE={rmse_beta_ff:.3f}")
        plt.ylim(beta_grid.min()-0.1, beta_grid.max()+0.1)
        plt.xlim(min(ff_grid)-1000, max(ff_grid)+1000)
        plt.legend()
        plt.show()

    return np.array(beta_curve_resampled), beta_fit# beta_fit, [beta_curve_rs, ff_grid_ext_rs], [beta_grid, ff_grid]







# def transform_fitting_shift_y(params0, time, random_per=1):
#     params_noisy = params0.copy()
#     params_noisy[-1] *= np.random.uniform(0.95, 1.05) # shift vertically
#     noisy_curve = np.polyval(params_noisy, time)
    
#     return noisy_curve, params_noisy

# def augmented_beta(
#     syllable, synthetized, model, # plot=True, beta
#     N=10, random_per=1, mode="composition", # mode params
#     alpha=0.5, poly_deg=5, no_params=4,
#     umbral_FF=1.0, n_fft=512, ff_method="yin",
#     verbose=True, save=True
# ) -> pd.DataFrame:
    
#     # Create empty DataFrame with defined columns
#     columns = ['ME (%)', 'RMSE (Hz)', 'params', 'alpha', 'id', 'file_name']
#     results_df = pd.DataFrame(columns=columns)
    
#     # Create folder to save augmented audios
#     original_name = syllable.file_name.split(" ")[0]
#     if verbose:
#         print(f"Original song: {original_name}")
#     if save:
#         Path(proj_dirs.augmented_audios).mkdir(parents=True, exist_ok=True)
    
#     duration = syllable.time_s[-1]
#     synthetic = Synthetic(duration=duration, proj_dirs=proj_dirs, sr=sr)
#     synthetic.initialize()

#     # ------------------ ---- ------------------
#     relative_error = 100 *np.abs(synthetized.ff - syllable.ff) / np.abs(syllable.ff)
#     mse = np.mean((synthetized.ff - syllable.ff)**2)
#     # fit_beta_final = Polynomial.fit(time_grid_4_ff, beta_curve_rs, deg=poly_deg)
#     fit_beta_final = Polynomial.fit(synthetized.time_s, synthetized.beta, deg=poly_deg)
#     params0 = fit_beta_final.convert().coef[::-1]

#     # Compute for the optimal a0* and b0* parameters
#     alpha = gaussian(synthetic.time_s, alpha_0, duration/2, sigma=0.1, a1=-0.1*alpha_0) # alpha 
#     synthetized = model.motor_gesture(synthetic, [alpha, synthetized.beta])
#     synthetized.acoustical_features(umbral_FF=umbral_FF, n_fft=n_fft, ff_method=ff_method)
#     # Add first row (original)
#     synthetized.file_name = f"{original_name}_opt.wav"
#     if save:
#         synthetized.write_audio(path=proj_dirs.augmented_audios / synthetized.file_name, verbose=verbose)
#     results_df.loc[len(results_df)] = [np.mean(relative_error), np.sqrt(mse), params0, alpha_0, -1, synthetized.file_name]

#     if mode=="composition": transform = transform_composition
#     elif mode=="fitting":   transform = transform_fitting
             
#     # Compute for the augmented parameters, varying
#     for i in range(N):
#         beta_noisy_curve, params_noisy = transform(params0, synthetized.time_s, random_per, no_params)
#         alpha = gaussian(synthetic.time_s, alpha_0, duration/2, sigma=0.1, a1=-0.1*alpha_0)
        
#         synthetized = model.motor_gesture(synthetic, [alpha, beta_noisy_curve]) # gera error
#         synthetized.acoustical_features(umbral_FF=umbral_FF, n_fft=n_fft, ff_method=ff_method)
        
#         synthetized.file_name = f"{original_name}_s{i}.wav"
#         if save:
#             synthetized.write_audio(path=proj_dirs.augmented_audios / synthetized.file_name, verbose=verbose)
#         # Store metrics
#         relative_error = 100 *np.abs(synthetized.ff - syllable.ff) / np.abs(syllable.ff)
#         mse = np.mean((synthetized.ff - syllable.ff)**2)
#         # Add new row to DataFrame
#         results_df.loc[len(results_df)] = [np.mean(relative_error), np.sqrt(mse), params_noisy, alpha_0, i, synthetized.file_name]

#     if save: 
#         results_df.to_csv(proj_dirs.augmented_audios / f"{original_name}.csv", index=False)
#     if verbose: display(results_df)
    
#     return results_df

# syllables_df = augmented_beta(btv_0, synthetized, model, mode="fitting", N=5, no_params=1)


# def plot_augmented_data(syllables_df, syllable, model, mode="fitting"):
#     N = len(syllables_df)
#     colors_array = plt.cm.tab20(np.linspace(0, 1, N))
#     colors_array[:, 3] = 0.5
#     colors_array = np.vstack([np.array([0,0,0,1]), colors_array])

#     duration = syllable.time_s[-1]
#     synthetic = Synthetic(duration=duration, proj_dirs=proj_dirs, sr=sr)
#     synthetic.initialize()
    
#     # ------------------ Plot ------------------
#     fig, axs = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
#     syllables_df.iloc[0]['id'] = "Opt"

#     for i in range(N):
#         # Extract data from dataframe
#         alpha_0 = syllables_df.iloc[i]['alpha']
#         beta_params = syllables_df.iloc[i]['params']
#         label = syllables_df.iloc[i]['id']

#         # Define curves
#         alpha = gaussian(synthetic.time_s, alpha_0, duration/2, sigma=0.1, a1=-0.1*alpha_0) # alpha 
#         beta = np.polyval(beta_params, synthetic.time_s)
        
#         synthetized = model.motor_gesture(synthetic, [alpha, beta]) # gera error
#         synthetized.acoustical_features(umbral_FF=syllable.umbral_FF, n_fft=syllable.n_fft, ff_method=syllable.ff_method)
        
#         # Compute metrics
#         relative_error = 100 *np.abs(synthetized.ff - syllable.ff) / np.abs(syllable.ff)
#         mse = np.mean((synthetized.ff - syllable.ff)**2)
#         # plot
#         color = colors_array[i]
#         axs[0].plot(synthetized.time, synthetized.ff, "-", color=color, label=label)
#         # axs[1].plot(synthetized.time, np.polyval(params_noisy, synthetized.time), alpha=alpha, color=color, label=label)
#         axs[1].plot(synthetized.time_s, beta, color=color, label=label)
#         axs[2].plot(synthetized.time, relative_error, "-", color=color, label=label)

#     axs[1].legend(loc='upper left', bbox_to_anchor=(1, 1))
#     axs[1].set_ylabel(r"Control Parameter ($\beta$)")

#     # axs[2].set_xlim(0-0.1, duration+0.1)
#     axs[2].set_xlabel("Time (s)")
#     axs[2].set_ylabel("Relative Error (%)")

#     axs[0].set_ylabel("FF (Hz)")

#     plt.subplots_adjust(hspace=0.1, top=0.925, right=0.85)
#     # plt.suptitle(rf"$\alpha={alpha_0}$ - Fit Degree: {poly_deg} - N={N} - Randomness: {random_per} %")
#     plt.show()

# plot_augmented_data(syllables_df, btv_0, model)