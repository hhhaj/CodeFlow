import bpy



# Get the Python console area
console_area = next(area for area in bpy.context.screen.areas if area.type == 'CONSOLE')



# Override the context
override = bpy.context.copy()
override['area'] = console_area

def part_2():
    return "Part 2:"
part_2_output = part_2()


# Append a newline before and after the output for better spacing
bpy.ops.console.scrollback_append(override, text="\n" + part_2_output + "\n", type='OUTPUT')
