from glm import ivec2, ivec3
import numpy as np
from gdpc import Editor, lookup, geometry, Block, Box, Rect
from gdpc.vector_tools import addY,DIAGONALS_3D,UP,DOWN,EAST,WEST,NORTH,SOUTH, dropY


EAST_2D  = ivec2( 1, 0)
WEST_2D  = ivec2(-1, 0)
NORTH_2D = ivec2( 0,-1)
SOUTH_2D = ivec2( 0, 1)

RELATIVE_POSITION_3X3 = [ivec2(1,1),[ivec2(0,0),ivec2(0,1),ivec2(0,2),ivec2(1,2),ivec2(2,2),ivec2(2,1),ivec2(2,0),ivec2(1,0)]]
ORIENTATIONS = {1:"west",-1:"east",2:"north",-2:"south"}

class HeighRelativeBlock:
    def __init__(self,block,height) -> None:
        self.block = block
        self.height = height

def carpet3x3():
     carpet_block = Block(np.random.choice(list(lookup.CARPETS)))
     return [
             [HeighRelativeBlock(carpet_block,0)],
             [
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)] 
             ]
            ]

def table3x3():
    return [
             [HeighRelativeBlock(Block("oak_fence"),0),HeighRelativeBlock(Block("oak_pressure_plate"),1)],
             [
                [],
                [HeighRelativeBlock(Block("oak_stairs",{"facing":"west"}),0)],
                [],
                [HeighRelativeBlock(Block("oak_stairs",{"facing":"south"}),0)],
                [],
                [HeighRelativeBlock(Block("oak_stairs",{"facing":"east"}),0)],
                [],
                [HeighRelativeBlock(Block("oak_stairs",{"facing":"north"}),0)] 
             ]
            ]


def bed_v1(orientation):
    return [
            [HeighRelativeBlock(Block(np.random.choice(list(lookup.BEDS)),{"facing":ORIENTATIONS[orientation]}),0)],
            [
                [HeighRelativeBlock(Block("bookshelf"),0),HeighRelativeBlock(Block("potted_cactus"),1)],
                [],
                [HeighRelativeBlock(Block("chest",{"facing":ORIENTATIONS[-orientation] }),0)],
                [],
                [],
                [],
                [],
                [] 
            ]
            ]
def bed_v2(orientation):
    return [
            [HeighRelativeBlock(Block(np.random.choice(list(lookup.BEDS)),{"facing":ORIENTATIONS[orientation]}),0)],
            [
                [HeighRelativeBlock(Block("bookshelf"),0),HeighRelativeBlock(Block("candle",{"candles":3,"lit":True}),1)],
                [],
                [HeighRelativeBlock(Block("jukebox"),0)],
                [],
                [],
                [],
                [],
                [] 
            ]
            ]

def storage_area(orientation):
    return[
            [],
            [
                [HeighRelativeBlock(Block("chest",{"facing":ORIENTATIONS[-orientation], "type":"left"}),0),HeighRelativeBlock(Block("chest",{"facing":ORIENTATIONS[-orientation], "type":"left" }),1)],
                [HeighRelativeBlock(Block("chest",{"facing":ORIENTATIONS[-orientation], "type":"right"}),0),HeighRelativeBlock(Block("chest",{"facing":ORIENTATIONS[-orientation], "type":"right"  }),1)],
                [HeighRelativeBlock(Block("bookshelf"),0),HeighRelativeBlock(Block("bookshelf"),1),HeighRelativeBlock(Block("bookshelf"),2)],
                [HeighRelativeBlock(Block("crafting_table"),0),HeighRelativeBlock(Block("candle",{"candles":3,"lit":True}),1)],
                [],
                [],
                [],
                [] 
            ]
            ]

class Structure3X3:
    @staticmethod
    def construct(editor,furniture):
        if(furniture.wall_orientaion == None):
            start = 0
            structures = [carpet3x3(),table3x3()]
            structure = structures[np.random.randint(len(structures))]
        else:
            if(furniture.wall_orientaion == 1):
                start = 0
            if(furniture.wall_orientaion == -2):
                start = furniture.dim   
            if(furniture.wall_orientaion == -1):
                start = 2*furniture.dim 
            if(furniture.wall_orientaion == 2):
                start = 3*furniture.dim 
        
            structures = [bed_v1(furniture.wall_orientaion),bed_v2(furniture.wall_orientaion),storage_area(furniture.wall_orientaion)]
            structure = structures[np.random.randint(len(structures))]

        for el in structure[0]:
            editor.placeBlock(
                        addY(furniture.start + RELATIVE_POSITION_3X3[0], el.height + furniture.y),
                        el.block
                    )
        for i in range(len(structure[1])):
                for el in structure[1][i]:
                    editor.placeBlock(
                        addY(furniture.start + RELATIVE_POSITION_3X3[1][(start+i)%8], el.height + furniture.y),
                        el.block
                    )
RELATIVE_POSITION_2X2 = [ivec2(0,0),ivec2(0,1),ivec2(1,1),ivec2(1,0)]

