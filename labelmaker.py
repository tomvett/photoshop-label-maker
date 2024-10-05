import csv
import os
from photoshop import Session
from photoshop.api.enumerations import LayerKind

csv_file_path = input("Enter the full path to the CSV file: ")

num_indexes = int(input("Enter the number of currencies (indexes): "))

text_layer_name = input("Enter the name of the name (TEXT) layer: ")

index_layers = {}

for i in range(num_indexes):
    main_layer_name = input(f"Enter the price (amount) layer name for index {i}: ")
    smart_layer_name = input(f"Enter the icon (smart object) layer name for index {i}: ")
    index_layers[i] = {
        "main_layer": main_layer_name,
        "smart_layer": smart_layer_name
    }

output_folder = "images"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

with Session() as ps:
    doc = ps.active_document
    
    layers = {}
    text_layer = None

    for layer in doc.artLayers:
        if layer.name == text_layer_name and layer.kind == LayerKind.TextLayer:
            text_layer = layer
        for i in range(num_indexes):
            if layer.name == index_layers[i]["main_layer"] and layer.kind == LayerKind.TextLayer:
                layers[f"main_layer_{i}"] = layer
            elif layer.name == index_layers[i]["smart_layer"] and layer.kind == LayerKind.SmartObjectLayer:
                layers[f"smart_layer_{i}"] = layer

    if not text_layer:
        print(f"Layer '{text_layer_name}' not found or it's not a text layer.")
        exit()

    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            name = row['Name'].upper()
            index = int(row['Index'])
            amount = row['Amount']

            text_layer.textItem.contents = name
            print(f"Layer '{text_layer_name}' updated to '{name}'.")

            main_layer = layers.get(f"main_layer_{index}")
            smart_layer = layers.get(f"smart_layer_{index}")

            if main_layer and smart_layer:
                for j in range(num_indexes):
                    layers[f"main_layer_{j}"].visible = (j == index)
                main_layer.textItem.contents = amount
                print(f"Layer '{index_layers[index]['main_layer']}' shown with amount '{amount}'.")

                for j in range(num_indexes):
                    layers[f"smart_layer_{j}"].visible = (j == index)

                print(f"Layer '{index_layers[index]['smart_layer']}' shown.")

                active_bounds = main_layer.bounds

                smart_layer_left = active_bounds[0] - 250
                translate_x_smart = smart_layer_left - smart_layer.bounds[0]
                smart_layer.translate(translate_x_smart, 0)

                combined_left = smart_layer.bounds[0]
                combined_right = active_bounds[2]
                combined_midpoint = (combined_left + combined_right) / 2

                canvas_center = doc.width / 2

                translate_x_center = canvas_center - combined_midpoint

                main_layer.translate(translate_x_center, 0)
                smart_layer.translate(translate_x_center, 0)

                print(f"Midpoint between '{name}' and '{amount}' layers centered on the canvas.")
            
                formatted_index = f"{i:04}"
                file_name = f"I_{formatted_index}_{name}.png"
                output_path = os.path.join(output_folder, file_name)
                options = ps.PNGSaveOptions()
                doc.saveAs(output_path, options, asCopy=True)
                print(f"Saved image as {output_path}")
            else:
                print(f"Layers for index {index} not properly found.")
