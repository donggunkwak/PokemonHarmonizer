from transformers import AutoModelForCausalLM

import math

import torch
import torch.nn.functional as F

from tqdm import tqdm

from anticipation import ops
from anticipation.config import *
from anticipation.vocab import *
from anticipation.sample import generate
from anticipation.tokenize import extract_instruments
from anticipation.convert import events_to_midi,midi_to_events


model = AutoModelForCausalLM.from_pretrained(
    "donggunkwak/PokemonHarmonizer",
    subfolder="amt_PKMN_Harmonizer_Small/checkpoint-3000"
).cuda()

length = 40 # time in seconds
# _, segment = extract_instruments(ops.clip(midi_to_events('./pokemon_midis/Hearthome-City.mid'),
#                    0,40), [0])

events1, melody =extract_instruments(generate(model, start_time=0, end_time=length, top_p=.98),[0])

accompaniment = generate(model, start_time=0, end_time=length, controls=melody, top_p=.98, active_instruments=[1,40,41,42,43])

events = ops.clip(ops.combine(accompaniment, melody), 0, 20, clip_duration=True)

mid = events_to_midi(events)
mid.save('generated.mid')