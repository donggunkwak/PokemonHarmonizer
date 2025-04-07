from anticipation.config import MAX_INSTR
from anticipation.vocab import CONTROL_OFFSET, NOTE_OFFSET

with open('./tokenized-events-pokemon_midis_transposed.txt') as f:
    lines = f.readlines()
tokens = []
for line in lines[1:]:
    tokens.append([int(i)-CONTROL_OFFSET if int(i)>=CONTROL_OFFSET else int(i) for i in line.split(" ")[1:]])

instruments = set()
for tokenLine in tokens:
    instruments.update([(i-NOTE_OFFSET)//MAX_INSTR for i in tokenLine[2::3]])
print(instruments)