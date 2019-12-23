import requests, re, time, urllib.parse
from log import log, error

class Network():
    def __init__(self):
        self.url = 'https://gartic.com.br'
        ua = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
        }
        self.sess = requests.session()
        self.sess.headers.update(ua)
        # pegando tokens
        self.sess.request('GET', self.url)
        self.lastid = False
        self.naction = 0
        self.tipid = 0

    def enterRoom(self, room_id, nick='hartic'):    
        # entrando na sala
        self.nick = nick
        self.naction = 0
        self.tipid = 0
        r = self.sess.request('POST', self.url + '/autenticar.php', data={
            'login': nick,
            'sala': room_id,
            'idioma': 1,
            'acesso': 1
        })
        if not room_id in r.url:
            error(r)
            raise Exception('Verify the room_id')
    
    def quitRoom(self):
        self.sess.request('GET', self.url + '/room/saida.php?cache=' + str(int(time.time())) + '000&tipo=0&ajax=1')
        self.lastid = False
        self.naction = 0

    def initialInfo(self):
        r = self.sess.request('GET', self.url + '/request/mobile/check.php?cache=' + str(int(time.time())) + '000')
        lastid = re.search('lastId":([0-9]+)', r.text)
        if lastid:
            self.lastid = lastid.group(1)
        

    def verifyStatus(self, resp):
        '''
            show if the response has some important info about the game
        '''
        lastid = re.search('^([0-9]+)@', resp.text)
        if lastid:
            self.lastid = lastid.group(1)
        log(resp)
        ret = {}
        ret['messages'] = []
        msgs = re.findall('7#~[^#]+#[^~#]+#', resp.text)
        for m in msgs:
            nick = re.search('7#~([^#]+)#', m).group(1)
            msg = re.search('7#~[^#]+#([^#]+)#', m).group(1)
            ret['messages'].append((nick, msg))

        # verify the turn and get the word to draw
        ret['endturn'] = False
        if re.search('[@*]~' + self.nick + '[.][0-9]+[.]0[.][0-9]+[.]1[.]', resp.text):
            ret['endturn'] = True

        ret['word'] = False
        if re.search('[@*]~' + self.nick + '[.][0-9]+[.]1[.][0-9]+[.]1[.]', resp.text):
            fword = re.search('\|10#[0-9]+#([^#]+)#', resp.text)
            if fword:
                ret['word'] = fword.group(1)
                self.tipid = 0 #when starts drawing reset tipid
        return ret

    def getNews(self):
        urlopt = ''
        if self.lastid:
            urlopt = '&lastid=' + self.lastid
        resp = self.sess.request('GET', self.url + '/room/news.php?cache=' + str(int(time.time())) + '000' + urlopt)
        return self.verifyStatus(resp)
    
    def getComando(self, code, data, encode=False):
        comando = ''
        for d in data:
            # if encode:
                # data encode to ã
            self.naction += 1
            comando += code + '@' + d + '@' + str(self.naction) + '|'
        return comando[:-1]

    def sendAction(self, code, data, encode=False, comando = False):
        if not comando:
            data = self.getComando(code, data, encode)
        r = self.sess.request('POST', self.url + '/room/atualizar.php', 
            data = {
                'comando': data
            }
        )
        return self.verifyStatus(r)
        

    def sendMessage(self, msg):
        r = self.sendAction('7', [msg], encode=False)
        log(r)

    def sendWord(self, word):
        self.sendAction('8', [word], encode=False)

    def acceptDraw(self):
        self.sendAction('32', ['1'])

    def sendTip(self):
        self.sendAction('19', [str(self.tipid)])
        self.tipid += 1
        
    def skipTurn(self):
        self.sendAction('16', [''])

    def reportDraw(self):
        self.sendAction('20', [''])

    def setColor(self, hex_color: str):
        self.sendAction('5', ['x' + hex_color.upper()])

    def drawPixels(self, coordinates, scale=2):
        data = []
        for xy in coordinates:
            data.append('2#' + str(xy[0]*scale) + '#' + str(xy[1]*scale) + '#' + str(xy[0]*scale+scale) + '#' + str(xy[1]*scale+scale))
        self.sendAction('1', data)

    def drawAllPixels(self, pixelsByColor, scale=2):
        commando = ''
        for c in pixelsByColor.keys():
            hex_color = '%02x%02x%02x' % c
            commando += self.getComando('5', ['x' + hex_color.upper()]) + '|'
            for xy in pixelsByColor[c]:
                commando += self.getComando('1', ['2#' + str(xy[0]*scale) + '#' + str(xy[1]*scale) + '#' + str(xy[0]*scale+scale) + '#' + str(xy[1]*scale+scale)]) + '|'
        r = self.sendAction('', commando, comando=True)
        return r


def sprint(string):
    print(string)
    

