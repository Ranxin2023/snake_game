import collections
import threading
import time
from typing import List, Tuple
import random

class Game:
    def __init__(self, height:int=None, width:int=None, level:int=None, init_length:int=None, board_file:str=None, border:bool=True) -> None:
        self.border=border
        if level==8:
            self.sleep_time=0.15
        elif level==7:
            self.sleep_time=0.225
        else:
            self.sleep_time=(9-level)*0.1
        
        self.board=[]
        if board_file is not None:
            try:
                with open(board_file, "r") as file:
                    lines=file.readlines()
                    for line in lines:
                        self.board.append([])
                        for c in line:
                            if c=='\n':
                                break
                            self.board[-1].append(c)
            except FileNotFoundError:
                print(f"Error: The file {board_file} was not found.")
        self.height=height if height is not None else len(self.board)
        self.width=width if width is not None else len(self.board[0])
        # print(f"board is:\n{self.board}")
        # print(f"height is {self.height} width is: {self.width}")
        if len(self.board)==0:
            self.board=[['*' for _ in range(self.width)] for _ in range(self.height)]
        self.init_snake_length=init_length
        self.snake_length=0
        self.direction="right"
        self.old_direction="right"
        self.snake_coor=collections.deque()
        self.x=0
        while self.board[self.x][0]=='w':
            self.x+=1
        self.y=-1
        self.snake_head_shape={"left":'<', "right":'>', "up":'^', "down":'V'}
        self.snake_body_shape={"left":'-', "right":'-', "up":'|', "down":'|'}
        self.empty_cell:List[Tuple[int]]=[]
        self.score=0
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j]=='*':
                    self.empty_cell.append((i, j))

    def _capture_arrow_keys(self):
        """
        Uses keyboard module to detect arrow keys.
        Updates the snake direction in real time.
        """
        import keyboard

        while True:
            if keyboard.is_pressed("up") and self.direction != "down":
                self.direction = "up"
            elif keyboard.is_pressed("down") and self.direction != "up":
                self.direction = "down"
            elif keyboard.is_pressed("left") and self.direction != "right":
                self.direction = "left"
            elif keyboard.is_pressed("right") and self.direction != "left":
                self.direction = "right"
            time.sleep(0.05)  # small delay to reduce CPU usage

    def play(self):
        input_thread = threading.Thread(target=self._capture_arrow_keys, daemon=True)
        input_thread.start()
        self.generate_money()
        while True:
            print("-------------------------------------------")
            print(f"Current Score is {self.score}")
            print(f"Current Snake Length is is {self.snake_length}")
            print(f"location at: {self.x}, {self.y}")
            self.print_board()
            self.old_direction = self.direction
            alive = self.move()
            if len(self.empty_cell)==0:
                print("You reach the maximum length")
                print(f"You got a score of {self.score}")
                print("You Win")
                break
            if not alive:
                print(f"You got a score of {self.score}")
                print("Game Over")
                break

    def move(self)->bool:
        time.sleep(self.sleep_time)
        old_x=self.x
        old_y=self.y
        if self.direction=="right":
            self.y=self.y+1 if self.border else (self.y+1)%self.width
        if self.direction=="up":
            self.x=self.x-1 if self.border else (self.x+self.height-1)%self.height
        if self.direction=="down":
            self.x=self.x+1 if self.border else (self.x+1)%self.height
        if self.direction=="left":
            self.y=self.y-1 if self.border else (self.y+self.width-1)%self.width
        if self.x==-1 or self.y==-1 or self.x==self.height or self.y==self.width:
            return False
        old_cell=self.board[self.x][self.y]
        
        
        if self.board[self.x][self.y] in ['<','>','^','V','-','|', 'w']:
            return False
        # print(f"location at: {self.x}, {self.y}")
        # move the snake
        self.empty_cell.remove((self.x, self.y))
        
        self.snake_coor.append((self.x, self.y))
        self.board[self.x][self.y]=self.snake_head_shape[self.direction]
        
        if self.snake_length<=self.init_snake_length:
            self.snake_length+=1
        if old_x!=-1 and old_y!=-1:
            self.board[old_x][old_y]=self.snake_body_shape[self.old_direction]
        # not deque
        if old_cell!='$' and self.snake_length==self.init_snake_length+1:
            tail_x, tail_y=self.snake_coor.popleft()
            self.board[tail_x][tail_y]='*'
            self.snake_length-=1
            self.empty_cell.append((tail_x, tail_y))
        if old_cell=='$':
            self.init_snake_length+=1
            if len(self.empty_cell)==0:
                self.score+=1
                return False
            self.score+=1
            self.generate_money()
        return True
    
    def generate_money(self):
        idx=random.randint(0, len(self.empty_cell)-1)
        x, y=self.empty_cell[idx]
        # print(f"money cell is{x}, {y}")
        self.board[x][y]='$'

    def print_board(self):
        WALL = "\033[34m"
        RESET = "\033[0m"
        if self.border:
            for _ in range(2*self.width+5):
                print(f"{WALL}={RESET}", end="")
            print()
        for i in range(self.height):
            if self.border:
                print(f"{WALL}||{RESET}", end=" ")
            for j in range(self.width):
                cell = self.board[i][j]

                if cell in ['<','>','^','V','-','|']:   # snake:red
                    print(f"\033[31m{cell}\033[0m", end=" ")
                elif cell == '$':                      # food:gold yellow
                    print(f"\033[93m{cell}\033[0m", end=" ")
                elif cell == 'w':
                    print(f"\033[94m{cell}\033[0m", end=" ") 
                else:
                    print(cell, end=" ")

            if self.border:
                print(f"{WALL}||{RESET}", end="")
            print()
        if self.border:
            for _ in range(2*self.width+5):
                print(f"{WALL}={RESET}", end="")
            print()

def main():
    print("Please input the mode of the game, enter either 'classic' or 'map'")
    mode=input()
    print("please input the difficulty")
    difficulty=int(input())
    print("please input the init length")
    init_length=int(input())
    
    game:Game
    if mode=="classic" or mode=="c":
        print("Please input whether to have the border or not")
        border_input=input()
        border=False if border_input[0:1].lower()=='f' or border_input[0:1].lower()=='n' else True
        print("please input the height")
        height=int(input())
        print("please input the width")
        width=int(input())
        game=Game(height=height, width=width, level=difficulty, init_length=init_length, border=border)
        
    else:
        print("please input the game board file")
        board_file=str(input())
        game=Game(None, None, difficulty, init_length, "./game_boards/game"+board_file+".txt", border=None)
    game.play()

if __name__=="__main__":
    main()