from fonts import FONT_5X7

print("Total bytes :", len(FONT_5X7))
print("Characters  :", len(FONT_5X7) // 5)

print("\nSpace (ASCII 32):")
print(FONT_5X7[0:5])

index = (ord('A') - 32) * 5

print("\nCharacter A:")
print(FONT_5X7[index:index+5])

index = (ord('Z') - 32) * 5

print("\nCharacter Z:")
print(FONT_5X7[index:index+5])

index = (ord('0') - 32) * 5

print("\nCharacter 0:")
print(FONT_5X7[index:index+5])

index = (ord('9') - 32) * 5

print("\nCharacter 9:")
print(FONT_5X7[index:index+5])