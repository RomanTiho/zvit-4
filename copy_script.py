import shutil

files = [
    (r"C:\Users\roman\.gemini\antigravity\brain\d62901f5-bd4e-42f8-bbde-92d36a2aa0e7\hero_1_1773829154977.png", r"d:\zvit4\diplom\frontend\images\hero_1.png"),
    (r"C:\Users\roman\.gemini\antigravity\brain\d62901f5-bd4e-42f8-bbde-92d36a2aa0e7\hero_2_1773829168388.png", r"d:\zvit4\diplom\frontend\images\hero_2.png"),
    (r"C:\Users\roman\.gemini\antigravity\brain\d62901f5-bd4e-42f8-bbde-92d36a2aa0e7\hero_3_1773829183782.png", r"d:\zvit4\diplom\frontend\images\hero_3.png")
]

for src, dst in files:
    try:
        shutil.copy(src, dst)
        print(f"Copied {src} to {dst}")
    except Exception as e:
        print(f"Failed to copy {src}: {e}")
