# The Gizmore–Chappy Tiny-Time Interferometer

## A Conceptual Experiment to Search for Non-Smooth Structure in Space-Time

**Authors:** gizmore and Chappy

## Abstract

We propose a conceptual experiment to test whether space-time behaves as a perfectly smooth continuum or whether it may show discrete, noisy, or non-smooth behavior at extremely small scales.

Unlike gravitational-wave interferometers, which mainly measure changes in spatial distance or optical path length, this experiment aims to modulate **proper time**. Two coherent laser references are compared by an interferometric detector. The key observable is not a large change in distance, but a small controlled change in the rate at which time passes for the laser references.

Standard relativity predicts a smooth phase and frequency response. If space-time has a discrete or “pixelated” structure, the interesting signal would not necessarily be a large frequency shift, but a repeatable residual: tiny steps, excess phase noise, non-continuous drift, or correlations that cannot be explained by known physics.

## 1. Motivation

Modern physics usually treats space-time as continuous. However, many ideas in quantum gravity suggest that this smooth description may break down at extremely small scales.

Directly observing Planck-scale structure is far beyond current laboratory ability. Therefore, instead of trying to directly “see pixels of space-time,” we propose a precision experiment that looks for deviations from the smooth predictions of relativity and optics.

The basic question is:

**If we change the rate of time in a controlled and periodic way, does the optical phase/frequency response remain perfectly smooth?**

## 2. Main Idea

A laser can be treated as an optical clock. If two lasers experience slightly different rates of proper time, their frequencies and phases should drift relative to each other.

Near weak gravitational fields, the fractional frequency difference is approximately:

[
\frac{\Delta f}{f} \approx \frac{\Delta \Phi}{c^2}
]

where:

* ( \Delta f/f ) is the fractional frequency shift,
* ( \Delta \Phi ) is the gravitational potential difference,
* ( c ) is the speed of light.

Near the surface of a body with gravitational acceleration (g), this becomes approximately:

[
\frac{\Delta f}{f} \approx \frac{g h}{c^2}
]

where (h) is the height difference.

However, our final proposed setup does not rely on a large height difference. The experiment may be very small. The important point is not large distance, but controlled modulation of proper time.

## 3. Difference from Gravitational-Wave Interferometers

Gravitational-wave interferometers such as LIGO measure extremely small changes in spatial arm length caused by passing gravitational waves.

The Gizmore–Chappy interferometer is different in intention.

It is not primarily designed to detect stretched or compressed space. Instead, it attempts to create or sample a tiny controlled difference in **time rate**.

In simple words:

**Gravitational-wave interferometer:**
measures changing space.

**Gizmore–Chappy interferometer:**
compares changing time.

More precisely, it compares the phase/frequency drift of laser references whose proper-time rates are modulated by a gravitational potential difference.

## 4. Tiny Modulated Experiment

A static femtometer-scale height difference would produce an extremely small gravitational redshift. For example, on Earth:

[
h = 10^{-15} \text{ m}
]

gives roughly:

[
\frac{\Delta f}{f} \sim 10^{-31}
]

For an optical laser near:

[
f \sim 5 \times 10^{14} \text{ Hz}
]

this corresponds to an absolute frequency difference of only about:

[
\Delta f \sim 5 \times 10^{-17} \text{ Hz}
]

This is far too small to observe directly as an ordinary beat frequency in any practical time.

Therefore, the experiment should not depend on a static femtometer height difference alone. Instead, the better approach is to **modulate** the gravitational potential periodically.

In other words:

**Rattle time, then listen for grain.**

## 5. Orbiting Around a Satellite or Test Mass

One proposed version is to place a very small optical experiment near or around a satellite, spacecraft, or artificial test mass.

The experiment could circle the satellite or mass. As it moves, the local gravitational potential changes periodically. Standard relativity predicts a smooth periodic phase/frequency modulation.

For a mass (M), the gravitational potential is approximately:

[
\Phi(r) = -\frac{GM}{r}
]

where:

* (G) is the gravitational constant,
* (M) is the mass of the satellite or test mass,
* (r) is the distance from its center.

The expected fractional frequency modulation between two positions (r_1) and (r_2) is:

[
\frac{\Delta f}{f}
\approx
\frac{GM}{c^2}
\left(
\frac{1}{r_1} - \frac{1}{r_2}
\right)
]

