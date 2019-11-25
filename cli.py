from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.styles import Style


class MyCustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        commands = self.getCommands()
        for c in commands.keys():
            if document.text in c:
                yield Completion(c, -(len(document.text)), display_meta=commands[c]['meta'])

class Console():    
    def __init__(self, getCommands, inGameInfo, isDrawingInfo, ctrlD):
        self.session = PromptSession(history=FileHistory('.hartic_history'))
        self.prompt = self.session.prompt
        self.getCommands = getCommands
        self.inGameInfo = inGameInfo
        self.isDrawingInfo = isDrawingInfo
        # self.ctrlD = ctrlD # binding ctrl + d e alt + f4 para chamar ctrlD
    
    def getStyle(self):
        style = Style.from_dict({
            # User input (default text).
            '':          'ansicyan',
            'word': '#ffffff',
            # Prompt.
            'username': '',
            'at':       '#ff0066',
            'bracket':    '#884444',
            'pound':    '#ff0066',
            'host':     '#60b48a',
        })
        return style

    def getPS1(self):
        PS1 = [
            ('class:host',     'hartic'),
            ('class:pound',    '~ '),
        ]

        inGame, room_id, nick = self.inGameInfo()
        if inGame:
            #remove the host
            PS1.reverse()
            PS1.pop()
            PS1.reverse()
            #add news
            drawing, word = self.isDrawingInfo()
            if drawing:
                PS1 = [
                    ('class:pound', ':'),
                    ('class:bracket', '['),
                    ('class:word', word),
                    ('class:bracket', ']'),
                ] + PS1
            PS1 = [
                ('class:username', nick),
                ('class:at',       '@'),
                ('class:host',     room_id),
            ] + PS1

        return PS1

    def print(self, _input):
        def _print():
            print(_input)
        run_in_terminal(_print)

    def readinput(self, ):
        completer = MyCustomCompleter()
        completer.getCommands = self.getCommands
        ps1 = self.getPS1()
        inp = self.prompt(self.getPS1, style=self.getStyle(), refresh_interval=1, completer=completer)
        return inp
