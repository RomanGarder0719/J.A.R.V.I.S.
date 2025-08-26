from PIL import Image, ImageSequence

input_path = "jarvis_centered.gif"
output_path = "jarvis_wider.gif"

# Новые размеры
new_width = 420
new_height = 300
canvas_size = (420, 380)

gif = Image.open(input_path)
frames = []

for frame in ImageSequence.Iterator(gif):
    frame = frame.convert("RGBA").resize((new_width, new_height), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    canvas.paste(frame, (0, (canvas_size[1] - new_height) // 2), mask=frame)

    frames.append(canvas)

frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=gif.info['duration'], loop=0, disposal=2)
