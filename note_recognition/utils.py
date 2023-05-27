import array
from collections import Counter

import numpy as np
import scipy
from scipy.fft import fft as ftt_func
from pydub.utils import get_array_type
from Levenshtein import distance

NOTES = {
    "C0": 16.351597831287414,
    "C0#": 17.323914436054505,
    "D0": 18.354047994837977,
    "D0#": 19.445436482630058,
    "E0": 20.601722307054366,
    "F0": 21.826764464562746,
    "F0#": 23.12465141947715,
    "G0": 24.499714748859326,
    "G0#": 25.956543598746574,
    "A0": 27.5,
    "A0#": 29.13523509488062,
    "B0": 30.86770632850775,
    "C1": 32.70319566257483,
    "C1#": 34.64782887210901,
    "D1": 36.70809598967594,
    "D1#": 38.890872965260115,
    "E1": 41.20344461410875,
    "F1": 43.653528929125486,
    "F1#": 46.2493028389543,
    "G1": 48.999429497718666,
    "G1#": 51.91308719749314,
    "A1": 55,
    "A1#": 58.27047018976124,
    "B1": 61.7354126570155,
    "C2": 65.40639132514966,
    "C2#": 69.29565774421802,
    "D2": 73.41619197935188,
    "D2#": 77.78174593052023,
    "E2": 82.4068892282175,
    "F2": 87.30705785825097,
    "F2#": 92.4986056779086,
    "G2": 97.99885899543733,
    "G2#": 103.82617439498628,
    "A2": 110,
    "A2#": 116.54094037952248,
    "B2": 123.47082531403103,
    "C3": 130.8127826502993,
    "C3#": 138.59131548843604,
    "D3": 146.8323839587038,
    "D3#": 155.56349186104046,
    "E3": 164.81377845643496,
    "F3": 174.61411571650194,
    "F3#": 184.9972113558172,
    "G3": 195.99771799087463,
    "G3#": 207.65234878997256,
    "A3": 220,
    "A3#": 233.08188075904496,
    "B3": 246.94165062806206,
    "C4": 261.6255653005986,
    "C4#": 277.1826309768721,
    "D4": 293.6647679174076,
    "D4#": 311.1269837220809,
    "E4": 329.6275569128699,
    "F4": 349.2282314330039,
    "F4#": 369.9944227116344,
    "G4": 391.99543598174927,
    "G4#": 415.3046975799451,
    "A4": 440,
    "A4#": 466.1637615180899,
    "B4": 493.8833012561241,
    "C5": 523.2511306011972,
    "C5#": 554.3652619537442,
    "D5": 587.3295358348151,
    "D5#": 622.2539674441618,
    "E5": 659.2551138257398,
    "F5": 698.4564628660078,
    "F5#": 739.9888454232688,
    "G5": 783.9908719634985,
    "G5#": 830.6093951598903,
}

def is_prime(number):
    if number < 2:
        return False
    for i in range(2, number):
        if number % i == 0:
            # number is not prime
            return False
    return True

def give_note_after_diff(note, diff):
    take_note = note[0]
    had_sharp = len(note) == 3
    the_chosen = ""
    minim = 100000
    for i in range(5):
        note_to_test = take_note + str(i)
        next_note = take_note + str(i + 1)
        if abs(NOTES[note_to_test] - diff) < minim:
            minim = abs(NOTES[note_to_test] - diff)
            the_chosen = next_note
    if had_sharp:
        the_chosen += "#"

    if the_chosen != note:
        # go to the next note
        take_note = note[0]
        take_number = int(note[1])
        new_note = take_note + str(take_number + 1)
        if had_sharp:
            new_note += "#"

        if NOTES[new_note] < 400:
            the_chosen = new_note
        else:
            the_chosen = note
    if diff < 10:
        the_chosen = note

    return the_chosen


