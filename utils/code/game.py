from utils import *
from menus import *
from scripts import *
from starSystem import *
from gui import *
from planet import *
from spaceship import *
from strafebat import *
from dialogs import *
from camera import *
from universe import *
from vec2d import Vec2d
import plot
import datetime
import sys

# command parsing (a command line interface for the game)
# that supports multiple commands, and functions.
from commandParse import CommandParse

# import librarie for showing mem usage in caption
try:
    import resource
    import gc
except Exception as e:
    print(e)

FPS = 3e6


class Game(object):
    """Game(resolution = None, fullscreen = False)
    -> new game instance. Multiple game instances
    are probably a bad idea."""
    menu = None

    def __init__(self, screen):
        self.console = False
        self.debug = False
        self.player = None
        self.starttime = 1899463445
        self.fps = FPS
        self.fpscounter = 0
        self.fpses = range(0, 30)
        self.averagefps = 0
        self.screen = screen
        self.top_left = 0, 0
        self.universe = Universe(self)
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.mouseControl = True
        self.timer = 0
        self.triggers = []
        self.camera = Camera(self.universe)
        self.universe.addCamera(self.camera)

        # messenger, with controls as first message:
        self.messenger = Messenger(self.universe)
        theone = SolarA1(self.universe, "theone", Vec2d(1, 100))
        thesecond = SolarA1(self.universe, "thesecond", Vec2d(1, -100), 2, 1)
        thethird = SolarA1(self.universe, "thethird", Vec2d(1, 200), 2, 1)
        theone.addNeighbor(thesecond)
        theone.addNeighbor(thethird)

        self.universe.addStarSystem(theone)
        self.universe.addStarSystem(thesecond)
        self.universe.addStarSystem(thethird)

        self.camera.layerAdd(self.messenger, 7)
        self.camera.layerAdd(MiniInfo(self.universe), 6)

        # key polling:
        self.keys = [False]*322
        # mouse is [pos, button1, button2, button3,..., button6].
        # new Apple mice think they have 6 buttons.
        self.mouse = [(0, 0), 0, 0, 0, 0, 0, 0]
        # pygame setup:
        self.clock = pygame.time.Clock()
        self.hud = HUD(self.universe)
        self.tageting = TargetingRect(self.universe)
        self.radarfield = RadarField(self.universe)
        self.camera.layerAdd(self.hud, 4)
        self.camera.layerAdd(self.radarfield, 4)
        self.camera.layerAdd(self.tageting, 4)
        self.spaceview = SpaceView(self)
        self.camera.layerAdd(self.spaceview, 3)
        # create a chatconsole for text input capabilities
        self.chatconsole = ChatConsole(self, Rect(int(self.width/8),
                                       self.height-40, self.width -
                                       int(self.width/8), 40))
        # does the universe have a player present in it?
        self.hasPlayer = None

    def run(self):
        """Runs the game."""
        self.running = True
        while self.running:
            # game setup:
            intro = IntroMenu(self, Rect((self.width - 800) / 2,
                                         (self.height - 600) / 2,
                                         800, 600))
            self.messenger.empty()
            while self.running and intro.running:
                # event polling:
                pygame.event.pump()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    intro.handleEvent(event)
                intro.update()
                self.screen.fill((0, 0, 0, 0))
                intro.draw(self.screen)
                pygame.display.flip()
                # aim for FPS but adjust vars for self.fps.
                self.clock.tick(FPS)
                self.fps = max(1, int(self.clock.get_fps()))
                self.timer += 1. / self.fps
            # setup initial state:
            self.playerScript = InputScript(self)
            self.menuScript = Script(self)
            self.consoleScript = Script(self)
            self.player = playerShip(self, Vec2d(0, 0), Vec2d(0, 0),
                                     color=self.playerColor,
                                     name=self.PlayerName,
                                     type=self.playerType)

            self.camera.layerAdd(shipDamage(self.universe), 5)
            self.camera.layerAdd(StarField(self.universe), 2)
            self.universe.setCurrentStarSystem("theone")
            self.camera.layerAdd(self.universe.curSystem.bg, 1)
            self.camera.setLayersPlayer(self.player)
            self.universe.setPlayer(self.player)
            self.camera.setPos(self.player.pos)
            makePlayerBindings(self.playerScript, self.player)

            self.menu = Menu(self, Rect((self.width - 800) / 2,
                             (self.height - 600) / 2, 800, 600))

            makeMenuBindings(self.menuScript, self)
            makeGameBindings(self.playerScript, self)
            makeConsoleBindings(self.consoleScript, self)

            # two rules below should be integrated into their classes
            # self.menu.keys.bindings.bindings = self.playerScript.bindings
            self.menu.keys.bindings.reset()
            self.menu.addScript(self.menuScript)
            self.chatconsole.addScript(self.consoleScript)
            self.player.addScript(self.playerScript)
            for x in range(10):
                self.clock.tick()

            self.triggers = plot.newGameTriggers(self.universe)
            # create a parser that parses chatconsole input
            # for command and such.
            self.commandParse = CommandParse(self, self.chatconsole,
                                             self.messenger)
            # check once wether the universe still has a player.
            self.hasPlayer = self.universe.curSystem.ships.has(self.player)
            # The in-round loop (while player is alive):
            while self.running and self.hasPlayer:
                # check wether the universe still has a player.
                self.hasPlayer = self.universe.curSystem.ships.has(self.player)
                # event polling:
                pygame.event.pump()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    # if not self.pause and not self.console:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.mouse[event.button] = 1
                        self.mouse[0] = event.pos
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.mouse[event.button] = 0
                        self.mouse[0] = event.pos
                    elif event.type == pygame.MOUSEMOTION:
                        self.mouse[0] = event.pos
                    elif event.type == pygame.KEYDOWN:
                        self.keys[event.key % 322] = 1
                        if event.key == pygame.K_BACKSLASH:
                            saveScreenShot("Screen-shots", self.screen)
                    elif event.type == pygame.KEYUP:
                        self.keys[event.key % 322] = 0
                    if self.menu.active:
                        self.menu.handleEvent(event)
                    if self.chatconsole.active:
                        self.chatconsole.handleEvent(event)
                # game-level key input:
                # somehow delete key will destroy ship and when back out of
                # menu will again destroy ship
                # when this schript part is in scripts thats
                # why it is still here.
                if self.keys[K_DELETE % 322]:
                    self.keys[K_DELETE % 322] = False
                    # suicide
                    self.player.kill()

                self.debug = False
                if self.keys[K_BACKSPACE % 322]:
                    self.keys[K_BACKSPACE % 322] = False
                # ctrl+q or alt+F4 quit:
                L_ALT_F4 = (self.keys[K_LALT % 322] and self.keys[K_F4 % 322])
                R_ALT_F4 = (self.keys[K_RALT % 322] and self.keys[K_F4 % 322])
                L_CTRL_Q = (self.keys[K_LCTRL % 322] and self.keys[K_q % 322])
                R_CTRL_Q = (self.keys[K_RCTRL % 322] and self.keys[K_q % 322])
                if (L_ALT_F4 or R_ALT_F4 or L_CTRL_Q or R_CTRL_Q):
                    self.running = False

                for trigger in self.triggers:
                    trigger.update()

                self.universe.update()
                self.universe.draw(self.screen)

                # self.camera.update()
                # self.camera.draw(self.screen)

                # paused:

                if self.menu.active:
                    self.menu.update()
                    self.menu.draw(self.screen)

                if self.chatconsole.active:
                    self.chatconsole.update()
                    self.chatconsole.draw(self.screen)

                # update actually parses input.
                # and does actions based upon that.
                self.commandParse.update()
                # reloading logic, couldn't make it work
                # from inside the commandParse class
                # reloads the module so it imports new code.
                if self.commandParse.reload:
                    self.commandParse.reload = False
                    reload(commandParse)
                    self.commandParse = CommandParse(self, self.chatconsole,
                                                     self.messenger)

                # frame maintainance:
                pygame.display.flip()
                if self.fpscounter >= 30:
                    self.fpscounter = 0
                self.fpses[self.fpscounter] = self.fps
                self.fpscounter += 1
                self.averagefps = reduce(lambda x, y: x+y, self.fpses)/30

                # aim for FPS but adjust vars for self.fps.
                self.clock.tick(FPS)
                self.fps = max(1, int(self.clock.get_fps()))
                self.timer += 1. / self.fps
                # try and print debuging caption
                try:
                    disp_str = 'Memory usage: %d(KB) %d(MB) %d(GB) FPS: %d'
                    memUse = int(resource.getrusage(
                                 resource.RUSAGE_SELF).ru_maxrss)
                    memUseMB = memUse/1024
                    memUseGB = memUseMB/1024
                    fps = self.averagefps
                    pygame.display.set_caption(disp_str % (memUse, memUseMB,
                                               memUseGB, fps))
                except Exception:
                    pygame.display.set_caption('FPS: %d' % (self.averagefps))
            # end round loop (until gameover)
        # end game loop
        # self.__init__(self.screen)