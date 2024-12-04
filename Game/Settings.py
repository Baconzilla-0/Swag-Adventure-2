import json

class Settings:
    def ReadFile(Path):
        with open(Path, "r") as File:
            Data = File.read()

        return json.loads(Data)
    def WriteFile(Path, Data):
        JsonData = json.dumps(Data)

        with open(Path, "w") as File:
            Data = File.write(JsonData)
