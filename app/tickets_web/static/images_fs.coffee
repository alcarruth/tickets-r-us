
messages = {}
messages[FileError.QUOTA_EXCEEDED_ERR] = 'QUOTA_EXCEEDED_ERR'
messages[FileError.NOT_FOUND_ERR] = 'NOT_FOUND_ERR'
messages[FileError.SECURITY_ERR] = 'SECURITY_ERR'
messages[FileError.INVALID_MODIFICATION_ERR] = 'INVALID_MODIFICATION_ERR'
messages[FileError.INVALID_STATE_ERR] = 'INVALID_STATE_ERR'

class TicketsFS

  constructor: ->
    webkitRequestFileSystem(TEMPORARY, 20*1024*1024, init_fs, error_fs)    

  error_fs: (err) =>
    console.log('There was an error !-)')
    msg = messages[err.code]
    msg = msg? && msg || 'UNKNOWN_ERR'
    console.log("Error: #{msg}")

  init_fs: (fs) =>
    @fs = fs

  mkdir: (path) =>
  


  writeText: (path, text) =>
    # Create a new Blob and write it to log.txt.
    blob = new Blob([text], {type: 'text/plain'})
    @writeBlob(path, blob)

  writeBlob: (path, blob) =>
    @fs.root.getFile(path, {create: true}, (fileEntry) =>
      # Create a FileWriter object for our FileEntry
      fileEntry.createWriter((fileWriter) =>
        fileWriter.onwriteend = (e) => console.log("#{path}")
        fileWriter.onerror = (e) => console.log('#{path} failed: #{e.toString()}')
        fileWriter.write(blob, errorHandler)),
      errorHandler)



    @fs.root.getFile(...)


  readFile: (path) =>
    @fs.root.getFile(...)
    



