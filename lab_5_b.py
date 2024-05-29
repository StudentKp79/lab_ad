from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, CheckboxGroup, Button
import numpy as np
from scipy.signal import butter, filtfilt
import sys
import subprocess


def harmonic(t, amplitude, frequency, phase):
    return amplitude * np.sin(2 * np.pi * frequency * t + phase)


def create_noise(t, noise_mean, noise_covariance):
    return np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))


def harmonic_with_noise(t, amplitude, frequency, phase=0, noise_mean=0, noise_covariance=0.1, noise=None):
    harmonic_signal = harmonic(t, amplitude, frequency, phase)
    if noise is not None:
        return harmonic_signal + noise
    else:
        global noise_g
        noise_g = create_noise(t, noise_mean, noise_covariance)
        return harmonic_signal + noise_g


def moving_avg(data, window_size):
    moving_avg = []
    window_size = int(window_size)
    for i in range(len(data)):
        if i < window_size:
            avg = np.mean(data[:i + 1])
        else:
            avg = np.mean(data[i - window_size + 1:i + 1])
        moving_avg.append(avg)
    return moving_avg


initial_amplitude = 1.0
initial_frequency = 1.0
initial_phase = 0.0
initial_noise_mean = 0.0
initial_noise_covariance = 0.1
noise_g = None

t = np.linspace(0, 10, 1000)
sampling_frequency = 1 / (t[1] - t[0])

plot = figure(title="Harmonic Signal with Noise and Lowpass Filter", x_axis_label='Time', y_axis_label='Amplitude',
              width=1500, height=500, sizing_mode="fixed")

harmonic_line = plot.line(t, harmonic(t, initial_amplitude, initial_frequency, initial_phase), line_width=2,
                          color='black', line_dash='dotted', legend_label='Harmonic line')

with_noise_line = plot.line(t, harmonic_with_noise(t, initial_amplitude, frequency=initial_frequency,
                                                   phase=initial_phase, noise_mean=initial_noise_mean,
                                                   noise_covariance=initial_noise_covariance, noise=None),
                            line_width=2, color='red', legend_label='Signal with noise')

filtered_signal = moving_avg(with_noise_line.data_source.data['y'], sampling_frequency)
l_filtered = plot.line(t, filtered_signal, line_width=2, color='#0f16e6', legend_label='Filtered Signal')

s_amplitude = Slider(title="Amplitude", value=initial_amplitude, start=0.1, end=10.0, step=0.1)
s_frequency = Slider(title="Frequency", value=initial_frequency, start=0.1, end=10.0, step=0.1)
s_phase = Slider(title="Phase", value=initial_phase, start=0.0, end=2 * np.pi, step=0.1)
s_noise_mean = Slider(title="Noise Mean", value=initial_noise_mean, start=-1.0, end=1.0, step=0.1)
s_noise_covariance = Slider(title="Noise Covariance", value=initial_noise_covariance, start=0.0, end=1.0, step=0.1)
s_cutoff_frequency = Slider(title="window_size", value=3, start=1, end=35.0, step=1)

cb_show_noise = CheckboxGroup(labels=['Show Noise'], active=[0])
button_regenerate_noise = Button(label='Regenerate Noise')
button_random_params = Button(label='Random Params')
button_reset = Button(label='Reset')


def update(attrname, old, new):
    amplitude = s_amplitude.value
    frequency = s_frequency.value
    phase = s_phase.value

    noise_mean = s_noise_mean.value
    noise_covariance = s_noise_covariance.value

    global initial_noise_mean, initial_noise_covariance, noise_g

    if initial_noise_covariance != noise_covariance or initial_noise_mean != noise_mean:
        initial_noise_mean = noise_mean
        initial_noise_covariance = noise_covariance
        noise_g = create_noise(t, noise_mean, noise_covariance)

    show_noise = bool(new)
    harmonic_line.data_source.data['y'] = harmonic(t, amplitude, frequency, phase)
    with_noise_line.data_source.data['y'] = harmonic_with_noise(t, amplitude, frequency, phase,
                                                                noise_mean, noise_covariance, noise_g)
    with_noise_line.visible = show_noise

    cutoff_frequency = s_cutoff_frequency.value
    filtered_signal = moving_avg(with_noise_line.data_source.data['y'], cutoff_frequency)
    l_filtered.data_source.data['y'] = filtered_signal


def regenerate_noise():
    with_noise_line.data_source.data['y'] = harmonic_with_noise(t, s_amplitude.value, s_frequency.value, s_phase.value,
                                                                s_noise_mean.value, s_noise_covariance.value)


def random_params():
    s_amplitude.value = np.random.uniform(0.1, 10.0)
    s_frequency.value = np.random.uniform(0.1, 10.0)
    s_phase.value = np.random.uniform(0.0, 2 * np.pi)
    s_noise_mean.value = np.random.uniform(-1.0, 1.0)
    s_noise_covariance.value = np.random.uniform(0.0, 1.0)
    regenerate_noise()


def reset_params():
    s_amplitude.value = initial_amplitude
    s_frequency.value = initial_frequency
    s_phase.value = initial_phase
    s_noise_mean.value = 0.0
    s_noise_covariance.value = 0.1
    s_cutoff_frequency.value = 3
    cb_show_noise.active = [0]
    regenerate_noise()


s_amplitude.on_change('value', update)
s_frequency.on_change('value', update)
s_phase.on_change('value', update)
s_noise_mean.on_change('value', update)
s_noise_covariance.on_change('value', update)
s_cutoff_frequency.on_change('value', update)

cb_show_noise.on_change('active', update)
button_regenerate_noise.on_click(regenerate_noise)
button_random_params.on_click(random_params)
button_reset.on_click(reset_params)

layout = column(plot,
                row(s_amplitude, s_frequency, s_phase),
                row(s_noise_mean, s_noise_covariance, s_cutoff_frequency),
                row(cb_show_noise, button_regenerate_noise, button_random_params, button_reset),
                sizing_mode='stretch_width', align='center')

curdoc().add_root(layout)

if __name__ == "__main__":
    with open("lab5_bokeh.py", "w", encoding="utf-8") as f:
        f.write(__import__("inspect").getsource(sys.modules[__name__]))
    subprocess.run(["bokeh", "serve", "--show", "lab_5_b.py"])
