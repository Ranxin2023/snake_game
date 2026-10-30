import collections
import random
import threading
import time

import questionary

from theme import THEMES, create_style

MAX_FILE_NUM=7

class Game:
    def __init__(self, height:int | None=None, width:int | None = None, level:int | None=None, 
                 init_length:int | None=None, board_file:str | None=None, border:bool=True) -> None:
        self.border=border
        self.difficulty=level
        if level==8:
            self.sleep_time=0.15
        elif level==7:
            self.sleep_time=0.21
        elif level==1:
            self.sleep_time=0.68
        elif level==2:
            self.sleep_time=0.61
        else:
            self.sleep_time=(9-level)*0.09
        
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
        self.empty_cell:list[tuple[int]]=[]
        self.score=0
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j]=='*':
                    self.empty_cell.append((i, j))
        self.direction_changed = False

    def _capture_arrow_keys(self):
        """
        Uses keyboard module to detect arrow keys.
        Updates the snake direction in real time.
        """
        import keyboard

        while True:
            if self.direction_changed:
                time.sleep(0.02)
                continue
            
                
            if (keyboard.is_pressed("up"))  or keyboard.is_pressed('W') and self.direction != "down":
                    self.direction = "up"
                    self.direction_changed=True
            elif (keyboard.is_pressed("down"))  or keyboard.is_pressed('S') and self.direction != "up":
                    self.direction = "down"
                    self.direction_changed=True
            elif (keyboard.is_pressed("left")) or keyboard.is_pressed('A') and self.direction != "right":
                    self.direction = "left"
                    self.direction_changed=True
            elif (keyboard.is_pressed("right"))  or keyboard.is_pressed('D') and self.direction != "left":
                    self.direction = "right"
                    self.direction_changed=True
            time.sleep(0.02) # small delay to reduce CPU usage

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
        self.direction_changed=False
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
                self.score+=self.difficulty
                return False
            self.score+=self.difficulty
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
    questions = [
        ("theme", "Choose your theme color:", list(THEMES.keys())),
        ("mode", "Choose game mode:", ["Classic", "Map"]),
        ("difficulty", "Choose difficulty:", list(range(1, 9))),
        ("init_length", "Choose initial snake length:", list(range(1, 6))),
    ]

    answers = {}
    step = 0
    style = None

    while True:
        # Add questions based on game mode
        current_questions = questions.copy()

        if answers.get("mode") == "Classic":
            current_questions += [
                ("border", "Enable border?", ["Yes", "No"]),
                ("height", "Choose board height:", None),
                ("width", "Choose board width:", None),
            ]

        elif answers.get("mode") == "Map":
            current_questions += [
                ("board_file", "Choose game map:", list(range(1, MAX_FILE_NUM + 1))),
            ]

        # All questions answered
        if step >= len(current_questions):
            break

        key, question, choices = current_questions[step]

        # Add Back option except for the first question
        if key in ("height", "width"):
            answer = questionary.text(
                question,
                default="10",
                style=style,
                validate=lambda x: (
                    x.lower() == "back"
                    or (x.isdigit() and 1 <= int(x) <= 50)
                )
            ).ask()

            if answer is not None:
                if answer.lower() == "back":
                    answer = "← Back"
                else:
                    answer = int(answer)

        else:
            if step > 0:
                choices = list(choices) + ["← Back"]

            answer = questionary.select(
                question,
                choices=[
                    questionary.Choice(str(c), value=c)
                    for c in choices
                ],
                style=style,
            ).ask()
        # Ctrl+C / Ctrl+D
        if answer is None:
            print("Game setup cancelled.")
            return

        # Go back
        if answer == "← Back":
            step -= 1
            continue

        # Save answer
        answers[key] = answer

        # Apply theme
        if key == "theme":
            style = create_style(answer)

        # Clear later answers when changing earlier selections
        for later_key, _, _ in current_questions[step + 1:]:
            answers.pop(later_key, None)

        step += 1

    # Create game
    if answers["mode"] == "Classic":
        game = Game(
            height=answers["height"],
            width=answers["width"],
            level=answers["difficulty"],
            init_length=answers["init_length"],
            border=answers["border"] == "Yes",
        )

    else:
        game = Game(
            height=None,
            width=None,
            level=answers["difficulty"],
            init_length=answers["init_length"],
            board_file=f"./game_boards/game{answers['board_file']}.txt",
            border=None,
        )

    game.play()


if __name__=="__main__":
    main()