This creates a known periodic signal. The detector can then compare measured phase/frequency behavior against the smooth prediction.

The main target becomes the residual:

[
\text{residual} =
\text{measured signal}
----------------------

\text{smooth relativistic prediction}
]

## 6. Lock-In Style Detection

A periodic modulation has an advantage over a static effect.

If the system is “rattled” at a known frequency, the detector can search at exactly that frequency and its harmonics. This is similar in spirit to lock-in detection.

The expected signal is:

[
\Phi(t) = \Phi_0 + \Delta\Phi \sin(\omega t)
]

and therefore:

[
\frac{\Delta f(t)}{f}
\approx
\frac{\Delta\Phi(t)}{c^2}
]

Standard physics predicts a smooth sinusoidal response. A possible non-smooth space-time structure might appear as:

* step-like phase changes,
* excess phase noise,
* non-continuous residuals,
* correlated irregularities,
* deviations synchronized with the modulation.

The important observable is primarily **phase**, with frequency drift as the related clock-rate measurement. Amplitude is secondary, because amplitude is more easily affected by ordinary optical imperfections.

## 7. Why a Space or Lagrange-Point Environment?

A quiet space environment may reduce some Earth-based noise sources such as seismic vibration, atmospheric turbulence, thermal gradients, and human-made mechanical disturbances.

A Lagrange-point spacecraft, drag-free satellite, or quiet orbital platform could provide a cleaner environment for long integration times.

However, a Lagrange point does not mean “no gravity.” It means gravitational and orbital effects balance in a useful way. The relevant quantity is still the gravitational potential and its gradient across the experiment.

The advantage of space is not necessarily a stronger signal. The advantage is control, quietness, and long-duration measurement.

## 8. Expected Difficulty

The expected ordinary gravitational frequency shifts are extremely small. A target such as:

[
10^{-38}
]

as a direct fractional frequency measurement is far beyond current straightforward measurement.

For an optical laser:

[
f \sim 5 \times 10^{14} \text{ Hz}
]

a fractional shift of:

[
10^{-38}
]

would imply:

[
\Delta f \sim 5 \times 10^{-24} \text{ Hz}
]

This is not realistically observable as a simple beat frequency.

Therefore, the experiment should not be presented as a simple direct measurement of a huge frequency change. Instead, it should be presented as a residual-search experiment:

1. Create a controlled proper-time modulation.
2. Predict the smooth relativistic phase/frequency response.
3. Measure the optical phase with extreme precision.
4. Subtract all known effects.
5. Search the residual for non-smooth behavior.

## 9. Experimental Requirements

A practical version would require:

* ultra-stable lasers or optical clocks,
* strong thermal isolation,
* vibration isolation,
* careful modeling of Doppler effects,
* careful modeling of path-length changes,
* stable interferometric readout,
* knowledge of the nearby mass distribution,
* long integration time,
* repeated modulation cycles,
* independent reference channels to reject ordinary noise.

The experiment must distinguish true proper-time effects from ordinary optical path changes.

This is crucial. If the optical path length changes, the detector may simply measure geometry. The goal is to keep optical paths as short, symmetric, and well-modeled as possible, while modulating the clock-rate environment.

## 10. Hypothesis

The standard prediction is:

**The phase/frequency response is smooth and fully explainable by relativity, optics, and known noise sources.**

The exploratory hypothesis is:

**If space-time has a discrete or non-smooth structure, then a controlled proper-time modulation may produce residual phase/frequency behavior that is not perfectly smooth after known physics has been subtracted.**

This could appear as:

[
\text{smooth prediction} + \text{irreducible residual}
]

The residual would be the object of interest.

## 11. Conclusion

The Gizmore–Chappy Proper-Time Interferometer is a conceptual proposal for a precision experiment that focuses on time-rate modulation rather than spatial arm-length measurement.

The experiment is not expected to directly observe Planck-scale pixels of space-time. Instead, it searches for unexplained residuals in a highly controlled optical phase/frequency measurement.

The strongest form of the idea is:

**Do not stretch space. Rattle time. Compare the phase. Search the residual.**

If the result is perfectly smooth, it confirms standard physics within the experimental limits.

If the result contains repeatable, non-smooth, unexplained residuals, it may point toward new physics worth deeper investigation.
