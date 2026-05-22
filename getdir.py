import minescript as m

def yaw_to_direction(yaw):
    yaw = yaw % 360
    if yaw < 0:
        yaw += 360

    if yaw <= 45 or yaw > 315:
        return "South"
    elif yaw <= 135:
        return "West"
    elif yaw <= 225:
        return "North"
    else:
        return "East"

orientation = m.player_orientation()
yaw, pitch = orientation  # unpack as tuple

direction = yaw_to_direction(yaw)
m.echo(f"Facing: {direction} (yaw={yaw:.1f}, pitch={pitch:.1f})")