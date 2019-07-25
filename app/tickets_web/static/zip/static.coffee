#!/usr/bin/env coffee 

fs = require('fs')
JSZip = require('jszip')

images_dir = "/var/www/git/udacity/tickets/app/tickets_web/static/images_64/"

images = {}

dirs = [ 'conference_logos_64', 'team_logos_64', 'tickets_64' ]


for dir in dirs
  images[dir] = {}
  for img_file in fs.readdirSync("#{images_dir}/#{dir}")
    images[dir][img_file] = fs.readFileSync("#{images_dir}/#{dir}/#{img_file}", 'utf-8')

images['FF8a5Ku_2000_cropped.jpg-64'] = fs.readFileSync("#{images_dir}/FF8a5Ku_2000_cropped.jpg-64", 'utf-8')
    

#zip = new JSZip()
#content = fs.readFileSync("./images.zip")
#zip_fs = {}
#zip.loadAsync(content).then((x)-> zip_fs.root = x)
#exports.zip_fs = zip_fs

exports.images = images
