#!/usr/bin/python
# Author: johmathe@nonutc.fr (Johan Mathe)
# License: LGPL

import amazon
import mpd
import os
import pygame
import sys
import time
import urllib

XSET_PATH = 'xset'
MPD_HOST = 'localhost'
MPD_PORT = 6600
DIRECTORY = '/home/johmathe/.cover_cache'
BLACK = 0, 0, 0
SCREEN_STATE = True

def ConnectMpd():
  client = mpd.MPDClient()
  client.connect(MPD_HOST, MPD_PORT)
  return client

def InitDisplay():
  pygame.init()
  size = width, height = 800, 480
  screen = pygame.display.set_mode(size)
  pygame.display.toggle_fullscreen()
  pygame.mouse.set_visible(False)
  return screen

def CacheFilePath(artist, album):
  file_name = '%s_%s' % (artist.replace(' ', '_'), album.replace(' ', '_'))
  file_path = os.path.join(DIRECTORY, file_name)
  return file_path

def CacheLookup(artist, album):
  file_path = CacheFilePath(artist, album)
  if os.path.isfile(file_path):
    return True
  return False

def PopulateCache(artist, album):
  dest = CacheFilePath(artist, album)
  url = amazon.GetUrl(artist, album)
  image = urllib.URLopener()
  image.retrieve(url, dest)

def GetCover(artist, album):
  if not CacheLookup(artist, album):
    PopulateCache(artist, album)
  return CacheFilePath(artist, album)

def UpdateDisplayCover(screen, current_song):
    dest = GetCover(current_song['artist'], current_song['album'])
    cover = pygame.image.load(dest)
    cover_rect = cover.get_rect()
    screen.fill(BLACK)
    screen.blit(cover, (140,0))
    pygame.display.flip()

def TurnScreen(status):
  global SCREEN_STATE
  if SCREEN_STATE is not status:
    if status:
      os.system('%s dpms force on' % XSET_PATH)
    else:
      os.system('%s dpms force suspend' % XSET_PATH)
    SCREEN_STATE = status

def main():
  screen = InitDisplay()
  client = ConnectMpd()
  while True:
    time.sleep(0.5)
    status = client.status()
    current_song = client.currentsong()
    screen_state = False
    if ('artist' in current_song and 'album' in current_song and
        status['state'] == 'play'):
      try:
        screen_state = True
        UpdateDisplayCover(screen, current_song)
      except amazon.NoCoverAvailable:
        print 'no cover available for artist %(artist)s album %(album)s' % current_song
        screen_state = False
    TurnScreen(screen_state)

if __name__ == '__main__':
  main()
