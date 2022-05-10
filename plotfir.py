figures = None
ax_wf = None
ax_sp = None
conns = [] #connections for close events

def fig(split = False, label = None):
    """fig(split = False): creates new figures to plot onto"""
    global figures, ax_wf, ax_sp, conns

    import matplotlib.pyplot as plt
    plt.ion()
    for conn, fig in conns:
        fig.canvas.mpl_disconnect(conn)
    conns = []
    
    if split:
        figure1 = plt.figure()
        ax_wf = figure1.add_subplot(
            1,1,1
        )
        figure2 = plt.figure()
        ax_sp = figure2.add_subplot(
            1,1,1,
            xscale='log', xlim=(20.0, 20e3),
            yscale='log', ylim=(1e-3, 3)
        )   
        figures = [figure1, figure2]
    else:
        figure = plt.figure(figsize = (15, 5), num= label)
        ax_wf = figure.add_subplot(
            1,3,1
        )
        ax_sp = figure.add_subplot(
            1,3,(2,3),
            xscale='log', xlim=(20.0, 20e3),
            yscale='log', ylim=(1e-3, 3)
        )
        figures = [figure,]
    
    ax_wf.set_title("waveforms")
    ax_wf.set_ylabel("amplitude")
    ax_wf.set_xlabel("time [samples]")
    ax_sp.set_xlabel("frequency [Hz]")
    ax_sp.set_ylabel("amplitude")
    ax_sp.grid(True, which= 'major', color='#00ff00ff', linewidth=0.6)
    ax_sp.grid(True, which= 'minor', color='#ffff00ff', linewidth=0.6)
    
    for fig in figures:
        conn = fig.canvas.mpl_connect('close_event', on_close)
        conns.append((conn, fig))
        

def plot_firwin(n_pts = 731, f_x = 250.0, window = ('tukey', 0.5), fs = 44100, pass_zero = 'lowpass', label = None):
    global figures, ax_wf, ax_sp

    import scipy.signal
    import numpy as np
    import myWindowFuncs
    

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
    


    if figures is None:
        fig(label= str(window) if label is None else label)
    
    ax_wf.plot(
        fir/np.abs(fir).max(), 
        label= "wf ({window} window)".format(window= str(window))
    )
    ax_wf.plot(
        win/np.abs(win).max(),
        label= "{window} window".format(window= str(window))
    )
    
    ax_wf.legend()    
    
    inversefir = fir.copy()
    inversefir[int((n_pts-1)/2)] -= 1.0
    
    import audioSpectralTools as AST
    frequencies, spec = AST.audio_fft(AST.pad(fir, 65536), normalize= 'filter')
    frequencies, invspec = AST.audio_fft(AST.pad(inversefir, 65536), normalize= 'filter')
    
    #import uuid
    #id = uuid.uuid4()
    ax_sp.plot(
        np.append(frequencies, frequencies[::-1]), 
        np.append(spec, invspec[::-1]), 
        label= str(window)
    )
    ax_sp.axvline(250.0, color='#00ff00ff')
    ax_sp.legend()

    import matplotlib.pyplot as plt
    tight_layout()
    
def save():
    figures[0].savefig(r'S:\tmp\{ft}.png'.format(ft=figures[0].get_label()))
    figures[0].clear()
    import matplotlib.pyplot as plt
    plt.close()
    


def on_close(event):
    global figures
    figures = None

def tight_layout():
    for fig in figures:
        fig.tight_layout()