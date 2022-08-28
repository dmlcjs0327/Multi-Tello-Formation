from tello import Tello
from tello_control_ui import TelloUI


def main():
    vplayer = TelloUI(Tello(),"./img/")
    vplayer.root.mainloop() 

if __name__ == "__main__": main()
