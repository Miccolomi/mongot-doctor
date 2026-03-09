with open("mongot_monitor.py", "r") as f:
    text = f.read()

text = text.replace("Errhours", "Error")
text = text.replace("chours", "core")
text = text.replace("Chours", "Cores")

with open("mongot_monitor.py", "w") as f:
    f.write(text)
