
class Team

  constructor: () ->

class Conference

  conference: () ->

class ImageElements

  constructor: (images) ->
    @div = document.createElement('div')
    @div.setAttribute('id', 'images')


  add_conference_logos: =>
    for k,v of images.conference_logos_64
      id = "conference-logo-#{k}"
      src = "data:image/png;base64, #{v}"
      alt = "logo for #{k}"
      @html += "<img id=\"#{id}\" src=\"#{src}\" alt=\"#{alt}\"> \n"

  add_team_logos: =>
    for k,v of images.team_logos_64
      id = "team-logo-#{k}"
      src = "data:image/png;base64, #{v}"
      alt = "logo for #{k}"
      @html += "<img id=\"#{id}\" src=\"#{src}\" alt=\"#{alt}\"> \n"

    @div.innerHTML = @html
    document.body.appendChild(@div)

window.ImageElements = ImageElements
    
