"

images = JSON.parse(images_json)

if window?
  window.images = images
else
  exports.images = images
