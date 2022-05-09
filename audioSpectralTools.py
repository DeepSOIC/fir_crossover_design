def plotWF(wf):
    import matplotlib.pyplot as plt
    import numpy as np
    
    plt.figure()
    plt.plot(wf)
    plt.title("waveform")
    plt.ylabel("amplitude")
    plt.xlabel("time [samples]")
    
    plt.show()

def plotSpectrumA(frequencies, spec, title= "spectrum", label= None):
    import matplotlib.pyplot as plt
    import numpy as np
    plt.figure(label)
    plt.gca(
        label='spectral',
        xscale='log', xlim=(20.0, 20e3),
        yscale='log', ylim=(1e-5, 3)
    )
    plt.plot(frequencies, spec)
    plt.title(title)
    plt.xlabel("frequency [Hz]")
    plt.ylabel("amplitude")
    plt.show()

def resample_log(frequencies, energies, num_points):
    """resample_log(frequencies, energies, num_points): returns tuple (frequencies, energies). 
    Smoothes out the data by doing adaptive adjacent averaging. The less num_points, the more smoothing; 
    smoothing gets more aggressive at higher frequencies because of increasing density of points in log scale.
    
    energies: the spectrum. List of floats, energies per unit of frequency
    
    frequencies: list of corresponding frequencies (linear spacing is assumed!)
    
    num_points sets the target point density (actual number of points will be less). """
    
    import math
    from math import log as ln
    cum = 0.0
    cum_n = 0
    
    output_amps = np.zeros(num_points)
    output_freqs = np.zeros(num_points)
    n = 0
    
    f_from = freqs[1] #skip first point, assume it's zero
    f_to = freqs[len(freqs)]
    ln_step = abs(ln(f_to) - ln(f_from)) / num_points
    
    f_prev = f_from
    ln_f_prev = ln(f_prev)
    
    #process: accumulate data values till frequency span covers ln_step; when it overcomes the span, the accumulated data average is dumped to output
    for i in range(1, len(amps)):
        f = freqs[i]
        ln_f = ln(f)
        if abs(ln_f - ln_f_prev) > ln_step:
            output_amps[n] = cum/cum_n
            output_freqs[n] = sqrt(freqs[i-1]*fprev) #log average of the frequency span
            n += 1
            cum = 0.0
            cum_n = 0
            f_prev = f
            ln_f_prev = ln_f
        cum += amps[i]
        cum_n += 1
    
    return (output_freqs[0:n], output_amps[0:n])

def audio_fft(waveform, fs = 44100.0, normalize = 'power', qDensity = False):
    """audio_fft(waveform, fs = 44100.0, normalize = 'power'): returns tuple (frequency_coord, amplitude). 
    waveform: numpy.array
    fs: sample rate in hz
    normalize can be either 'voltage' (V/rtHz), 'power' (V^2/Hz), 'energy' (V^2*s/Hz), or 'max' (amplitude spectrum, peak is made equal to 1).
    qDensity: convert per-hz to per-delta-ln units
    """
    
    timestep = 1/fs

    import numpy as np

    if normalize == 'filter':
        fft=np.fft.rfft(waveform)
        amps = np.abs(fft)
        amps[0] = amps[0] / 2
        freqs = np.linspace(0,fs/2,len(fft))
        return freqs, amps
        
    datare = waveform*np.sqrt(timestep) # each point is square root of point energy. Point energy is U^2*dt. The idea is that fft preserves sum of squares, and we want to preserve total energy.
    fft=np.fft.rfft(datare)/np.sqrt(len(datare))
    freqs = np.linspace(0,fs/2,len(fft))
    datare = None #cleanup
    ffte = abs(fft)**2 * 2 #convert amplitudes to energies. I'm not quite sure why multiplying by 2 is needed. The 0-th item shouldn't be doubled, but we lose it later anyway, so doesn't matter.
    ffte[0] = ffte[0] / 2
    fft = None #cleanup
    
    # apply frequency scaling, by first converting to per delta-ln spectrum, then to per-hz spectrum
    #fftxlog = np.array([ffte[i]*(i) for i in xrange(len(fft))])
    #energy_hz = np.array([fftxlog[i]/(i/(len(waveform)*timestep)) for i in xrange(len(fft))])
    #...same but more efficient:
    energy_hz = ffte*len(waveform)*timestep
    ffte = None #cleanup
    
    if qDensity:
        energy = np.array([  energy_hz[i]*freqs[i]   for i in range(len(energy_hz))  ])
    else:
        energy = energy_hz
    
    if normalize == 'energy':
        result = energy
    elif normalize == 'power':
        #convert energy spectrum into power spectrum (divide by time duration of waveform)
        result = energy/(len(waveform)*timestep)
    elif normalize == 'voltage':
        #convert energy spectrum into power spectrum (divide by time duration of waveform), then into voltage spectrum (sqrt).
        result = np.sqrt(energy/(len(waveform)*timestep))
    elif normalize == 'max':
        vdens = np.sqrt(energy/(len(waveform)*timestep))
        result = vdens/vdens.max()
    else:
        raise KeyError(repr(normalize))
    
    return freqs, result

def pad(waveform, num_points):
    import numpy as np
    return np.append(waveform, np.zeros(num_points - len(waveform)))
