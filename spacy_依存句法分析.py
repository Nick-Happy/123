import spacy

# 加载英文语言模型
nlp = spacy.load("models\en_core_web_sm")

# 输入文本
text = """
Honor of Kings: The Ultimate 5v5 Hero Battle Game


Honor of Kings International Edition, developed by Tencent Timi Studio and published by Level Infinite, is the world's most popular mobile MOBA game. Dive into the classic MOBA excitement with 5V5 hero's gorge, fair matchups; numerous battle modes and a vast selection of heroes allow you to demonstrate your dominance with first blood, pentakills, and legendary feats, crushing all competition! Localized hero voiceovers, skins, and smooth server performance ensure quick matchmaking, teaming up with friends for ranking battles, and enjoying all the fun of PC MOBAs and action games as you ascend to the pinnacle of honor! The enemy is nearing the battlefield—players, rally your allies for team battles in Honor of Kings!


Moreover, Honor of Kings invites you to partake in top global eSports events! Cheer for your favorite teams, witness thrilling, fervent gameplay, and even become a player yourself, standing on the global stage as a mobile legend MOBA player! It's all in your hands! Here, you are not a playerunknow; enjoy the battleground that's rightfully yours.


**Game Features**

1. 5V5 Tower Pushing Team Battles!

Classic 5V5 MOBA maps, three lanes to advance, providing the purest combat experience. Hero strategy combinations, forming the strongest team, seamless cooperation, showcasing extreme skills! Abundant wild monsters, a wide range of hero choices, battle after battle, fire freely, enjoying all the classic MOBA fun!


2. Legendary Heroes, Unique Skills, Dominate the Battlefield

Experience the power of heroes from myth and legend! Unleash their unique skills and experience completely different gameplay fun. Master the special skills of each hero, become a legend on the battlefield! Challenge your operations and strategies in the peak showdown of skills, experience unparalleled gaming fun. Choose your favorite heroes, unleash their power, fight alongside your teammates, conquer opponents, and create legends!


3. Ready to Team Up with Friends Anytime! Experience Ultimate Competitive Gameplay in 15 Minutes!

A MOBA game tailored for mobile, enjoy competitive gaming in just 15 minutes. Use your intellect in battle, combine strategy with skill, fight to the death, and become the MVP of the match! Team up with friends anytime, coordinate with rational hero selections, use your synergy with friends to sweep the battlefield with skill combinations, and become the heroes who dominate the battlefield!


4. Team-Based Fair Competition! Fun and Fair, It's All About Skill!

Dominate the field with skill, pursuing glory with your team. No hero cultivation, no stamina system, bringing back the original joy of gaming! A fair competitive environment without additional pay-to-win aspects. Superior skill and strategy are your only means to victory and championship honor.

Enter the mobile arena where legends are born, and valor is tested with every challenge you face.


5. Local Servers, Local Voiceovers, Local Game Content, Smooth gaming, immersive experience!

Local servers ensure smooth gaming experiences for you; localized hero voiceovers immerse you in every exciting battle; localized heroes and skins allow you to use your familiar heroes to achieve victory. At the same time, Honor of Kings prepares excellent AI for you. When you or your teammates disconnect, the AI will temporarily control the character to assist you in continuing the battle, ensuring you don't lose the victory due to outnumbered battles.
"""

# 依存句法分析
doc = nlp(text)

# # 输出名词短语
words_split = []
for chunk in doc.noun_chunks:
    words_split.append(chunk.text)
print(words_split)



