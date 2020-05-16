#!/usr/bin/env coffee

fs = require('fs')

showdown = require('showdown')
converter = new showdown.Converter()

render = (md_src) ->
  return """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title> Readme </title>
    <link rel="stylesheet" href="css/prism_custom.css">
    <script src="js/prism.js"></script>
    <link rel="stylesheet" href="css/main.css">
  </head>
  <body>
    #{converter.makeHtml(md_src)}
  </body>
</html>
"""

for md_file in fs.readdirSync("./md")
  src = fs.readFileSync("./md/#{md_file}", 'utf-8')
  html_file = md_file.replace('.md', '.html')
  fs.writeFileSync(html_file, render(src))
