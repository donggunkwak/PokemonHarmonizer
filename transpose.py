import os
import shutil
import mido

# Configuration variables - modify these paths as needed
INPUT_DIR = "./pokemon_midis"  # Directory containing original MIDI files
OUTPUT_DIR = "./pokemon_midis_transposed"  # Directory where transposed files will be saved

def transpose_midi_files(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
    """
    Transposes all MIDI files in input_dir to all 12 keys,
    saving the results in output_dir with appropriate naming.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Get list of MIDI files in input directory
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return
        
    midi_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.mid') or f.lower().endswith('.midi')]
    
    if not midi_files:
        print(f"No MIDI files found in {input_dir}")
        return
    
    print(f"Found {len(midi_files)} MIDI files. Beginning transposition...")
    
    # Process each MIDI file
    for midi_file in midi_files:
        file_path = os.path.join(input_dir, midi_file)
        file_name, file_ext = os.path.splitext(midi_file)
        
        print(f"Processing {midi_file}...")
        
        # Make a copy with +0 (original key)
        output_file = os.path.join(output_dir, f"{file_name}+0{file_ext}")
        shutil.copy2(file_path, output_file)
        
        # Process all other transpositions (1-11 semitones up)
        for i in range(1, 12):
            try:
                # Load the MIDI file
                midi_data = mido.MidiFile(file_path)
                
                # Create a new MIDI file for the transposed version
                transposed_midi = mido.MidiFile(ticks_per_beat=midi_data.ticks_per_beat)
                
                # Process each track
                for track in midi_data.tracks:
                    new_track = mido.MidiTrack()
                    transposed_midi.tracks.append(new_track)
                    
                    # Process each message in the track
                    for msg in track:
                        # Clone the message
                        new_msg = msg.copy()
                        
                        # Transpose note_on and note_off messages
                        if msg.type == 'note_on' or msg.type == 'note_off':
                            # Apply transposition, keeping notes in valid MIDI range (0-127)
                            new_note = msg.note + i
                            if 0 <= new_note <= 127:
                                new_msg.note = new_note
                        
                        # Add the message to the new track
                        new_track.append(new_msg)
                
                # Save the transposed MIDI file
                output_file = os.path.join(output_dir, f"{file_name}+{i}{file_ext}")
                transposed_midi.save(output_file)
                
                print(f"  Created {file_name}+{i}{file_ext}")
                
            except Exception as e:
                print(f"Error processing {midi_file} at transposition +{i}: {str(e)}")
    
    print("Transposition complete!")

if __name__ == "__main__":
    # You can run the script directly with the configured paths
    transpose_midi_files()
    
    # Alternatively, you can still override the paths when calling the function:
    # transpose_midi_files("/custom/input/path", "/custom/output/path")