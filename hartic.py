import cli, re, os, time, html
from network import *
from threading import Thread
from image import preprocessingImage, getPixelByColors

class Hartic():
    def __init__(self):
        self.console = cli.Console(self.getCommands, self.inGameInfo, self.isDrawingInfo, self.ctrlD)
        self.net = Network()
        self.threads = []
        self.setInGame(False)
        self.setDrawing(False)
        self.closed = False
        self.room_id = False
        self.nick = False
        self.word = False

    def getNews(self):
        while self.inGame():
            time.sleep(2)
            news = self.net.getNews()
            for m in news['messages']:
                self.console.print('~' + html.unescape(m[0]) + ': ' + html.unescape(m[1]))
            if news['word']:
                if not self.isDrawing():
                    self.setDrawing(True, news['word'])
                    self.net.acceptDraw()
                    self.console.print('You turn! The word is ' + news['word'])
            if news['endturn']:
                self.setDrawing(False)

    def inGame(self):
        return self.entered

    def inGameInfo(self):
        return (self.inGame(), self.room_id, self.nick)

    def isDrawingInfo(self):
        return (self.isDrawing(),self.word)

    def setInGame(self, state):
        self.entered = state

    def isDrawing(self):
        return self.drawing

    def setDrawing(self, state, word=False):
        self.drawing = state
        self.word = word

    def enterRoom(self, args):
        room_id = args[0]
        fid = re.search('gartic[.]com[.]br[/]([0-9]+)', room_id)
        if fid:
            room_id = fid.group(1)
        nick = 'hartic'
        if len(args) > 1:
            nick = args[1]
        try:
            self.net.enterRoom(room_id, nick)
            self.net.initialInfo()
            self.setDrawing(False)
            self.setInGame(True)
            self.console.print('enter here ' + self.net.url+'/' + room_id)
            self.room_id = room_id
            self.nick = nick
            t = Thread(target=self.getNews)
            t.start()
            self.threads.append(t)
        except Exception:
            self.console.print('- Verify the room_id')
        
        
    def quitRoom(self, args):
        self.net.quitRoom()
        self.setInGame(False)
        self.setDrawing(False)
        self.nick = False
        self.room_id = False
    
    def ctrlD(self):
        if self.inGame():
            self.quitRoom([])
        else:
            self.close()

    def close(self, args):
        if self.inGame():
            self.quitRoom([])
        self.closed = True

    def sendMessage(self, args):
        msg = ''
        for m in args:
            msg += m + ' '
        msg = msg[:-1]
        self.net.sendMessage(msg)

    def sendWord(self, args):
        word = ''
        for w in args:
            word += w + ' '
        word = word[:-1]
        self.net.sendWord(word)

    def skipTurn(self, args):
        self.net.skipTurn()

    def sendTip(self, args):
        self.net.sendTip()

    def sendDraw(self, args):
        filepath = args[0]
        colors = 12
        width = 125
        height = 70

        if len(args) > 1:
            width = int(args[1])
        if len(args) > 2:
            height = int(args[2])
        if len(args) > 3:
            colors = int(args[3])

        scale = max(1, int(500/(width*0.94)))

        img = preprocessingImage(filepath, width, height, colors)
        pixels = getPixelByColors(img)
        self.net.drawAllPixels(pixels, scale=scale)
        # for color in pixels.keys():
        #     if not self.isDrawing(): #stop send pixels if time finished
        #         return 
        #     hex_color = '%02x%02x%02x' % color
        #     self.net.setColor(hex_color)
        #     self.net.drawPixels(pixels[color])
                    


    def getCommands(self):
        both = {
            '/close': {
                'meta': 'Close the program',
                'func': self.close
            }
        }
        before = {
            '/enter': {
                'meta': 'Enter in a room. e.g. /enter 01315840 hartic',
                'func': self.enterRoom,
                'args': lambda n:len(n) > 0 and (re.match('[0-9]{8}', n[0]) or re.search('gartic[.]com[.]br[/][0-9]{8}', n[0]))
            },
            '/draw': {
                'meta': 'e.g. /draw /tmp/a.jpg [125 70 16]',
                'func': self.sendDraw,
                'args': lambda n:len(n) > 0 and os.path.isfile(n[0])
            },
        }
        after = {
            '/msg': {
                'meta': 'Send a message',
                'func': self.sendMessage,
                'args': lambda msg:len(msg) > 0
            },

            '/word' : {
                'meta': 'Try to hit the drawing',
                'func': self.sendWord,
                'args': lambda w:len(w) > 0
            },
            '/quit': {
                'meta': 'Quit from the current room',
                'func': self.quitRoom
            },
        }
        drawing = {
            '/draw': {
                'meta': 'e.g. /draw /tmp/a.jpg',
                'func': self.sendDraw,
                'args': lambda n:len(n) > 0 and os.path.isfile(n[0])
            },
            '/tip': {
                'meta': 'Give a tip about the draw',
                'func': self.sendTip
            },
            '/skip': {
                'meta': 'Skip your turn',
                'func': self.skipTurn
            },
        }
        if self.inGame():
            both.update(after)
            if self.isDrawing():
                both.update(drawing)
        else:
            both.update(before)
        return both

    def getInput(self):
        line = self.console.readinput().split(' ')
        command = line[0]
        args = line[1:]
        args = list(filter(lambda x:len(x)>0, args)) #remove empty fields
        return (command, args)
    

if __name__ == '__main__':
    har = Hartic()
    while not har.closed:
        inp, args = har.getInput()
        if inp in har.getCommands():
            com = har.getCommands()[inp]
            if not 'args' in com or com['args'](args):
                com['func'](args)
            else:
                har.console.print('- Verify the required arguments')

    
    