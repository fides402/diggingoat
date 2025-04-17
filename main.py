#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube Samples Downloader

Questo script cerca playlist su YouTube con la parola chiave "samples",
filtra le playlist, seleziona 3 playlist casuali e scarica 3 audio casuali
da ciascuna playlist.
"""

import os
import sys
import argparse
from youtube_search import (
    cerca_playlist_youtube,
    filtra_playlist,
    seleziona_playlist_random,
    scarica_audio_random
)

def main():
    """
    Funzione principale che esegue il flusso completo del programma.
    """
    parser = argparse.ArgumentParser(description='Scarica audio casuali da playlist di YouTube con la parola chiave "samples".')
    parser.add_argument('--keyword', type=str, default='samples', help='Parola chiave da cercare (default: "samples")')
    parser.add_argument('--num-playlists', type=int, default=3, help='Numero di playlist casuali da selezionare (default: 3)')
    parser.add_argument('--num-audio', type=int, default=3, help='Numero di audio da scaricare per playlist (default: 3)')
    parser.add_argument('--min-videos', type=int, default=5, help='Numero minimo di video che una playlist deve contenere (default: 5)')
    parser.add_argument('--output-dir', type=str, default=None, help='Directory di output per i file scaricati (default: ./downloads)')
    
    args = parser.parse_args()
    
    # Crea la directory di output principale se non specificata
    if args.output_dir is None:
        args.output_dir = os.path.join(os.getcwd(), "downloads")
    
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Directory di output principale: {args.output_dir}")
    
    # Passo 1: Cerca playlist su YouTube
    print(f"\n=== RICERCA PLAYLIST ===")
    playlists = cerca_playlist_youtube(args.keyword)
    
    if not playlists:
        print(f"Nessuna playlist trovata con la parola chiave '{args.keyword}'. Uscita.")
        return 1
    
    print(f"Trovate {len(playlists)} playlist.")
    
    # Passo 2: Filtra le playlist
    print(f"\n=== FILTRAGGIO PLAYLIST ===")
    filtered_playlists = filtra_playlist(playlists, args.min_videos)
    
    if not filtered_playlists:
        print(f"Nessuna playlist ha superato il filtraggio. Uscita.")
        return 1
    
    print(f"Playlist filtrate: {len(filtered_playlists)}/{len(playlists)}")
    
    # Passo 3: Seleziona playlist casuali
    print(f"\n=== SELEZIONE PLAYLIST CASUALI ===")
    selected_playlists = seleziona_playlist_random(filtered_playlists, args.num_playlists)
    
    if not selected_playlists:
        print(f"Nessuna playlist selezionata. Uscita.")
        return 1
    
    # Passo 4: Scarica audio casuali da ciascuna playlist
    print(f"\n=== DOWNLOAD AUDIO ===")
    all_downloaded_files = []
    
    for i, playlist in enumerate(selected_playlists, 1):
        print(f"\nPlaylist {i}/{len(selected_playlists)}: {playlist['title']}")
        
        # Crea una sottodirectory per questa playlist
        playlist_dir = os.path.join(args.output_dir, f"playlist_{i}_{playlist['id']}")
        
        # Scarica gli audio
        downloaded_files = scarica_audio_random(playlist, args.num_audio, playlist_dir)
        all_downloaded_files.extend(downloaded_files)
    
    # Riepilogo finale
    print(f"\n=== RIEPILOGO ===")
    print(f"Playlist trovate: {len(playlists)}")
    print(f"Playlist filtrate: {len(filtered_playlists)}")
    print(f"Playlist selezionate: {len(selected_playlists)}")
    print(f"Audio scaricati: {len(all_downloaded_files)}/{args.num_playlists * args.num_audio}")
    
    if all_downloaded_files:
        print("\nFile audio scaricati:")
        for i, file_path in enumerate(all_downloaded_files, 1):
            print(f"{i}. {file_path}")
        
        print(f"\nTutti i file sono stati salvati nella directory: {args.output_dir}")
        return 0
    else:
        print("Nessun file audio è stato scaricato. Verifica la connessione o prova con un'altra parola chiave.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
