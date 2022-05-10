# fir_crossover_design
my fir filter crossover design tools and experiments (mainly with scipy)

## story

I wanted to try out a linear phase crossover for my dsp for my audio system. 
So i dived into fir filter design a little bit, and generated a whole ton of graphs.
Might as well share it with the world, so here it comes.

My dsp is adau1701 from analog devices, programmed with sigma studio. 
I needed a crossover between the (single) woofer driver and full-range drivers, at around 250 Hz. 
Adau1701 has quite some compute power, but fir filters can eat it up a lot of it fast.
Also, a long linear-phase fir filter causes audio delay, which is also undesirable.
Yet, the longer the filter, the sharper the crossover, which sound like a good thing when considering audio interference.
So, i want a sharpest crossover for a given length of the filter.

The concept of the crossover is very simple. I pass the input audio through a low-pass filter, and that goes to the woofer (with some extra correction after).
Then i delay the input signal by the delay of LPF (which is half the filter length), and subtract out the LPF-ed signal.
This gives the high-pass complement of the filter, that sums together perfectly with the LPF-ed signal to reconstruct the original (a "subtractive crossover" - that summation should be happening in the air).
The best part about it is that i can handle the full stereo crossover with just one fir LPF (with a slight problem that bass in the side channel will get through into the mid drivers, which isn't a problem for me right now, but can be filtered out with an iir filter if really necessary).

I figured out that my dsp program leaves about 750-ish taps for fir filtering. So my design goal was 250 Hz low-pass fir filter with 731 taps.

I found three methods of constructing the fir in scipy. 

* The window method `firwin`
* `remez`, which seems to actually be [Parks-McClellan filter design algorithm](https://en.wikipedia.org/wiki/Parks%E2%80%93McClellan_filter_design_algorithm)
* least-squares algorithm `firls` 

The window method lets me choose a window to tame side-lobes (spectral leakage) caused by the cropping of the sinc function by the filter length.
There is a ton of windows to choose from, and i had a hard time finding out how each one will affect the crossover, so i did it the easy way - computed them all, and plotted their spectra.
All of them are in 'gallery' directory of the repo, here come a few of them.

## filter design gallery

First is "boxcar", which is no window at all - steepest crossover but high leakage (though, it can get even steeper!)

![boxcar aka no window at all fir crossover](/gallery/731pts%20250hz/boxcar.png)

Next, a few of the standard windows provided by scipy.

![tukey windows fir crossover](/gallery/731pts%20250hz/tukey%20series.png)

![slepian windows fir crossover](/gallery/731pts%20250hz/slepian%20series.png)

![flattop window fir crossover](/gallery/731pts%20250hz/flattop.png)

![kaiser window fir crossover](/gallery/731pts%20250hz/kaiser%20series.png)

Then i tried inventing a window function. After a bit of optimisation, this produced the best compromise between steepness and leakage, in my opinion.

![invendelirium1 window crossover vs tukey 0.3](/gallery/731pts%20250hz/invendelirium1_0.2_0.5_vs_tukey_0.3.png)

This will be the standard i'll compare the other methods to.

Next, i tried `remez`, which [is regarded as "probably the most widely used FIR filter design method" by dspguru.com](https://dspguru.com/dsp/faqs/fir/design/)

![remez or Parks-McClellan fir crossover](/gallery/731pts%20250hz/remez_70_invendelirium1_0.2_0.5.png)

I have tuned it to match the steepness of the best window-design crossover. It is very nice near the crossover, but the amount of ripple at high frequencies is worrying. 
It is a comb filter, and probably can be ignored for loudspeakers because there will be a lot more comb filtering due to room reflections anyway, but i just don't like it.

And now, the least-squares:

![least-squares fir crossover](/gallery/731pts%20250hz/ls-30_vs_invendelirium1-0.2-0.5.png)

Again, tuned to match the steepness of the best window-designed crossover. Very nice result, about as good, with very little effort!

So, my recommended fir crossover design command is (so far):

```
fir = scipy.signal.firls(
    731, 
    [0, 250 - 30/2, 
    250 + 30/2, 44100/2],
    [1.0, 1.0, 0.0, 0.0],
    fs=44100
)
```

## replicating my results / designing your filter 

So, you want a fir crossover, but you have a different priorities and a different crossover frequency? 
Well, here's a quick guide on how to get these nice graphs, and this is what this repo is all about.

0. you'll need scipy and matplotlib installed

1. place all the .py files of the repo somewhere they can be directly imported from. Except maybe InitGui.py and window-list.py

2. enter the console, and interactively run some of these commands:

`import plotfir` - first and foremost

`plotfir.fs = 48000` - if you need a different sample rate

`plotfir.plot_firwin(window= ('barthann'))`
This displays a plot (waveform and spectrum) of a fir filter generated with the window method. Further calls get overlaid onto what's already on screen.

`plotfir.plot_remez(t_width = 70)`, `plotfir.plot_firls(t_width = 30)` - same, but the other two methods.

`plotfir.fig()` - start a new figure. You can instead just close the old figure if you don't need it anymore.

`plotfir.plot_fir(fir, win, label):` - plot a fir filter that you designed somehow. (`fir` must be a numpy.array of the filter taps; `win` is the window function which will be plotted to the waveform plot, use `None` if you don't want it; `label` is for legend)

window-list.py contains a bunch of these commands that i've used to generate the figures you see above.

InitGui.py is related to how i use this repo - i install it as a freecad addon (convenient, because FreeCAD already packs in matplotlib and scipy).

Be prepared to manually edit plotfir.py to your needs, because it was written as a tinker tool, and is not general-purpose at all.

To save your fir filter as a text file, you may find this quick snippet helpful:

```
import scipy.signal

fir = scipy.signal.firls(
    731,                  # filter length
    [0, 250 - 30/2,       # 250 is xover frequency, 30 is xover width
    250 + 30/2, 44100/2],
    [1.0, 1.0, 0.0, 0.0],
    fs=44100              # sample rate
)

import numpy

numpy.savetxt(
    r'C:\path\to\somewhere\fir.txt',  
    fir
)
```
