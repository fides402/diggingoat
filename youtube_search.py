#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import time
import json
from typing import List, Dict, Any
import yt_dlp
import requests

def cerca_playlist_youtube(keyword: str) -> List[Dict[str, str]]:
    """
    Cerca playlist su YouTube con la parola chiave specificata utilizzando yt-dlp.
    
    Args:
        keyword (str): La parola chiave da cercare
        
    Returns:
        List[Dict[str, str]]: Lista di playlist trovate con titolo e URL
    """
    print(f"Ricerca di playlist su YouTube con la parola chiave: '{keyword}'")
    
    # Configurazione di yt-dlp per la ricerca
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    # URL di ricerca per le playlist
    search_url = f"ytsearch50:{keyword} playlist"
    
    playlist_data = []
    
    try:
        # Esegui la ricerca con yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            
            if 'entries' in info:
                for entry in info['entries']:
                    # Verifica se l'elemento è una playlist o contiene un link a una playlist
                    if entry and 'url' in entry:
                        url = entry['url']
                        # Se è un video, controlla se ha una playlist associata
                        if 'watch?v=' in url and 'list=' in url:
                            playlist_id = url.split('list=')[1].split('&')[0]
                            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                            title = entry.get('title', f"Playlist {playlist_id}")
                            
                            # Evita duplicati
                            if not any(p['id'] == playlist_id for p in playlist_data):
                                playlist_data.append({
                                    'title': title,
                                    'url': playlist_url,
                                    'id': playlist_id
                                })
        
        # Se non abbiamo trovato abbastanza playlist, proviamo un approccio alternativo
        if len(playlist_data) < 10:
            print("Utilizzando metodo alternativo per trovare più playlist...")
            # Cerca direttamente playlist con yt-dlp
            search_url = f"ytsearchplaylist20:{keyword}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_url, download=False)
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry and 'id' in entry and 'title' in entry:
                            playlist_id = entry['id']
                            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                            title = entry['title']
                            
                            # Evita duplicati
                            if not any(p['id'] == playlist_id for p in playlist_data):
                                playlist_data.append({
                                    'title': title,
                                    'url': playlist_url,
                                    'id': playlist_id
                                })
        
        print(f"Trovate {len(playlist_data)} playlist")
        return playlist_data
    
    except Exception as e:
        print(f"Errore durante la ricerca delle playlist: {e}")
        # Approccio di fallback usando l'API di ricerca di YouTube
        try:
            print("Tentativo di ricerca tramite API di YouTube...")
            # Questo è un approccio semplificato che non richiede API key
            search_term = f"{keyword} playlist"
            search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}&sp=EgIQAw%3D%3D"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(search_url, headers=headers)
            
            # Estrai gli ID delle playlist dalla risposta
            import re
            playlist_ids = re.findall(r"list=([a-zA-Z0-9_-]+)", response.text)
            
            # Rimuovi duplicati
            playlist_ids = list(set(playlist_ids))
            
            for playlist_id in playlist_ids[:20]:  # Limita a 20 playlist
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                playlist_data.append({
                    'title': f"Playlist {playlist_id}",
                    'url': playlist_url,
                    'id': playlist_id
                })
            
            print(f"Trovate {len(playlist_data)} playlist con il metodo alternativo")
            return playlist_data
        except Exception as e2:
            print(f"Anche il metodo alternativo ha fallito: {e2}")
            return []

def filtra_playlist(playlists: List[Dict[str, str]], min_videos: int = 5) -> List[Dict[str, str]]:
    """
    Filtra le playlist in base a criteri specifici.
    
    Args:
        playlists (List[Dict[str, str]]): Lista di playlist da filtrare
        min_videos (int): Numero minimo di video che la playlist deve contenere
        
    Returns:
        List[Dict[str, str]]: Lista di playlist filtrate
    """
    print(f"Filtraggio delle playlist (minimo {min_videos} video)...")
    
    filtered_playlists = []
    
    for playlist in playlists:
        try:
            # Ottieni informazioni sulla playlist
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist['url'], download=False)
                
                # Verifica il numero di video nella playlist
                if 'entries' in info and len(info['entries']) >= min_videos:
                    # Aggiungi il conteggio dei video alla playlist
                    playlist['video_count'] = len(info['entries'])
                    # Aggiungi gli ID dei video alla playlist
                    playlist['video_ids'] = [entry['id'] for entry in info['entries'] if 'id' in entry]
                    filtered_playlists.append(playlist)
                    print(f"Playlist qualificata: {playlist['title']} ({playlist['video_count']} video)")
        except Exception as e:
            print(f"Errore durante il filtraggio della playlist {playlist['url']}: {e}")
    
    print(f"Playlist filtrate: {len(filtered_playlists)}/{len(playlists)}")
    return filtered_playlists

