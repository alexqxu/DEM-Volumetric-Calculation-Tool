class DataHandler:
    def __init__(self, demList, shapeFile):
        self.demFiles = []
        self.setDEM(demList)
        self.shapeFile = ""
        self.setShape(shapeFile)

    def setDEM(self, demList):
        self.demFiles = list(demList)
        return

    def setShape(self, shapeFile):
        self.shapeFile = shapeFile
        return

    def getDEMs(self):
        return self.demFiles

    def getShape(self):
        return self.shapeFile
