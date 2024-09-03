import os
import subprocess
import pystray
from PIL import Image, ImageDraw

def create_image(width, height, color1, color2):
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2),fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)

    return image

# Get all available power plans and put them in an array
def get_power_plans():
    # Define some strings we'll use
    begin_line = "Power Scheme GUID: "
    split_char = " "
    guid_location = 3
    name_start_location = 5

    output = subprocess.run(["powercfg", "/l"], stdout=subprocess.PIPE).stdout.decode("utf-8").splitlines()

    print(output)

    power_plans = dict()

    for line in output:
        if line.startswith(begin_line):
            if split_char in line:
                line_array = line.split(split_char)
                guid = line_array[guid_location]
                name_array = line_array[name_start_location:]
                is_active = False

                # If a power plan is marked with "*", then it's active, so change its status then remove "*" from the string
                if (name_array[-1] == "*"):
                    is_active = True
                    del name_array[-1]

                # Recreate the string from the array, and then strip the surrounding parenthesis
                name = " ".join(name_array)[1:-1]

                # Populate the dict with the format {<GUID>: (<Name of Power Plan>, <Power Plan Status>)}
                power_plans[guid] = (name, is_active)
                

    return power_plans

def set_power_plan(guid, icon):
    subprocess.run(["powercfg", "/s", guid])
    icon.notify(guid)

def create_menu_item(guid):
    return pystray.MenuItem(
        text=get_power_plans()[guid][0],
        action=lambda icon : set_power_plan(guid, icon),
        checked=lambda status : get_power_plans()[guid][1],
        radio=True
    )

def create_icon(power_plans):
    menu_items = []

    menu_items.append(pystray.MenuItem(
        text="Power Options",
        action=lambda : subprocess.run(["powercfg.cpl"], shell=True),
        default=True
    ))
    
    menu_items.append(pystray.Menu.SEPARATOR)

    for guid in power_plans:
        menu_items.append(create_menu_item(guid))

    menu_items.append(pystray.Menu.SEPARATOR)


    # Append separator and exit
    menu_items.append(pystray.MenuItem(
        text="Exit",
        action=lambda icon : icon.stop()
    ))

    return pystray.Icon(
        name="Power Plan Changer",
        icon=create_image(64, 64, "black", "white"),
        menu=menu_items
    )


def main():
    icon = create_icon(get_power_plans())
    icon.run()

if __name__ == "__main__":
    main()