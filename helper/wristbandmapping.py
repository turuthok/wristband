import json
from os import path

class WristbandMapping:
    wristband_map = {}

    def __init__(self, map_file):
        self.map_file = map_file
        self.load()

    def load(self):
        if path.exists(self.map_file):
            with open(self.map_file, "r") as f:
                self.wristband_map = json.load(f)

    def save(self):
        with open(self.map_file, "w") as f:
            json.dump(self.wristband_map, f)

    def get(self, rfid):
        if rfid in self.wristband_map:
            print('Map wristband RFID {} => {}'.format(rfid, self.wristband_map[rfid]))
            rfid = self.wristband_map[rfid]
        return rfid

    def create(self, wristband_rfid, rfid):
        self.wristband_map[wristband_rfid] = rfid
        self.save()
