#!/usr/bin/env python3


import os
from core.api.blueprint import app


watch_directories = [ 'local', 'default' ]
watch_files = []
for watch_directory in watch_directories:
  for dirname, dirs, files in os.walk(watch_directory):
    for filename in files:
      filename = os.path.join(dirname, filename)
      print(f'test: {filename}')
      if not filename.endswith('.swp'):
        print(f'file does not end with swp')
        if os.path.isfile(filename):
          watch_files.append(filename)


if __name__ == '__main__':

  print(f'watch files: {watch_files}')
  app.run(debug=True, extra_files=watch_files)
