from PIL import Image

# Display resolution
EPD_WIDTH = 400
EPD_HEIGHT = 300


class EPD():
    def __init__(self):
        self.width = 400
        self.height = 300

    def init(self):
        pass

    def getbuffer(self, image):
        return image

    def display(self, image: Image):
        image.show(command='feh')
