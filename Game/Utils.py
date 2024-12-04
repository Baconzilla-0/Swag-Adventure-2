import json

class Utils:
    def WriteData(File, Dict):
        Data = json.dumps(Dict)

        with open(File, "w") as JsonFile:
            JsonFile.write(Data)
    
    def ReadData(File):
        with open(File, "w") as JsonFile:
            Raw = JsonFile.read()
            Data = json.load(Raw)

        return Data