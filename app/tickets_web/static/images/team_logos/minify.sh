# recommendation from stackoverflow:
# http://stackoverflow.com/questions/7261855/recommendation-for-compressing-jpg-files-with-imagemagick
# convert -strip -interlace Plane -gaussian-blur 0.05 -quality 85% source.jpg result.jpg

for img in `cat root_names.txt` ; do
    echo ${img}.png
    #convert -strip -interlace Plane -gaussian-blur 0.05 -quality 85% orig/${img}.png ${img}.png ;
    convert -strip -interlace Plane -gaussian-blur 0.05 -quality 85% -resize 100x100 orig/${img}.png ${img}.jpg ;
    #convert -strip -interlace Plane -gaussian-blur 0.05 -quality 85% -resize 15x15 orig/${img}.png ${img}_15.png ;
done

