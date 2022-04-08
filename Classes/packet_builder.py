def buildLocP(x, y):
    locP = f'$LOC{x}.{y}'
    locP = str(len(locP)) + locP
    return locP


def buildMoveP(dirX, dirY):
    moveP = f'$MOVE{dirX}.{dirY}'
    moveP = str(len(moveP)) + moveP
    return moveP


def buildOtherPP(otherP):
    if otherP:
        otherPP = '$OTHERP'
        for player in otherP:
            otherPP += f'{player.x}.{player.y}@'
        otherPP = otherPP[:-1]
        otherPP = str(len(otherPP)) + otherPP
        return otherPP
    return ''


def buildMobsP(mobs):
    if mobs:
        mobP = '$MOBS'
        for mob in mobs:
            mobP += f'{mob.x}.{mob.y}.{mob.is_melee}@'
        mobP = mobP[:-1]
        mobP = str(len(mobP)) + mobP
        return mobP
    return ''


def buildParticlesP(particles):
    if particles:
        particleP = f'$PARTICLES'
        for particle in particles:
            particleP += f'{particle.x}.{particle.y}.{particle.angle}.{particle.name}@'
        particleP = particleP[:-1]
        particleP = str(len(particleP)) + particleP
        return particleP
    return ''


def buildSpearsP(spears):
    if spears:
        spearP = '$SPEARS'
        for spear in spears:
            spearP += f'{spear.x}.{spear.y}.{spear.angle}@'
        spearP = spearP[:-9]
        spearP = str(len(spearP)) + spearP
        return spearP
    return ''


def buildAttackP(mouseX, mouseY):
    attackP = f'$ATTACK{mouseX}.{mouseY}'
    attackP = str(len(attackP)) + attackP
    return attackP


def buildInventoryP(inv):
    inventoryP = '$INV'
    for i, slot in enumerate(inv):
        inventoryP += f'{slot}@'
    inventoryP = inventoryP[:-1]
    inventoryP = str(len(inventoryP)) + inventoryP
    return inventoryP


def buildSlotP(slot):
    slotP = f'$SLOT{slot}'
    slotP = str(len(slotP)) + slotP
    return slotP


def buildGoldP(gold):
    goldP = f'$GOLD{gold}'
    goldP = str(len(gold)) + goldP
    return goldP


def buildChatP(chatMsg):
    chatP = f'$CHAT' + chatMsg
    chatP = str(len(chatP)) + chatP
    return chatP


def buildAllServer(player, chatMsg):
    packet = buildLocP(player.x, player.y)
    packet += buildOtherPP(player.other_players_list)
    packet += buildMobsP(player.mobs_in_range)
    packet += buildParticlesP(player.particles_in_range)
    packet += buildSpearsP(player.spears_in_range)
    packet += buildInventoryP(player.inventory)
    packet += buildGoldP(player.gold)

    if chatMsg:
        packet += buildChatP(chatMsg)

    return packet

#mark is gay
def buildAllClientWithAttack(player, mouseX, mouseY, chatMsg):
    packet = buildMoveP(player.x, player.y)
    packet += buildAttackP(mouseX, mouseY)
    packet += buildSlotP(player.picked)

    if chatMsg:
        packet += buildChatP(chatMsg)

    return packet


def buildAllClient(player, chatMsg):
    packet = buildMoveP(player.x, player.y)
    packet += buildSlotP(player.picked)

    if chatMsg:
        packet += buildChatP(chatMsg)

    return packet
