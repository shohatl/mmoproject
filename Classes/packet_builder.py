def buildMoveP(dirX, dirY):
    move = f'$MOVE{dirX}.{dirY}'
    move = str(len(move)) + move
    return move


def buildOtherPP(otherP):
    otherPP = '$OTHERP'
    for player in otherP:
        otherPP += f'{player.x}.{player.y}@'
    otherPP = otherPP[:-1]
    otherPP = str(len(otherPP)) + otherPP
    return otherPP


def buildMobsP(mobs):
    mobP = '$MOBS'
    for mob in mobs:
        mobP += f'{mob.x}.{mob.y}.{mob.is_melee}@'
    mobP = mobP[:-1]
    mobP = str(len(mobP)) + mobP
    return mobP


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


def buildAllServer(player, chatMsg):
    packet = buildMoveP(player.dir_x, player.dir_y)
    packet += buildOtherPP(player.other_players_list)
    packet += buildMobsP(player.mobs_in)