def books_v1():
    return[
            [HeighRelativeBlock(Block("bookshelf"),0),HeighRelativeBlock(Block("bookshelf"),1),HeighRelativeBlock(Block("bookshelf"),2)],
            [HeighRelativeBlock(Block("bookshelf"),0),HeighRelativeBlock(Block("bookshelf"),1),HeighRelativeBlock(Block("candle",{"candles":2,"lit":True}),2)],
            [],
            [HeighRelativeBlock(Block("bookshelf"),0),HeighRelativeBlock(Block("potted_mangrove_propagule"),1)],
    ]

def table2x2(): 
    return [
                [HeighRelativeBlock(Block("oak_stairs",{"facing":"west"}),0)],
                [HeighRelativeBlock(Block("oak_stairs",{"facing":"west"}),0)],
                [HeighRelativeBlock(Block("oak_fence"),0),HeighRelativeBlock(Block("oak_pressure_plate"),1)],
                [HeighRelativeBlock(Block("oak_fence"),0),HeighRelativeBlock(Block("oak_pressure_plate"),1)],
            ]

def carpet2x2():
    carpet_block = Block(np.random.choice(list(lookup.CARPETS)))
    return [
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
                [HeighRelativeBlock(carpet_block,0)],
            ]

def books_v2():
    return [
                [HeighRelativeBlock(Block("bookshelf"),0),HeighRelativeBlock(Block("bookshelf"),1),HeighRelativeBlock(Block("lantern"),2)],
                [HeighRelativeBlock(Block("bookshelf"),0)],
                [],
                [HeighRelativeBlock(Block("bookshelf"),0)],
            ]

def food_area(orientation):
    return [
                [HeighRelativeBlock(Block("smoker",{"facing":ORIENTATIONS[-orientation]}),0),HeighRelativeBlock(Block("spruce_trapdoor",{"half":"top"}),1)],
                [HeighRelativeBlock(Block("barrel",{"facing":ORIENTATIONS[-orientation]}),0),HeighRelativeBlock(Block("spruce_trapdoor",{"half":"top"}),1),HeighRelativeBlock(Block("lantern"),2)],
                [],
                [],
            ]


def armor_area(orientation):
    return [
                [HeighRelativeBlock(Block("blast_furnace",{"facing":ORIENTATIONS[-orientation]}),0),HeighRelativeBlock(Block("grindstone",{"facing":ORIENTATIONS[-orientation],"face":"floor"}),1),HeighRelativeBlock(Block("spruce_trapdoor"),2)],
                [HeighRelativeBlock(Block("anvil"),0),HeighRelativeBlock(Block("spruce_trapdoor"),2),HeighRelativeBlock(Block("lantern",{"hanging":True}),1)],
                [],
                [],
            ]

def storage_area_v2(orientation):
    return [
                [HeighRelativeBlock(Block("barrel",{"facing":ORIENTATIONS[-orientation]}),0),HeighRelativeBlock(Block("chest",{"facing":ORIENTATIONS[-orientation],"type":"left"}),1)],
                [HeighRelativeBlock(Block("crafting_table"),0),HeighRelativeBlock(Block("chest",{"facing":ORIENTATIONS[-orientation],"type":"right"}),1)],
                [],
                [],
            ]


class Structure2X2:
    @staticmethod
    def construct(editor,furniture):
        if(furniture.wall_orientaion == None):
            start = 0
            structures = [carpet2x2(),table2x2(),books_v2(),books_v2(),books_v2()]
            structure = structures[np.random.randint(len(structures))]
        else:
            if(furniture.wall_orientaion == 1):
                start = 0
            if(furniture.wall_orientaion == -2):
                start = furniture.dim 
            if(furniture.wall_orientaion == -1):
                start = 2*furniture.dim 
            if(furniture.wall_orientaion == 2):
                start = 3*furniture.dim 
        
            structures = [books_v1(),food_area(furniture.wall_orientaion),storage_area_v2(furniture.wall_orientaion),armor_area(furniture.wall_orientaion)]
            structure = structures[np.random.randint(len(structures))]

        for i in range(len(structure)):
                for el in structure[i]:
                    editor.placeBlock(
                        addY(furniture.start + RELATIVE_POSITION_2X2[(start+i)%4], el.height + furniture.y),
                        el.block
                    )

 






class Furniture:
    def __init__(self, start, dim, y, wall_orientaion=None) -> None:
        self.start = start
        self.dim = dim
        self.y = y
        self.wall_orientaion = wall_orientaion


    def construct(self,editor):
        if(self.dim == 1):
           
            Structure2X2.construct(editor,self)
            pass
        if(self.dim == 2):
            Structure3X3.construct(editor,self)




if __name__ == '__main__':
    try:
        editor = Editor()
        for _ in range(10):
            buildArea = editor.getBuildArea()
            buildRect = buildArea.toRect()
            worldSlice = editor.loadWorldSlice(buildRect)

            X1,Z1 = buildRect.begin 
            a = Furniture(buildRect.begin,1,-60)
            geometry.placeCuboid(editor,ivec3(X1,-60,Z1),ivec3(X1+3,-50,Z1+3),Block("air"))
            Structure2X2.construct(editor,a)

            a = Box(ivec3(X1 + 5, -61, Z1),ivec3(5,0,5))
            editor.setBuildArea(a)

    except KeyboardInterrupt: # useful for aborting a run-away program
        print("Pressed Ctrl-C to kill program.")


