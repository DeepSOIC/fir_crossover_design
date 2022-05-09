import myWindowFuncs

def plot_fir(n_pts = 731, f_x = 250.0, window = ('tukey', 0.5), fs = 44100, pass_zero = 'lowpass', label = 'main'):
    import scipy.signal
    import numpy as np
    
    try:
        win = scipy.signal.windows.get_window(window, n_pts)
    except Exception: raise()
    #except Exception as err:
    #    print("non-standard window ({err})".format(err= err))
    #    import myWindowFuncs
    #    win = myWindowFuncs.getWindow(n_pts, window)
    #    win = win/np.abs(win).max()
    #    fir_nw = scipy.signal.firwin(
    #        n_pts, # fir length, determines xover transition width
    #        f_x, # xover frequency
    #        window='boxcar', 
    #        fs= fs, # sample rate
    #        pass_zero= pass_zero
    #    )
    #    fir_unnorm = fir_nw*win
    #    fir = fir_unnorm/np.sum(fir_unnorm)
    else:
        fir = scipy.signal.firwin(
            n_pts, # fir length, determines xover transition width
            f_x, # xover frequency
            window=window, 
            fs= fs, # sample rate
            pass_zero= pass_zero
        )
    
    import matplotlib.pyplot as plt
    
    plt.ion()
    
    plt.figure('waveform'+label if label else None)
    plt.plot(
        fir/np.abs(fir).max(), 
        label= "wf ({window} window)".format(window= str(window))
    )
    plt.plot(
        win,
        label= "{window} window".format(window= str(window))
    )
    plt.title("waveforms")
    plt.ylabel("amplitude")
    plt.xlabel("time [samples]")
    plt.legend()
    
    plt.show()
    
    inversefir = fir.copy()
    inversefir[int((n_pts-1)/2)] -= 1.0
    
    import audioSpectralTools as AST
    frequencies, spec = AST.audio_fft(AST.pad(fir, 65536), normalize= 'filter')
    frequencies, invspec = AST.audio_fft(AST.pad(inversefir, 65536), normalize= 'filter')
    
    plt.figure('spectrum'+label if label else None)
    plt.gca(
        label='spectral',
        xscale='log', xlim=(20.0, 20e3),
        yscale='log', ylim=(1e-3, 3)
    )
    plt.xlabel("frequency [Hz]")
    plt.ylabel("amplitude")
    #import uuid
    #id = uuid.uuid4()
    plt.plot(
        np.append(frequencies, frequencies[::-1]), 
        np.append(spec, invspec[::-1]), 
        label= str(window)
    )
    plt.axvline(250.0, color='#00ff00ff')
    plt.grid(True, which= 'major', color='#00ff00ff', linewidth=0.6)
    plt.grid(True, which= 'minor', color='#ffff00ff', linewidth=0.6)
    plt.legend()
    plt.show()
