#!/usr/bin/env coffee 

JSZip = require('jszip')


create_images_json = ->

  fs = require('fs')
  images_dir = "/var/www/git/udacity/tickets/app/tickets_web/static/images_64/"
  images = {}
  dirs = [ 'conference_logos_64', 'team_logos_64', 'tickets_64' ]

  for dir in dirs
    images[dir] = {}
    for img_file in fs.readdirSync("#{images_dir}/#{dir}")
      file_path = "#{images_dir}/#{dir}/#{img_file}"
      images[dir][img_file] = fs.readFileSync(file_path, 'utf-8')

  file = 'FF8a5Ku_2000_cropped.jpg-64'
  images[file] = fs.readFileSync("#{images_dir}/#{file}", 'utf-8')

  images_json = JSON.stringify(images)
  fs.writeFileSync('images_json', images_json)


exports.create_images_json = create_images_json
