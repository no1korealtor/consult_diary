import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Make sure trackerModal has id="trackerModal" class="modal-backdrop" style="display: none !important;"
text = text.replace('id="trackerModal" class="modal-backdrop"', 'id="trackerModal" class="modal-backdrop" style="display: none !important;"')
text = text.replace('id="trackerModal" class="modal-backdrop" style="display: none;"', 'id="trackerModal" class="modal-backdrop" style="display: none !important;"')

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Forced display: none !important on trackerModal!")
