

# recommendation from stackoverflow:
# http://stackoverflow.com/questions/7261855/recommendation-for-compressing-jpg-files-with-imagemagick
# convert -strip -interlace Plane -gaussian-blur 0.05 -quality 85% source.jpg result.jpg

for img in delete_tickets edit_tickets game_tickets logged_in login my_ticket_lot my_tickets new_tickets sell_tickets step2 ticket_lot tickets_step1 ; do
    echo convert -strip -interlace Plane -gaussian-blur 0.05 -quality 85% ${img}.png ${img}.jpg ; 
    convert -strip -interlace Plane -gaussian-blur 0.05 -quality 85% ${img}.png ${img}.jpg ; 
done
