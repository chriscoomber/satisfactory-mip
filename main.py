from mip import *
import csv
import math


class Material:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Material({})".format(self.name)


class Solid(Material):
    def __str__(self):
        return "Solid({})".format(self.name)


class MinedSolid(Solid):
    def __str__(self):
        return "MinedSolid({})".format(self.name)


class ScavangedSolid(Solid):
    def __str__(self):
        return "ScavangedSolid({})".format(self.name)


class CraftedSolid(Solid):
    def __str__(self):
        return "CraftedSolid({})".format(self.name)


class Fluid(Material):
    def __str__(self):
        return "Fluid({})".format(self.name)


class MinedFluid(Fluid):
    def __str__(self):
        return "MinedFluid({})".format(self.name)


class CraftedFluid(Fluid):
    def __str__(self):
        return "CraftedFluid({})".format(self.name)


# Materials
materials = dict()
with open('recipes.csv', newline='', encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    first_row = reader.__next__()

    for row in reader:
        material1_name = row[first_row.index("product")]
        material2_name = row[first_row.index("ingredient1")]
        material3_name = row[first_row.index("ingredient2")]
        material4_name = row[first_row.index("ingredient3")]
        material5_name = row[first_row.index("ingredient4")]

        if material1_name != "":
            materials[material1_name] = Material(material1_name)
        if material2_name != "":
            materials[material2_name] = Material(material2_name)
        if material3_name != "":
            materials[material3_name] = Material(material3_name)
        if material4_name != "":
            materials[material4_name] = Material(material4_name)
        if material5_name != "":
            materials[material5_name] = Material(material5_name)

print([str(x) for x in materials.values()])


class Building:
    def __init__(self,
                 name,
                 power_in_mw,
                 integer_valued=True):
        self.name = name
        self.power_in_mw = power_in_mw
        self.integer_valued = integer_valued

    def __str__(self):
        return "Building({})".format(self.name)


# Buildings
buildings = dict()
with open('buildings.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    first_row = reader.__next__()

    for row in reader:
        building_name = row[first_row.index("name")]

        try:
            power_usage = int(row[first_row.index("powerUsage")])
        except ValueError:
            power_usage = 0

        try:
            power_generation = int(row[first_row.index("powerGenerated")])
        except ValueError:
            power_generation = 0

        if power_usage != 0 or power_generation != 0:
            power = int(power_generation - power_usage)
            buildings[building_name] = Building(building_name, power)

# Extra buildings / tweaks
buildings["AWESOME Sink"].integer_valued = False
buildings["Coal Generator"].integer_valued = False
buildings["Fuel Generator"].integer_valued = False
buildings["Miner"] = Building("Miner", -30)  # Add a generic miner building called "Miner", equiv to Miner mk 3
print([str(x) for x in buildings.values()])


class Recipe:
    """A class representing a recipe"""

    def __init__(self,
                 name,
                 building,
                 seconds,
                 alternative_recipe=False,
                 materials_dict=None,  # Dict from material identifier to quantity.
                 ):
        self.name = name
        self.building = building
        self.seconds = seconds
        self.alternative_recipe = alternative_recipe
        self.materials_dict = materials_dict if materials_dict is not None else {}

    def __str__(self):
        return "Recipe({} from {})".format(self.name, self.building)

    def rate_per_min(self):
        return float(60) / float(self.seconds)


# Recipes
recipes = dict()
with open('recipes.csv', newline='', encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    first_row = reader.__next__()

    for row in reader:

        if row[first_row.index("craftedIn")] == "" or row[first_row.index("craftedIn")] == "BuildGun":
            # ignore recipes for the build gun
            continue

        recipe_name = row[first_row.index("recipeName")]

        building_name = row[first_row.index("craftedIn")]
        try:
            building = buildings[building_name]
        except KeyError:
            continue

        seconds = row[first_row.index("craftingTime")]

        alternative_recipe = row[first_row.index("alternateRecipe")] == "Yes"
        if alternative_recipe:
            # For now, ignore alternatives
            continue

        product1_name = row[first_row.index("product")]
        product1 = materials[product1_name]
        product1_count = int(row[first_row.index("productCount")])
        materials_dict = {product1: product1_count}

        product2_name = row[first_row.index("product2")]
        if product2_name != "":
            product2 = materials[product2_name]
            product2_count = int(row[first_row.index("productCount2")])
            materials_dict[product2] = product2_count

        output1_name = row[first_row.index("ingredient1")]
        if output1_name != "":
            output1 = materials[output1_name]
            output1_count = -int(row[first_row.index("quantity1")])
            materials_dict[output1] = output1_count

        output2_name = row[first_row.index("ingredient2")]
        if output2_name != "":
            output2 = materials[output2_name]
            output2_count = -int(row[first_row.index("quantity2")])
            materials_dict[output2] = output2_count

        output3_name = row[first_row.index("ingredient3")]
        if output3_name != "":
            output3 = materials[output3_name]
            output3_count = -int(row[first_row.index("quantity3")])
            materials_dict[output3] = output3_count

        output4_name = row[first_row.index("ingredient4")]
        if output4_name != "":
            output4 = materials[output4_name]
            output4_count = -int(row[first_row.index("quantity4")])
            materials_dict[output4] = output4_count

        recipes[recipe_name] = Recipe(recipe_name, building, seconds, alternative_recipe, materials_dict)

# Extra recipes / tweaks
# AWESOME sink
fluids = ["Crude Oil", "Water", "Fuel", "Heavy Oil Residue", "Liquid Biofuel", "Alumina Solution", "Sulfuric Acid", "Turbofuel"]
sinks = {
    "Excess {}".format(material.name): Recipe("Excess {}".format(material.name), buildings["AWESOME Sink"], float(60) / float(780), materials_dict={material: -1})
    for material_name, material in materials.items()
    if material_name not in fluids
}
recipes.update(sinks)
# Power generation
generators = {
    "Power (from Coal)": Recipe("Power (from Coal)", buildings["Coal Generator"], 4, materials_dict={materials["Coal"]: -1, materials["Water"]: -3}),
    "Power (from Fuel)": Recipe("Power (from Fuel)", buildings["Fuel Generator"], 4, materials_dict={materials["Fuel"]: -1}),
    "Power (from Liquid Biofuel)": Recipe("Power (from Liquid Biofuel)", buildings["Fuel Generator"], 5, materials_dict={materials["Liquid Biofuel"]: -1}),
}
recipes.update(generators)


print([str(x) for x in recipes.values()])

# User input
required_materials_per_min = {materials["Smart Plating"]: 5, materials["Versatile Framework"]: 5, materials["Automated Wiring"]: 1}

# Calculations
m = Model()

# Decision variables are the number of buildings running each recipe. This is a dict from the recipe to the variable
# reference of the number of buildings for that recipe
x = {
    recipe: m.add_var()  # var_type=INTEGER if recipe.building.integer_valued else CONTINUOUS)
    for recipe in recipes.values()
}

# Objective is just to minimize number of buildings
m.objective = minimize(xsum(num_buildings for num_buildings in x.values()))

# Constraints
# Firstly, there's the constraints on each resource. Its total across all recipes must equal what the user requested.
# This is calculated by calculating for each recipe the number of that material produced per minute.
for material in materials.values():
    required_amount = required_materials_per_min[material] if material in required_materials_per_min else 0

    m += xsum(recipe.rate_per_min() * recipe.materials_dict[material] * num_buildings for recipe, num_buildings in x.items() if material in recipe.materials_dict) == required_amount

# Secondly, resulting power must be >ve.
m += xsum(recipe.building.power_in_mw * num_buildings for recipe, num_buildings in x.items()) >= 0

status = m.optimize()

results = {str(recipe): buildings.x for recipe, buildings in x.items() if buildings.x != 0 and buildings.x is not None and buildings.x > 0.001}

print("Requirements per min:")
for material, quantity in required_materials_per_min.items():
    print("    {}: {}".format(material, quantity))

print("Results: {}", status)
for recipe, num_buildings in results.items():
    print("    {}: {}".format(num_buildings, recipe))
