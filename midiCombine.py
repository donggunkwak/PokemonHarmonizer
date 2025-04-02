#!/usr/bin/env python3
import mido
import os
import argparse
from pathlib import Path

def combine_midi_files(input_files, output_file):
    """
    Combine multiple MIDI files into a single file, preserving track structure.
    
    Args:
        input_files (list): List of paths to input MIDI files
        output_file (str): Path to save the combined output file
    """
    # Create a new MIDI file to store the combined tracks
    combined = mido.MidiFile()
    
    # Store the first file's ticks_per_beat to use for all files
    reference_ticks = None
    
    # Process each input file
    for file_path in input_files:
        print(f"Processing: {file_path}")
        try:
            midi_file = mido.MidiFile(file_path)
            
            # Set reference ticks_per_beat from the first file
            if reference_ticks is None:
                reference_ticks = midi_file.ticks_per_beat
                combined.ticks_per_beat = reference_ticks
            
            # Add each track from the file to the combined file
            for i, track in enumerate(midi_file.tracks):
                # Create a new track with the original file name as prefix
                file_name = os.path.basename(file_path)
                track_name = f"{file_name} - Track {i+1}"
                
                # Create a new track for the combined file
                new_track = mido.MidiTrack()
                
                # Add a track name meta message at the beginning
                new_track.append(mido.MetaMessage('track_name', name=track_name, time=0))
                
                # Add all messages from the original track
                for msg in track:
                    new_track.append(msg)
                
                # Add the new track to the combined file
                combined.tracks.append(new_track)
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Save the combined file
    combined.save(output_file)
    print(f"Combined MIDI file saved to: {output_file}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Combine multiple MIDI files into one file.')
    # parser.add_argument('input_files', nargs='+', help='Input Midi to combine')
    parser.add_argument('-o', '--output', default='combined.mid', help='Output MIDI file path')
    
    args = parser.parse_args()
    
    # Validate input files
    input_file_directory = "C:/Users/dongg/Documents/UROPSP25/Pokemon Musescores/UncombinedMidis/Twinleaf_Town"
    valid_files = []
    for root, _, files, in os.walk(input_file_directory):
        for file in files:
            file_path = os.path.join(input_file_directory,file)
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
            else:
                valid_files.append(file_path)
    
    if not valid_files:
        print("No valid input files provided. Exiting.")
        return
    
    # Combine the files
    combine_midi_files(valid_files, args.output)

if __name__ == "__main__":
    main()