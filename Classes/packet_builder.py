def build_location_packet(x, y):
    packet = f'$LOC{x}.{y}'
    packet = str(len(packet)) + packet
    return packet


def build_move_packet(dir_x, dir_y):
    packet = f'$MOVE{dir_x}.{dir_y}'
    packet = str(len(packet)) + packet
    return packet


def build_other_player_packet(other_players):
    if other_players:
        packet = '$OTHERP'
        for player in other_players:
            packet += f'{player.x}.{player.y}@'
        packet = packet[:-1]
        packet = str(len(packet)) + packet
        return packet
    return ''


def build_mob_packet(mobs):
    if mobs:
        packet = '$MOBS'
        for mob in mobs:
            packet += f'{mob.x}.{mob.y}.{mob.is_melee}@'
        packet = packet[:-1]
        packet = str(len(packet)) + packet
        return packet
    return ''


def build_particles_packet(particles):
    if particles:
        packet = f'$PARTICLES'
        for particle in particles:
            packet += f'{particle.x}.{particle.y}.{particle.angle}.{particle.name}@'
        packet = packet[:-1]
        packet = str(len(packet)) + packet
        return packet
    return ''


def build_spears_packet(spears):
    if spears:
        packet = '$SPEARS'
        for spear in spears:
            packet += f'{spear.x}.{spear.y}.{spear.angle}@'
        packet = packet[:-9]
        packet = str(len(packet)) + packet
        return packet
    return ''


def build_attack_packet(mouse_x, mouse_y):
    packet = f'$ATTACK{mouse_x}.{mouse_y}'
    packet = str(len(packet)) + packet
    return packet


def build_inventory_packet(inventory):
    packet = '$INV'
    for i, slot in enumerate(inventory):
        packet += f'{slot}@'
    packet = packet[:-1]
    packet = str(len(packet)) + packet
    return packet


def build_slot_packet(slot):
    packet = f'$SLOT{slot}'
    packet = str(len(packet)) + packet
    return packet


def build_gold_packet(gold):
    packet = f'$GOLD{gold}'
    packet = str(len(gold)) + packet
    return packet


def build_chat_packet(chat_message):
    packet = f'$CHAT' + chat_message
    packet = str(len(packet)) + packet
    return packet


def build_all_server(player, chat_message):
    packet = build_location_packet(x=player.x, y=player.y)
    packet += build_other_player_packet(other_players=player.other_players_list)
    packet += build_mob_packet(mobs=player.mobs_in_range)
    packet += build_particles_packet(particles=player.particles_in_range)
    packet += build_spears_packet(spears=player.spears_in_range)
    packet += build_inventory_packet(inventory=player.inventory)
    packet += build_gold_packet(gold=player.gold)
    if chat_message:
        packet += build_chat_packet(chat_message=chat_message)
    return packet


def build_all_client(player, mouse_x, mouse_y, chat_message):
    packet = build_move_packet(dir_x=player.x, dir_y=player.y)
    packet += build_slot_packet(slot=player.picked)
    if mouse_x and mouse_y:
        packet += build_attack_packet(mouse_x=mouse_x, mouse_y=mouse_y)
    if chat_message:
        packet += build_chat_packet(chat_message=chat_message)
    return packet
