from transformers import AutoModelForCausalLM

import math

import torch
import torch.nn.functional as F

from tqdm import tqdm

from anticipation import ops
from anticipation.config import *
from anticipation.vocab import *
from anticipation.tokenize import extract_instruments
from anticipation.convert import events_to_midi,midi_to_events
from custom_sample import generate, add_token


model = AutoModelForCausalLM.from_pretrained(
    "donggunkwak/PokemonHarmonizer",
    subfolder="amt_PKMN_Harmonizer_Small/checkpoint-3000"
).cuda()

length = 10 # time in seconds
# _, segment = extract_instruments(ops.clip(midi_to_events('./pokemon_midis/Hearthome-City.mid'),
#                    0,40), [0])

melody =generate(model, start_time=0, end_time=length, top_p=.98, active_instruments=[0], monophony=True)
print(melody)

z = [ANTICIPATE]
top_p = 0.98
tokens = []
# result = []
harmonies = [[],[],[],[],[]]
other_instruments = [1,40,41,42,43]
current_time = 0
melody = [CONTROL_OFFSET+x for x in melody]
# anticipate everything
tokens.extend(melody)


# we generate new notes for the first note in the melody
# for t, d, n in tqdm(zip(melody[::3], melody[1::3], melody[2::3]), total=len(melody)//3):
#     print(f"Time {t-CONTROL_OFFSET}")
#     # tokens.extend([t, d, n])
#     result.extend([t-CONTROL_OFFSET, d-CONTROL_OFFSET, n-CONTROL_OFFSET])
#     for i, instr in enumerate(other_instruments):
#         new_token = add_token(model, z, tokens, top_p, current_time, active_instruments=[instr], forceTime=t-CONTROL_OFFSET, forceDuration=d-CONTROL_OFFSET)
#         tokens.extend(new_token)
#         result.extend(new_token)
#         print(f"New token: {new_token}")
#         current_time = new_token[0]

#         # save harmony
#         originalNote = n - CONTROL_OFFSET - NOTE_OFFSET
#         generatedNote = (new_token[2] - NOTE_OFFSET) - (2**7)*instr
#         diff = generatedNote - originalNote
#         harmonies[i].append((new_token[0], diff))

t, d, _ = melody[:3]

# tokens.extend([t, d, n])
for i, instr in enumerate(other_instruments):
    new_token = add_token(model, z, tokens, top_p, current_time, active_instruments=[instr], forceTime=t-CONTROL_OFFSET, forceDuration=d-CONTROL_OFFSET)
    tokens.extend(new_token)
    print(f"First chord, new token: {new_token}")
    current_time = new_token[0]

while current_time <= melody[-3] - CONTROL_OFFSET:
    new_token = add_token(model, z, tokens, top_p, current_time, active_instruments=other_instruments)
    tokens.extend(new_token)
    print(f"New token: {new_token}")
    current_time = new_token[0]

result = ops.combine([x for x in tokens if x < CONTROL_OFFSET], melody)

mid = events_to_midi(result)
mid.save('generated.mid')

# accompaniment = generate(model, start_time=0, end_time=length, controls=melody, top_p=.98, active_instruments=[1,40,41,42,43])

# events = ops.clip(ops.combine(accompaniment, melody), 0, 20, clip_duration=True)

# mid = events_to_midi(events)
# mid.save('generated.mid')