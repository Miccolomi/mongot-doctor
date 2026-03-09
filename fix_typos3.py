with open("mongot_monitor.py", "r") as f:
    text = f.read()

text = text.replace("onper()", "super()")
text = text.replace("onm(", "sum(")
text = text.replace("reonlt", "result")
text = text.replace("_onm", "_sum")
text = text.replace(".onb", ".sub")
text = text.replace("pipe-onb", "pipe-sub")
text = text.replace("onbstantially", "substantially")
text = text.replace("cononmato", "consumato")
text = text.replace("Reonme", "Resume")
text = text.replace("Totalal", "Total")

with open("mongot_monitor.py", "w") as f:
    f.write(text)
