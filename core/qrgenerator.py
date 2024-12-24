
# Importing library
import json
import qrcode

from core.models import Registered_Participant


def generate_qr():

    data_list = Registered_Participant.objects.all().order_by('id').values_list('unique_code')

    # Iterating over the data list
    for i, data in enumerate(data_list, start=1):
        print(data)
        # Encoding data using make() function
        img = qrcode.make(json.dumps({"unqc":data[0]}))
    
        # Saving each QR code as an image file
        img.save(f'Participant_QR/{i}.png')
        print(f'QR Code {i} saved as {i}.png')

    print("All QR codes have been generated successfully!")