with open("mongot_monitor.py", "r") as f:
    text = f.read()

text = text.replace("sthours", "store")
text = text.replace("sc.getmhours", "sc.getmores")
text = text.replace("getMhours", "getMores")
text = text.replace("importErrhours", "importError")
text = text.replace("ImportErrhours", "ImportError")
text = text.replace("TypeErrhours", "TypeError")

with open("mongot_monitor.py", "w") as f:
    f.write(text)
