from PIL import Image

with Image.open("assets/player_board.png") as img:
    img = img.resize((1000, 720))
    img.save("assets/player_board_resized.png")



















