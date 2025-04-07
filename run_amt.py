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
from anticipation.convert import events_to_midi


model_path = './amt_PKMN_Harmonizer_Small/checkpoint-1000'
model = AutoModelForCausalLM.from_pretrained(model_path).cuda()

length = 20 # time in seconds
events1, melody =extract_instruments(generate(model, start_time=0, end_time=length, top_p=.98, active_instruments=[0]),[0])
accompaniment = generate(model, start_time=0, end_time=length, controls=melody, top_p=.98, active_instruments=[1,40,41,42,43])
# events = generate(model, start_time=0, end_time=length, top_p=.98, active_instruments=[0,1])
events = ops.clip(ops.combine(accompaniment, melody), 0, 20, clip_duration=True)

mid = events_to_midi(events)
mid.save('generated.mid')


mel = events_to_midi(melody)
mel.save('melody.mid')