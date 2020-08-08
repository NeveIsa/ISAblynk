class Terminal():
    def __init__(self,oled):
        """
        Resolution -> (xpixels,ypixels)
        """
        self.oled = oled
        self.xmax = oled.width
        self.ymax = oled.height

        #pixels for lineheight
        self.lineheight = 10


        self.maxlines = self.ymax // self.lineheight
        # current pos of cursor
        self.ypos = 0
        self.xpos = 0


    #current line number of cursor
    @property
    def yline(self):
        return self.ypos//self.lineheight

    @yline.setter
    def yline(self,lineno):
        self.ypos = lineno * self.lineheight


    def clean(self):
        self.oled.fill(0)
        self.oled.show()


    def hline(self,lineno=None,solid=True):
        if lineno==None:
            lineno = self.yline
        for x in range(self.xmax):
            #draw 2 pix-height above the start of new line
            if x%5<2:
                if solid:
                    self.oled.framebuf.pixel(x,lineno*self.lineheight-2,1)
                else:
                    self.oled.framebuf.pixel(x,lineno*self.lineheight-2,0)

            else:
                self.oled.framebuf.pixel(x,lineno*self.lineheight-2,1)

        self.oled.show()


    def clearln(self,lineno=None):
        if lineno==None:
            lineno = self.yline
        for x in range(self.xmax):
            for y in range(self.lineheight*lineno, self.lineheight*(lineno+1)):
                #calling directly on framebuff instead of pixel for speedup
                # https://github.com/adafruit/micropython-adafruit-ssd1306/blob/master/ssd1306.py
                self.oled.framebuf.pixel(x,y,0)
        self.oled.show()

    def println(self,data="",lineno=None):
        if lineno==None:
            lineno = self.yline

        #print(lineno)
        self.clearln(lineno)
        self.oled.text(data,0,lineno*self.lineheight)
        self.oled.show()
        self.yline = (lineno + 1) % self.maxlines