def frequency_spectrum(sample, max_frequency=800):
    """
    Derive frequency spectrum of a signal pydub.AudioSample
    Returns an array of frequencies and an array of how prevelant that frequency is in the sample
    """
    # Convert pydub.AudioSample to raw audio data
    # Copied from Jiaaro's answer on https://stackoverflow.com/questions/32373996/pydub-raw-audio-data
    bit_depth = sample.sample_width * 8
    array_type = get_array_type(bit_depth)
    raw_audio_data = array.array(array_type, sample._data)
    n = len(raw_audio_data)

    # Compute FFT and frequency value for each index in FFT array
    # Inspired by Reveille's answer on https://stackoverflow.com/questions/53308674/audio-frequencies-in-python
    freq_array = np.arange(n) * (float(sample.frame_rate) / n)  # two sides frequency range
    freq_array = freq_array[: (n // 2)]  # one side frequency range

    raw_audio_data = raw_audio_data - np.average(raw_audio_data)  # zero-centering
    freq_magnitude = ftt_func(raw_audio_data)  # fft computing and normalization
    freq_magnitude = freq_magnitude[: (n // 2)]  # one side

    if max_frequency:
        max_index = int(max_frequency * n / sample.frame_rate) + 1
        freq_array = freq_array[:max_index]
        freq_magnitude = freq_magnitude[:max_index]

    freq_magnitude = abs(freq_magnitude)
    freq_magnitude = freq_magnitude / np.sum(freq_magnitude)
    return freq_array, freq_magnitude


def classify_note_attempt_1(freq_array, freq_magnitude):
    i = np.argmax(freq_magnitude)
    f = freq_array[i]
    print("frequency {}".format(f))
    print("magnitude {}".format(freq_magnitude[i]))
    return get_note_for_freq(f)


def classify_note_attempt_2(freq_array, freq_magnitude):
    note_counter = Counter()
    for i in range(len(freq_magnitude)):
        if freq_magnitude[i] < 0.01:
            continue
        note = get_note_for_freq(freq_array[i])
        if note:
            note_counter[note] += freq_magnitude[i]
    return note_counter.most_common(1)[0][0]


def classify_note_attempt_3(freq_array, freq_magnitude):
    min_freq = 82
    note_counter = Counter()
    for i in range(len(freq_magnitude)):
        if freq_magnitude[i] < 0.01:
            continue

        for freq_multiplier, credit_multiplier in [
            (1, 1),
            (1 / 3, 3 / 4),
            (1 / 5, 1 / 2),
            (1 / 6, 1 / 2),
            (1 / 7, 1 / 2),
        ]:
            freq = freq_array[i] * freq_multiplier
            if freq < min_freq:
                continue
            note = get_note_for_freq(freq)
            if note:
                note_counter[note] += freq_magnitude[i] * credit_multiplier

    return note_counter.most_common(1)[0][0]


# If f is within tolerance of a note (measured in cents - 1/100th of a semitone)
# return that note, otherwise returns None
# We scale to the 440 octave to check
def get_note_for_freq(f, tolerance=33):
    # Calculate the range for each note
    tolerance_multiplier = 2 ** (tolerance / 1200)
    note_ranges = {
        k: (v / tolerance_multiplier, v * tolerance_multiplier) for (k, v) in NOTES.items()
    }

    # Get the frequence into the 440 octave
    range_min = note_ranges["E2"][0]
    range_max = note_ranges["G4"][1]
    if f < range_min:
        while f < range_min:
            f *= 2
    else:
        while f > range_max:
            f /= 2

    # Check if any notes match
    for (note, note_range) in note_ranges.items():
        if f > note_range[0] and f < note_range[1]:
            return note
    return None


# Assumes everything is either natural or sharp, no flats
# Returns the Levenshtein distance between the actual notes and the predicted notes
def calculate_distance(predicted, actual):
    # To make a simple string for distance calculations we make natural notes lower case
    # and sharp notes cap
    def transform(note):
        if "#" in note:
            return note[0].upper()
        return note.lower()

    return distance(
        "".join([transform(n) for n in predicted]), "".join([transform(n) for n in actual]),
    )

# Transform each note to tab
def transform_notes_to_tab():
    notes = ["E2", "F2", "F2#", "G2", "A2", "A2#", "B2", "C3", "D3", "D3#", "E3", "F3", "G3", "G3#", "A3", "A3#", "B3", "C4", "C4#", "D4", "E4", "F4", "F4#", "G4"]
    # tabs will be in e, B, G, D, A, E order
    tabs = dict()
    for i in range(len(notes)):
        print(notes[i], end = ", ")
        if i == 0:
            string = 5
        else:
            string = 5 - i // 4
        fret = i % 4
        tabs[ notes[i] ] = ["-", "-", "-", "-", "-", "-"]
        tabs[ notes[i] ][string] = str(fret)
    return tabs

def transform_actual_notes_to_tabs(notes, number_of_notes_per_tab=10):
    transform = transform_notes_to_tab()
    tabs = []
    note = 0
    for i in range(0, len(notes), number_of_notes_per_tab):
        tab = []
        for j in range(i, min(i + number_of_notes_per_tab, len(notes))):
            tab.append(transform[notes[j]])
        tabs.append(tab)
    return tabs

def transform_tabs_to_text(notes, number_of_notes_per_tab=10):
    tabs = transform_actual_notes_to_tabs(notes, number_of_notes_per_tab)
    text = ""
    notes = ["e", "B", "G", "D", "A", "E"]
    for tab in tabs:
        for j in range(6):
            text += notes[j] + "|--"
            for step in tab:
                text += step[j] + "--"
            text += "\n"
        text += "\n" * 2
    return text
