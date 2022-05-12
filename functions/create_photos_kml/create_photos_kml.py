import os
import re
import time

from GPSPhoto import gpsphoto
import simplekml
import sentry_sdk
sentry_sdk.init(
    "https://0c979e12cc50474eae418fa5c038d246@o775062.ingest.sentry.io/6397917",
    traces_sample_rate=0.1
)

missions_regex = r'^\d{4}-\d{1,}-\d{1,} \d{1,}$'


def main():    

    letters = ['D', 'E', 'F', 'G']
    for letter in letters:
        try:
            missions_path = f'{letter}:\\Missions'
            missions = os.listdir(missions_path)
            break
        except:
            pass
    else:
        print('No external hard drives found.')
        return
    
    try:
        missions = os.listdir(missions_path)
    except FileNotFoundError:
        print("Make sure HD is plugged in.")
        return

    missions = [m for m in missions if re.search(missions_regex, m) is not None]

    kml = simplekml.Kml()

    for mission in missions:
        
        photos_path = f'{missions_path}/{mission}'
        photos = os.listdir(photos_path)
        photos = [p for p in photos if p.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if len(photos) == 0:
            continue
            
        mission_folder = kml.newfolder(name=mission)

        for photo in photos:

            photo_path = f'{photos_path}/{photo}'

            data = gpsphoto.getGPSData(photo_path)

            latitude = data['Latitude']
            longitude = data['Longitude']
            altitude = data['Altitude']

            marker = mission_folder.newpoint()
            marker.coords = [(longitude, latitude)]
            marker.style.iconstyle.icon.href = 'https://static.virunga.link/icons/drone_photo.png'
            marker.description = f'<![CDATA[<img style="max-width:500px;" src="file:///{photo_path}">]]>'
            marker.visibility = 0

        mission_folder.open = 0

    #local_kmz_href = os.path.join('/', 'tmp', 'spot.kmz')

    drone_photos_path = os.path.join(os.path.dirname(__file__), "drone_photos.kml")

    kml.save(drone_photos_path)

    with open(drone_photos_path, "r") as f:
        kml_file = f.read()
        kml_file = kml_file.replace("&lt;", "<")
        kml_file = kml_file.replace("&quot;", "\"")
        kml_file = kml_file.replace("&gt;", ">")

    with open(drone_photos_path, "w+") as f:
        f.write(kml_file)

    print('success')


if __name__ == "__main__":

    start_time = time.time()
    main()
    print("--- %0.2f seconds ---" % (time.time() - start_time))

