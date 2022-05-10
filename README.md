# fir_crossover_design
my fir filter crossover design tools and experiments (mainly with scipy)

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
Then i delay the input signal by the delay of LPF, and subtract out the LPF-ed signal.
This gives the high-pass complement of the filter, that sum together perfectly (a subtractive crossover).
The best part about it is that i can handle the full stereo crossover with just one fir LPF (with a slight problem that bass in the side channel will get through into the mid drivers, which isn't a problem for me right now, but can be filtered out with an iir filter if really necessary).

I figured out that my dsp program leaves about 750-ish taps for fir filtering. So my design goal was 250 Hz low-pass fir filter with 731 taps.

I found three methods of constructing the fir in scipy. 

* The window method `firwin`
* `remez`, which seems to actually be [Parks-McClellan filter design algorithm](https://en.wikipedia.org/wiki/Parks%E2%80%93McClellan_filter_design_algorithm)
* least-squares algorithm `firls` 

The window method lets me choose a window to tame side-lobes caused by cropping the sinc function by the filter length.
There is a ton of filters to choose from, and i had a hard time finding out how each one will affect the crossover, so i did it the easy way - computed them all, and plotted their spectra.
All of them are in 'gallery' directory of the repo, here come a few of them.

First is "boxcar", which is no window at all - steepest crossover but high leakage (though, it can get even steeper!)

![boxcar aka no window at all fir crossover](/gallery/731pts%20250hz/boxcar.png)

Next, a few of the standard windows provided by scipy.

![tukey windows fir crossover](/gallery/731pts%20250hz/tukey%20series.png)

![slepian windows fir crossover](/gallery/731pts%20250hz/slepian%20series.png)

![flattop window fir crossover](/gallery/731pts%20250hz/flattop.png)

![kaiser window fir crossover](/gallery/731pts%20250hz/kaiser%20series.png)

Then i tried inventing a window function. After a bit of optimisation, this produced the best compromise between steepness and leakage, in my opinion.

![invendelirium1 window crossover vs tukey 0.3](/gallery/731pts%20250hz/invendelirium1_0.2_0.5_vs_tukey_0.3.png)

This will be the standard i'll compare other methods with.

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