def seleziona_playlist_random(playlists: List[Dict[str, str]], num_playlists: int = 3) -> List[Dict[str, str]]:
    """
    Seleziona un numero specificato di playlist casuali dalla lista.
    
    Args:
        playlists (List[Dict[str, str]]): Lista di playlist da cui selezionare
        num_playlists (int): Numero di playlist da selezionare
        
    Returns:
        List[Dict[str, str]]: Lista di playlist selezionate casualmente
    """
    if not playlists:
        print("Nessuna playlist disponibile per la selezione casuale.")
        return []
    
    num_to_select = min(num_playlists, len(playlists))
    print(f"Selezione di {num_to_select} playlist casuali da {len(playlists)} disponibili...")
    
    selected_playlists = random.sample(playlists, num_to_select)
    
    for i, playlist in enumerate(selected_playlists, 1):
        print(f"Playlist {i} selezionata: {playlist['title']} ({playlist['video_count']} video)")
    
    return selected_playlists

def scarica_audio_random(playlist: Dict[str, str], num_audio: int = 3, output_dir: str = None) -> List[str]:
    """
    Scarica un numero specificato di audio casuali da una playlist.
    
    Args:
        playlist (Dict[str, str]): Playlist da cui scaricare gli audio
        num_audio (int): Numero di audio da scaricare
        output_dir (str): Directory di output per i file scaricati
        
    Returns:
        List[str]: Lista dei percorsi dei file audio scaricati
    """
    if 'video_ids' not in playlist or not playlist['video_ids']:
        print(f"Nessun video disponibile nella playlist {playlist['title']}")
        return []
    
    # Crea la directory di output se non esiste
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "downloads", f"playlist_{playlist['id']}")
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"Directory di output: {output_dir}")
    
    # Seleziona video casuali dalla playlist
    num_to_select = min(num_audio, len(playlist['video_ids']))
    selected_video_ids = random.sample(playlist['video_ids'], num_to_select)
    
    downloaded_files = []
    
    for i, video_id in enumerate(selected_video_ids, 1):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        output_template = os.path.join(output_dir, f"audio_{i}_{video_id}")
        
        print(f"Scaricamento audio {i}/{num_to_select} dalla playlist {playlist['title']}: {video_url}")
        
        # Configurazione di yt-dlp per il download
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template + '.%(ext)s',
            'quiet': False,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                downloaded_file = output_template + '.mp3'
                
                # Verifica che il file esista
                if os.path.exists(downloaded_file):
                    downloaded_files.append(downloaded_file)
                    print(f"Audio scaricato con successo: {downloaded_file}")
                else:
                    print(f"Errore: il file {downloaded_file} non è stato creato")
        except Exception as e:
            print(f"Errore durante il download dell'audio {video_url}: {e}")
    
    print(f"Download completato: {len(downloaded_files)}/{num_to_select} audio scaricati dalla playlist {playlist['title']}")
    return downloaded_files

# Test delle funzioni
if __name__ == "__main__":
    playlists = cerca_playlist_youtube("samples")
    
    if playlists:
        print("\nPrime 5 playlist trovate:")
        for i, playlist in enumerate(playlists[:5], 1):
            print(f"{i}. {playlist['title']} - {playlist['url']}")
        
        # Test della funzione di filtraggio
        filtered_playlists = filtra_playlist(playlists)
        
        if filtered_playlists:
            print("\nPrime 5 playlist filtrate:")
            for i, playlist in enumerate(filtered_playlists[:5], 1):
                print(f"{i}. {playlist['title']} ({playlist['video_count']} video) - {playlist['url']}")
            
            # Test della funzione di selezione casuale
            selected_playlists = seleziona_playlist_random(filtered_playlists, 3)
            
            if selected_playlists:
                # Test della funzione di download
                for playlist in selected_playlists[:1]:  # Test solo con la prima playlist
                    scarica_audio_random(playlist, 1)  # Scarica solo 1 audio per il test
        else:
            print("Nessuna playlist ha superato il filtraggio.")
    else:
        print("Nessuna playlist trovata. Prova con un'altra parola chiave o approccio.")
