**Test Cases Explanation**

**1) Normal Case**
- Host: cat.jpg
- Secret: ict.jpg

> Expected result: Embeds normally; extracted image matches secret (or resized version)

-------------------------------------------------------------------------------
Steps:
Embed → cat.jpg → ict.jpg → hidden1.png
Extract → hidden1.png → reveal1.png
-------------------------------------------------------------------------------

**2) Secret Image Too Large**
- Host: cat.jpg
- Secret: mu.jpg

> Expected result: Program displays warning and resizes secret image automatically

-------------------------------------------------------------------------------
Steps:
Embed → cat.jpg → mu.jpg → hidden2.png
-------------------------------------------------------------------------------

**3) Host Image Too Small**
- Host: small_cat.png
- Secret: ict.jpg

> Expected result: Program stops and shows error; no output generated

-------------------------------------------------------------------------------
Steps:
Embed → small_cat.png → ict.jpg
-------------------------------------------------------------------------------

