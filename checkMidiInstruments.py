import os
import mido


def analyze_midi_file(file_path):
    try:
        # Load the MIDI file
        mid = mido.MidiFile(file_path)
        
        # Set to store unique instruments
        instruments = set()
        
        # Iterate through all tracks and messages in the MIDI file
        for track in mid.tracks:
            for msg in track:
                # Check for program_change messages which indicate instrument changes
                if msg.type == 'program_change':
                    # MIDI program numbers are 0-127, but are conventionally displayed as 1-128
                    program_num = msg.program + 1
                    channel = msg.channel
                    
                    # Channel 9 (or 10 in 1-based numbering) is reserved for percussion
                    if channel == 9:
                        instrument_name = f"Percussion (Channel 10)"
                    else:
                        instrument_name = f"{program_num}: {get_instrument_name(program_num)}"
                    
                    instruments.add(instrument_name)
        
        # Print the filename and list of instruments
        print(f"\nFile: {file_path}")
        if instruments:
            print("Instruments:")
            for instrument in sorted(instruments):
                print(f"  - {instrument}")
        else:
            print("No instruments found in this file.")
            
    except Exception as e:
        print(f"\nError reading {file_path}: {str(e)}")

def analyze_midi_files(directory):
    """
    Analyze all MIDI files in the given directory and print the filename
    along with a list of unique instruments used in each file.
    
    Args:
        directory (str): Path to the directory containing MIDI files
    """
    # Check if directory exists
    if os.path.isfile(directory):
        analyze_midi_file(directory)
        return


    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        return
        
    # Get all MIDI files in the directory
    midi_files = [file for file in os.listdir(directory) 
                  if file.lower().endswith(('.mid', '.midi'))]
    
    if not midi_files:
        print(f"No MIDI files found in '{directory}'.")
        return
    
    # Process each MIDI file
    for midi_file in midi_files:
        file_path = os.path.join(directory, midi_file)
        analyze_midi_file(file_path)

def get_instrument_name(program_num):
    """
    Return the standard name for a given MIDI program number (1-128).
    
    Args:
        program_num (int): MIDI program number (1-128)
    
    Returns:
        str: The name of the instrument
    """
    # General MIDI Level 1 instrument names
    instrument_names = [
        # Piano (1-8)
        "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano",
        "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet",
        # Chromatic Percussion (9-16)
        "Celesta", "Glockenspiel", "Music Box", "Vibraphone",
        "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
        # Organ (17-24)
        "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ",
        "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",
        # Guitar (25-32)
        "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)",
        "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar",
        "Distortion Guitar", "Guitar Harmonics",
        # Bass (33-40)
        "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass",
        "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
        # Strings (41-48)
        "Violin", "Viola", "Cello", "Contrabass",
        "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
        # Ensemble (49-56)
        "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2",
        "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
        # Brass (57-64)
        "Trumpet", "Trombone", "Tuba", "Muted Trumpet",
        "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2",
        # Reed (65-72)
        "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax",
        "Oboe", "English Horn", "Bassoon", "Clarinet",
        # Pipe (73-80)
        "Piccolo", "Flute", "Recorder", "Pan Flute",
        "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina",
        # Synth Lead (81-88)
        "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)",
        "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",
        # Synth Pad (89-96)
        "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)",
        "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",
        # Synth Effects (97-104)
        "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)",
        "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
        # Ethnic (105-112)
        "Sitar", "Banjo", "Shamisen", "Koto",
        "Kalimba", "Bagpipe", "Fiddle", "Shanai",
        # Percussive (113-120)
        "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock",
        "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal",
        # Sound Effects (121-128)
        "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet",
        "Telephone Ring", "Helicopter", "Applause", "Gunshot"
    ]
    
    # Adjust program_num to 0-based index
    index = program_num - 1
    
    if 0 <= index < len(instrument_names):
        return instrument_names[index]
    else:
        return "Unknown Instrument"

if __name__ == "__main__":
    # Ask the user for the directory containing MIDI files
    midi_directory = "C:/Users/dongg/Documents/UROPSP25/PokemonHarmonizer/pokemon_midis/"
    analyze_midi_files(midi_directory)