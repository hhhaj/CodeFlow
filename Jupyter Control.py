bl_info = {
    "name": "Jupyter Control",
    "author": "Hazzaa Alhajri",
    "version": (1, 0),
    "blender": (3, 4, 1),
    "location": "Text Editor > Run in Parts",
    "description": "Allows running code in parts within the Text Editor",
    "category": "Development",
}

import bpy
import random
import sys
import io

addon_registered = False  # Flag to track if the add-on is registered
part_counter = 1  # Counter for part numbers

# This operator adds a new cell of code to the Text Editor
class JupyterAddonOperator(bpy.types.Operator):
    bl_idname = "jupyter.add_cell"  # Unique identifier for the operator
    bl_label = "➕"  # Emoji for Add Cell
    bl_description = "Add a new cell"  # Tooltip for Add Cell

    # This method is called when the operator is executed
    def execute(self, context):
        self.add_part()  # Call the function to add a code block
        return {'FINISHED'}

    # This method adds a new cell of code at the current cursor position
    def add_part(self):
        global part_counter  # Declare part_counter as global

        # Find the active text data block
        text_data = bpy.context.edit_text

        # Get the current cursor position
        cursor_position = text_data.current_character

        # Define the code for the current part
        code = f"def part_{part_counter}():\n    # Code for part {part_counter}\n"

        # Insert the code at the cursor position
        text_data.write(code)

        # Move the cursor to the end of the inserted code
        text_data.current_character = cursor_position + len(code)

        # Increment the part counter
        part_counter += 1

def get_existing_part_functions():
    return [name for name in globals() if name.startswith("part_")]

# This operator runs the current cell of code in the Text Editor
class RunCellOperator(bpy.types.Operator):
    bl_idname = "jupyter.run_cell"  # Unique identifier for the operator
    bl_label = "▶️"  # Emoji for Run Cell
    bl_description = "Run current cell"  # Tooltip for Run Cell

    # This method is called when the operator is executed
    def execute(self, context):
        self.run_single_cell()  # Call the function to run a single cell
        return {'FINISHED'}

    # This method runs the current cell of code and adds a # CELL SUCCESS comment
    def run_single_cell(self):
        # Find the active text data block
        text_data = bpy.context.edit_text

        # Get the current line number
        line_number = text_data.current_line_index

        # Remove any existing # CELL SUCCESS comments
        for line in text_data.lines:
            if "# CELL SUCCESS" in line.body:
                line.body = line.body.replace("# CELL SUCCESS", "")

        # Get the code of the next function
        function_code = ""
        while line_number < len(text_data.lines) and text_data.lines[line_number].body.strip() != "":
            line = text_data.lines[line_number].body
            function_code += line + "\n"
            line_number += 1

        # Redirect print statements to Python Console
        original_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        # Run the code of the next function in the global scope
        exec(function_code, globals())

        # Restore the original stdout and print the captured output to Python Console
        sys.stdout = original_stdout
        captured_output = redirected_output.getvalue()

        # Get the Python console area
        console_area = next(area for area in bpy.context.screen.areas if area.type == 'CONSOLE')

        # Override the context
        override = bpy.context.copy()
        override['area'] = console_area

        # Append captured_output to the console
        bpy.ops.console.scrollback_append(override, text=captured_output, type='OUTPUT')

        # Add a # CELL SUCCESS comment at the end of the cell
        text_data.write("# CELL SUCCESS\n")

        # Remove the # CELL SUCCESS comment
        text_data.lines[-1].body = text_data.lines[-1].body.replace("# CELL SUCCESS", "")

# This operator runs all cells of code after the current cell in the Text Editor
class RunAfterOperator(bpy.types.Operator):
    bl_idname = "jupyter.run_after"  # Unique identifier for the operator
    bl_label = "⏭️"  # Emoji for Run After
    bl_description = "Run all cells after cursor line"  # Tooltip for Run After

    # This method is called when the operator is executed
    def execute(self, context):
        self.run_code_after_current_cell()  # Call the function to run code after the current cell
        return {'FINISHED'}

    # This method runs all cells of code after the current cell
    def run_code_after_current_cell(self):
        # Find the active text data block
        text_data = bpy.context.edit_text

        # Get the current line number
        line_number = text_data.current_line_index

        # Get the code after the current line
        code = "\n".join([line.body for line in text_data.lines[line_number+1:]])

        # Redirect print statements to Python Console
        original_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        # Run the code in the global scope
        exec(code, globals())

        # Restore the original stdout and print the captured output to Python Console
        sys.stdout = original_stdout
        captured_output = redirected_output.getvalue()

        # Get the Python console area
        console_area = next(area for area in bpy.context.screen.areas if area.type == 'CONSOLE')

        # Override the context
        override = bpy.context.copy()
        override['area'] = console_area

        # Append captured_output to the console
        bpy.ops.console.scrollback_append(override, text=captured_output, type='OUTPUT')


def menu_func(self, context):
    self.layout.operator("jupyter.add_cell")  # Add the "Add Cell" operator to the menu
    self.layout.operator("jupyter.run_cell")  # Add the "Run Cell" operator to the menu
    self.layout.operator("jupyter.run_after")  # Add the "Run After" operator to the menu

def register():
    if not hasattr(bpy.types, 'JupyterAddonOperator'):
        bpy.utils.register_class(JupyterAddonOperator)  # Register the "Add Cell" operator
    if not hasattr(bpy.types, 'RunCellOperator'):
        bpy.utils.register_class(RunCellOperator)  # Register the "Run Cell" operator
    if not hasattr(bpy.types, 'RunAfterOperator'):
        bpy.utils.register_class(RunAfterOperator)  # Register the "Run After" operator
    bpy.types.TEXT_MT_editor_menus.append(menu_func)  # Add operators to the Text Editor menu

def unregister():
    global addon_registered

    if addon_registered:
        bpy.utils.unregister_class(JupyterAddonOperator)  # Unregister the "Add Cell" operator
        bpy.utils.unregister_class(RunCellOperator)  # Unregister the "Run Cell" operator
        bpy.utils.unregister_class(RunAfterOperator)  # Unregister the "Run After" operator
        bpy.types.TEXT_MT_editor_menus.remove(menu_func)  # Remove operators from the Text Editor menu
        addon_registered = False

if __name__ == "__main__":
    register()  # Call register() if the script is executed directly
