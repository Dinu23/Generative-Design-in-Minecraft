from glm import ivec2, ivec3
import numpy as np
from gdpc import Editor, lookup, geometry, Block, Box, Rect
from gdpc.vector_tools import addY,DIAGONALS_3D,UP,DOWN,EAST,WEST,NORTH,SOUTH, dropY

from furniture import Furniture
class BlockPallet:
    
    def __init__(self,wood_type="oak") -> None:
        stones = ['cobblestone','stone','cobbled_deepslate']
        stone = stones[np.random.randint(len(stones))]
        self.floor_block = Block(stone)
        self.ceiling_block = Block(wood_type + "_planks")
        self.wall_block = Block(wood_type+"_planks")
        self.corner_block = Block(wood_type+"_log")
        self.border_flat_roof_block = Block(stone + "_slab")
        self.flat_roof_block = Block(wood_type+"_slab")
        self.roof_block = Block(wood_type+"_stairs")
        self.border_roof_block = Block(stone+"_stairs")
        self.door = Block(wood_type + "_door")
        self.glass = Block("glass_pane")
    



WIDTHS = [13,14,15]
LENGTHS = [13,14,15]
HEIGTHS = [4,5]
SIDES = [6,7]

ORIENTATIONS = ['SW']#,"NW","SE","NE"]

EAST_2D  = ivec2( 1, 0)
WEST_2D  = ivec2(-1, 0)
NORTH_2D = ivec2( 0,-1)
SOUTH_2D = ivec2( 0, 1)
DIRECTIONS_2D = [EAST_2D, WEST_2D, NORTH_2D, SOUTH_2D]
ALL_DIRECTIONS_NO_DIAGS = [UP,DOWN,EAST,WEST,NORTH,SOUTH]
ALL_DIRECTIONS = list(DIAGONALS_3D) + ALL_DIRECTIONS_NO_DIAGS

def add_tags_block(block,tags):
    return Block(block.id, tags)



class RoofTop:
    def __init__(self,direction ,x1, x2, z1, z2, flat_area) -> None:
        self.direction = direction
        self.x1 = x1 
        self.z1 = z1
        self.x2 = x2
        self.z2 = z2
        self.flat_area = flat_area


class House:
    def __init__(self, orientation, center, corner_NV, corner_SE, corners, floors, areas, ceiling_hight, roof_top) -> None:
        self.orientation = orientation
        self.center = center
        self.corner_NV = corner_NV
        self.corner_SE = corner_SE
        self.corners = corners
        self.floors = floors
        self.areas = areas
        self.ceiling_hight = ceiling_hight
        self.roof_top = roof_top
        self.block_pallete = None
        self.y = None 
        self.wall_positions = []
        self.door_position = None
        self.window_positions = []
        self.ladder_position = None

    def _construct_floor_and_ceiling(self,editor):
        for floor in self.floors:
            geometry.placeCuboid(editor,
                addY(floor.begin, self.y), # Corner 1
                addY(floor.end, self.y), # Corner 2
                self.block_pallete.floor_block
            )
            geometry.placeCuboid(editor,
                addY(floor.begin, self.y + self.ceiling_hight), # Corner 1
                addY(floor.end, self.y + self.ceiling_hight), # Corner 2
                self.block_pallete.ceiling_block
            )
    
    def _construct_walls(self,editor):
        for pos in range(len(self.corners)):
            start = self.corners[pos-1]
            end = self.corners[pos]
            geometry.placeCuboid(editor,
                addY(start, self.y+1), # Corner 1
                addY(end, self.y+self.ceiling_hight), # Corner 2
                self.block_pallete.wall_block  
            )

            if(start.x == end.x):
                x = start.x
                direction = ( 1 if end.y > start.y else -1)
                for z in range(start.y, end.y, direction):
                    self.wall_positions.append(ivec2(x,z))
            else:
                z = start.y
                direction = ( 1 if end.x > start.x else -1)
                for x in range(start.x, end.x, direction):
                  self.wall_positions.append(ivec2(x,z))

            


        for corner in self.corners:
            geometry.placeCuboid(editor,
                addY(corner, self.y), # Corner 1
                addY(corner, self.y + self.ceiling_hight), # Corner 2
                self.block_pallete.corner_block
            )

    def _construct_roof(self,editor):
        geometry.placeCuboid(editor,
            addY(self.roof_top.flat_area.begin, self.y + self.ceiling_hight+1), # Corner 1
            addY(self.roof_top.flat_area.end, self.y + self.ceiling_hight+1), # Corner 2
            self.block_pallete.flat_roof_block
        )
        xx1 = self.roof_top.flat_area.begin.x
        xx2 = self.roof_top.flat_area.end.x
        zz1 = self.roof_top.flat_area.begin.y
        zz2 = self.roof_top.flat_area.end.y

        for x in range(xx1, xx2 + (1 if xx1 < xx2 else -1), 1 if xx1 < xx2 else -1):
            editor.placeBlock(ivec3(x, self.y + self.ceiling_hight+1,zz1), self.block_pallete.border_flat_roof_block)
            editor.placeBlock(ivec3(x, self.y + self.ceiling_hight+1,zz2), self.block_pallete.border_flat_roof_block)
        for z in range(zz1, zz2 + (1 if zz1 < zz2 else -1), 1 if zz1 < zz2 else -1):
            editor.placeBlock(ivec3(xx1, self.y + self.ceiling_hight+1,z), self.block_pallete.border_flat_roof_block)
            editor.placeBlock(ivec3(xx2, self.y + self.ceiling_hight+1,z), self.block_pallete.border_flat_roof_block)
        
            

        if(self.roof_top.direction == 0):
            z1 = self.roof_top.z1
            z2 = self.roof_top.z2
            h = self.y + self.ceiling_hight + 1
            ok = False
            while(z1 < z2):
                geometry.placeCuboid(editor,
                    ivec3(self.roof_top.x1+1,h,z1+1), # Corner 1
                    ivec3(self.roof_top.x1+1,h,z2-1), # Corner 2
                    self.block_pallete.wall_block if ok else add_tags_block(self.block_pallete.corner_block,{"axis": "z"})
                )
                geometry.placeCuboid(editor,
                    ivec3(self.roof_top.x2-1,h,z1+1), # Corner 1
                    ivec3(self.roof_top.x2-1,h,z2-1), # Corner 2
                    self.block_pallete.wall_block if ok else  add_tags_block(self.block_pallete.corner_block,{"axis": "z"})
                    )
                

                geometry.placeCuboid(editor,
                    ivec3(self.roof_top.x1,h,z1), # Corner 1
                    ivec3(self.roof_top.x2,h,z1), # Corner 2
                    
                    add_tags_block(self.block_pallete.roof_block, {"facing": "south", "half": "bottom"}) if ok else add_tags_block(self.block_pallete.border_roof_block, {"facing": "south", "half": "bottom"})
                )

                editor.placeBlock(ivec3(self.roof_top.x1,h,z1), add_tags_block(self.block_pallete.border_roof_block, {"facing": "south", "half": "bottom"} ) )
                editor.placeBlock(ivec3(self.roof_top.x2,h,z1), add_tags_block(self.block_pallete.border_roof_block, {"facing": "south", "half": "bottom"} ))
                editor.placeBlock(ivec3(self.roof_top.x1,h,z1+1), add_tags_block(self.block_pallete.border_roof_block, {"facing": "north", "half": "top"} ))
                editor.placeBlock(ivec3(self.roof_top.x2,h,z1+1), add_tags_block(self.block_pallete.border_roof_block, {"facing": "north", "half": "top"} ))
                
                geometry.placeCuboid(editor,
                    ivec3(self.roof_top.x1,h,z2), # Corner 1
                    ivec3(self.roof_top.x2,h,z2), # Corner 2
                    add_tags_block(self.block_pallete.roof_block, {"facing": "north", "half": "bottom"}) if ok else add_tags_block(self.block_pallete.border_roof_block, {"facing": "north", "half": "bottom"})
                )

                editor.placeBlock(ivec3(self.roof_top.x1,h,z2),add_tags_block(self.block_pallete.border_roof_block, {"facing": "north", "half": "bottom"} ))
                editor.placeBlock(ivec3(self.roof_top.x2,h,z2),add_tags_block(self.block_pallete.border_roof_block, {"facing": "north", "half": "bottom"} ))
                editor.placeBlock(ivec3(self.roof_top.x1,h,z2-1),add_tags_block(self.block_pallete.border_roof_block, {"facing": "south", "half": "top"} ))
                editor.placeBlock(ivec3(self.roof_top.x2,h,z2-1),add_tags_block(self.block_pallete.border_roof_block, {"facing": "south", "half": "top"} ))

                ok= True
                z1 +=1
                z2 -=1
                h +=1

            if(z1 == z2):
                geometry.placeCuboid(editor,
                    ivec3(self.roof_top.x1,h,z1), # Corner 1
                    ivec3(self.roof_top.x2,h,z1), # Corner 2
                    self.block_pallete.border_flat_roof_block
                )
                editor.placeBlock(ivec3(ivec3(self.roof_top.x1,h-1,z1)),add_tags_block(self.block_pallete.border_roof_block, {"facing": "east", "half": "top"}) )
                editor.placeBlock(ivec3(ivec3(self.roof_top.x2,h-1,z1)),add_tags_block(self.block_pallete.border_roof_block, {"facing": "west", "half": "top"}) )
        else:
            x1 = self.roof_top.x1
            x2 = self.roof_top.x2
            h = self.y + self.ceiling_hight + 1
            ok = False
            while(x1 < x2):
                geometry.placeCuboid(editor,
                    ivec3(x1+1,h,self.roof_top.z1+1), # Corner 1
                    ivec3(x2-1,h,self.roof_top.z1+1),
                    self.block_pallete.wall_block if ok else add_tags_block(self.block_pallete.corner_block,{"axis": "x"})
                )
                geometry.placeCuboid(editor,
                    ivec3(x1+1,h,self.roof_top.z2-1), # Corner 1
                    ivec3(x2-1,h,self.roof_top.z2-1),
                    self.block_pallete.wall_block if ok else add_tags_block(self.block_pallete.corner_block,{"axis": "x"})
                )

                geometry.placeCuboid(editor,
                    ivec3(x1,h,self.roof_top.z1), # Corner 1
                    ivec3(x1,h,self.roof_top.z2), # Corner 2
                    add_tags_block(self.block_pallete.roof_block, {"facing": "east", "half": "bottom"}) if ok else add_tags_block(self.block_pallete.border_roof_block, {"facing": "east", "half": "bottom"})
                )

                editor.placeBlock(ivec3(x1,h,self.roof_top.z1),add_tags_block(self.block_pallete.border_roof_block, {"facing": "east", "half": "bottom"}) )
                editor.placeBlock(ivec3(x1,h,self.roof_top.z2),add_tags_block(self.block_pallete.border_roof_block, {"facing": "east", "half": "bottom"}) )
                editor.placeBlock(ivec3(x1+1,h,self.roof_top.z1),add_tags_block(self.block_pallete.border_roof_block, {"facing": "west", "half": "top"}) )
                editor.placeBlock(ivec3(x1+1,h,self.roof_top.z2),add_tags_block(self.block_pallete.border_roof_block, {"facing": "west", "half": "top"}) )

                geometry.placeCuboid(editor,
                    ivec3(x2,h,self.roof_top.z1), # Corner 1
                    ivec3(x2,h,self.roof_top.z2), # Corner 2
                    add_tags_block(self.block_pallete.roof_block, {"facing": "west", "half": "bottom"}) if ok else add_tags_block(self.block_pallete.border_roof_block, {"facing": "west", "half": "bottom"})
                )

                editor.placeBlock(ivec3(x2,h,self.roof_top.z1),add_tags_block(self.block_pallete.border_roof_block, {"facing": "west", "half": "bottom"}) )
                editor.placeBlock(ivec3(x2,h,self.roof_top.z2),add_tags_block(self.block_pallete.border_roof_block, {"facing": "west", "half": "bottom"}) )
                editor.placeBlock(ivec3(x2-1,h,self.roof_top.z1),add_tags_block(self.block_pallete.border_roof_block, {"facing": "east", "half": "top"}) )
                editor.placeBlock(ivec3(x2-1,h,self.roof_top.z2),add_tags_block(self.block_pallete.border_roof_block, {"facing": "east", "half": "top"}) )

                ok = True
                x1 +=1
                x2 -=1
                h +=1

            if(x1 == x2):
                geometry.placeCuboid(editor,
                    ivec3(x2,h,self.roof_top.z1), # Corner 1
                    ivec3(x2,h,self.roof_top.z2), # Corner 2
                    self.block_pallete.border_flat_roof_block
                )
                editor.placeBlock( ivec3(x2,h-1,self.roof_top.z1),add_tags_block(self.block_pallete.border_roof_block, {"facing": "south", "half": "top"}) )
                editor.placeBlock( ivec3(x2,h-1,self.roof_top.z2),add_tags_block(self.block_pallete.border_roof_block, {"facing": "north", "half": "top"}) )

    def construct(self, editor, y, block_pallete):
        print("Start building structure")
        self.y = y
        self.block_pallete = block_pallete
        self._construct_floor_and_ceiling(editor)
        self._construct_walls(editor)    
        self._construct_roof(editor)
        print("End building structure")
        

    def add_doors_windows(self,editor, window_probability):
        print("Start adding door and windows")
        valid_door_spots = []
        for pos in range(len(self.corners)):
            start = self.corners[pos-1]
            end = self.corners[pos]
            if(start.x == end.x):
                x = start.x
                direction = ( 1 if end.y > start.y else -1)
                for z in range(start.y + 2*direction, end.y-direction, direction):
                    loc = ivec2(x,z)
                    ok = True
                    for dir in DIRECTIONS_2D:
                        if(editor.getBlock(addY(loc+dir,self.y)) == 'minecraft:air'):
                            ok = False
                            break
                    if(ok):
                        valid_door_spots.append(loc)

            else:
                z = start.y
                direction = ( 1 if end.x > start.x else -1)
                for x in range(start.x + 2*direction , end.x-direction, direction):
                    loc = ivec2(x,z)
                    ok = True
                    for dir in DIRECTIONS_2D:
                        if(editor.getBlock(addY(loc+dir,self.y)) == 'minecraft:air'):
                            ok = False
                            break
                    if(ok):
                        valid_door_spots.append(loc)
        
        self.door_position = valid_door_spots[np.random.randint(len(valid_door_spots))]

        geometry.placeCuboid(
            editor,
            addY(self.door_position,self.y+1),
            addY(self.door_position,self.y+2),
            Block("air")
        )
        editor.placeBlock(  addY(self.door_position,self.y+1), self.block_pallete.door)

        for pos in range(len(self.corners)):
            start = self.corners[pos-1]
            end = self.corners[pos]
            if(start.x == end.x):
                x = start.x
                direction = ( 1 if end.y > start.y else -1)
                for z in range(start.y + 2*direction, end.y - direction, direction):
                    if(ivec2(x,z) != self.door_position):
                        ok=True
                        for dir in DIRECTIONS_2D:
                            if(ivec2(x,z) + dir == self.door_position):
                                ok=False
                                break
                        if(ok and np.random.random() < window_probability):
                            self.window_positions.append(ivec2(x,z))
                            geometry.placeCuboid(   
                                editor,
                                addY(ivec2(x,z),self.y+2),
                                addY(ivec2(x,z),self.y+3),
                                self.block_pallete.glass
                            )

            else:
                z = start.y
                direction = ( 1 if end.x > start.x else -1)
                for x in range(start.x + 2*direction, end.x - direction, direction):
                    if(ivec2(x,z) != self.door_position):
                        ok = True
                        for dir in DIRECTIONS_2D:
                            if(ivec2(x,z) + dir == self.door_position):
                                ok=False
                                break
                        if(ok and np.random.random() < window_probability):
                            self.window_positions.append(ivec2(x,z))
                            geometry.placeCuboid(
                                editor,
                                addY(ivec2(x,z),self.y+2),
                                addY(ivec2(x,z),self.y+3),
                                self.block_pallete.glass
                            )
        print("End adding door and windows")

    def create_attic(self, editor, proability_trash):
        print("Start add attic details")
        starting_point = addY(self.center, self.y + self.ceiling_hight + 1 )
        attic_blocks = np.array(fill_3d(editor,starting_point,["minecraft:air"],diretions=ALL_DIRECTIONS_NO_DIAGS )[16:])
        count_trash_spots = np.int32(len(attic_blocks)*proability_trash)

        trash_spots = attic_blocks[np.random.choice( len(attic_blocks),count_trash_spots,replace=False)]


        floating_blocks = [Block("cobweb")]

        ground_blocks = [Block("barrel"),Block("beehive"),Block("chest"),Block("bookshelf")]
        
        for spot in trash_spots:
            if(editor.getBlock(spot + DOWN).id not in ["minecraft:air", "minecraft:cobweb"]):
                editor.placeBlock(spot,np.random.choice(ground_blocks))
            else:
                editor.placeBlock(spot,np.random.choice(floating_blocks))

        ladder_position = None

        if(self.roof_top.direction == 0):
            pos1 = self.center + NORTH_2D
            pos2 = self.center + SOUTH_2D
            if(editor.getBlock(addY(pos1,self.y+1)).id == "minecraft:air"):
                ladder_position = pos1
                geometry.placeCuboid(
                    editor,
                    addY(pos1,self.y+1),
                    addY(pos1,self.y+self.ceiling_hight),
                    Block("ladder",{"facing": "north"})
                )
                editor.placeBlock(
                    addY(pos1,self.y+self.ceiling_hight),
                    Block("oak_trapdoor")
                )
            else:
                ladder_position = pos2
                geometry.placeCuboid(
                    editor,
                    addY(pos2,self.y+1),
                    addY(pos2,self.y+self.ceiling_hight),
                    Block("ladder",{"facing": "south"})
                )
                editor.placeBlock(
                    addY(pos2,self.y+self.ceiling_hight),
                    Block("oak_trapdoor")
                )
        else:
            pos1 = self.center + WEST_2D
            pos2 = self.center + EAST_2D
            if(editor.getBlock(addY(pos1,self.y+1)).id == "minecraft:air"):
                ladder_position = pos1
                geometry.placeCuboid(
                    editor,
                    addY(pos1,self.y+1),
                    addY(pos1,self.y+self.ceiling_hight),
                    Block("ladder",{"facing": "west"})
                )
                editor.placeBlock(
                    addY(pos1,self.y+self.ceiling_hight),
                    Block("oak_trapdoor")
                )
            else:
                ladder_position = pos2
                geometry.placeCuboid(
                    editor,
                    addY(pos2,self.y+1),
                    addY(pos2,self.y+self.ceiling_hight),
                    Block("ladder",{"facing": "east"})
                )
                editor.placeBlock(
                    addY(pos2,self.y+self.ceiling_hight),
                    Block("oak_trapdoor")
                )
        self.ladder_position = ladder_position
        print("End add attic details")

    def populate_inside(self, editor, no_of_structures):
        print("Start add furniture to ground floor")
        W = [1,2]
        structures = 0
        furnitures = []
        while(structures < no_of_structures or (structures >= no_of_structures and np.random.rand()<0.6)):
            # print()
            dim = np.random.choice(W)
            

            x = np.random.randint(self.corner_NV.x+1, self.corner_SE.x)
            z = np.random.randint(self.corner_NV.y+1, self.corner_SE.y)
            if(not(self.corner_NV.x+1 <= x + dim <= self.corner_SE.x-1)):
                continue
            if(not(self.corner_NV.y+1 <= z + dim <= self.corner_SE.y-1)):
                continue
            if(self.orientation == "NW"):
                a1 = self.corner_NV.x+1
                b1 = self.center.x
                a2 = self.corner_NV.y+1
                b2 = self.center.y
            if(self.orientation == "NE"):
                a1 = self.center.x
                b1 = self.corner_SE.x-1
                a2 = self.corner_NV.y+1
                b2 = self.center.y
            if(self.orientation == "SW"):
                a1 = self.corner_NV.x+1
                b1 = self.center.x
                a2 = self.center.y
                b2 = self.corner_SE.y-1
            if(self.orientation == "SE"):
                a1 = self.center.x
                b1 = self.corner_SE.x-1
                a2 = self.center.y
                b2 = self.corner_SE.y-1
            
            if(((a1 <= x <= b1) or (a1 <= x + dim <= b1)) and ((a2 <= z <= b2) or (a2 <= z + dim <= b2))):
                continue
            ok = True

            a1 = x - 1
            b1 = x + dim + 1
            a2 = z - 1
            b2 = z + dim + 1
            if((a1 <= self.door_position.x <= b1) and (a2 <= self.door_position.y <= b2)):
                continue
            if((a1 <= self.ladder_position.x <= b1) and (a2 <= self.ladder_position.y <= b2)):
                continue
            
            
            for furniture in furnitures:
                a1 = furniture.start.x - 1
                b1 = furniture.start.x + furniture.dim + 1
                a2 = furniture.start.y - 1
                b2 = furniture.start.y + furniture.dim + 1
                if(((a1 <= x <= b1) or (a1 <= x + dim <= b1)) and ((a2 <= z <= b2) or (a2 <= z + dim <= b2))):
                    ok = False
                    break
            
            if( not ok):
                continue
            
            wall_orietaion = None
            if(ivec2(x-1,z) in self.wall_positions):
                wall_orietaion = 1

            if(ivec2(x,z-1) in self.wall_positions):
                wall_orietaion = 2

            if(ivec2(x+dim+1,z) in self.wall_positions):
                wall_orietaion = -1

            if(ivec2(x,z+dim+1) in self.wall_positions):
                wall_orietaion = -2

            furniture = Furniture(ivec2(x,z),dim,self.y+1,wall_orietaion)
            furnitures.append(furniture)
            structures +=1

        for furniture in furnitures:
            furniture.construct(editor)
        print("End add furniture to ground floor")
          
    @staticmethod
    def create_house(x1,z1):
        print("Start creating blue print of the house")
        width = np.random.choice(WIDTHS)
        length = np.random.choice(LENGTHS)
        height = np.random.choice(HEIGTHS)
        w1 = np.random.choice(SIDES)
        w2 = np.random.choice(SIDES)
        roof_direction = np.random.randint(0,2)
        x3 = x1 + length
        z3 = z1 + width
        
        orientation = np.random.choice(ORIENTATIONS)

        

        if(orientation == 'NW'):
            x2 = x3 - w1 - 1
            z2 = z3 - w2 - 1
            center = ivec2(x2,z2)
            corners = [ivec2(x2,z2),ivec2(x2,z1), ivec2(x3,z1), ivec2(x3,z3), ivec2(x1,z3), ivec2(x1,z2)]
            floor_corners = [ivec2(x3,z3),ivec2(x1,z3),ivec2(x3,z1)]
            
            area_center = ivec2(x2-2,z2-2)
            area_corners = [ivec2(x3+2,z3+2),ivec2(x1-2,z3+2),ivec2(x3+2,z1-2)]
            
            
            

            if(roof_direction == 0):
                flat_area =  Rect(ivec2(x2-1,z2-1))
                flat_area.end = ivec2(x3+1,z1-1)
                roof = RoofTop(roof_direction,x1-1,x3+1,z2-1,z3+1,flat_area)
            else:
                flat_area =  Rect(ivec2(x2-1,z2-1))
                flat_area.end = ivec2(x1-1,z3+1)
                roof = RoofTop(roof_direction,x2-1,x3+1,z1-1,z3+1,flat_area)         

        if(orientation == 'NE'):
            x2 = x1 + w1 + 1
            z2 = z3 - w2 - 1
            center = ivec2(x2,z2)
            corners = [ivec2(x2,z2), ivec2(x3,z2), ivec2(x3,z3), ivec2(x1,z3), ivec2(x1,z1), ivec2(x2,z1)]
            floor_corners = [ivec2(x1,z3),ivec2(x3,z3),ivec2(x1,z1)]
            
            area_center = ivec2(x2+2,z2-2)
            area_corners = [ivec2(x1-2,z3+2),ivec2(x3+2,z3+2),ivec2(x1-2,z1-2)]

            if(roof_direction == 0):
                flat_area =  Rect(ivec2(x2+1,z2-1))
                flat_area.end = ivec2(x1-1,z1-1)
                roof = RoofTop(roof_direction,x1-1,x3+1,z2-1,z3+1,flat_area)
            else:
                flat_area =  Rect(ivec2(x2+1,z2-1))
                flat_area.end = ivec2(x3+1,z3+1)
                roof = RoofTop(roof_direction,x1-1,x2+1,z1-1,z3+1,flat_area)

        if(orientation == 'SW'):
            x2 = x3 - w1 - 1
            z2 = z1 + w2 - 1
            center = ivec2(x2,z2)
            corners = [ivec2(x2,z2), ivec2(x1,z2), ivec2(x1,z1), ivec2(x3,z1), ivec2(x3,z3), ivec2(x2,z3)]
            floor_corners = [ivec2(x3,z1),ivec2(x3,z3),ivec2(x1,z1)]

            area_center = ivec2(x2-2,z2+2)
            area_corners = [ivec2(x3+2,z1-2),ivec2(x3+2,z3+2),ivec2(x1-2,z1-2)]

            if(roof_direction == 0):
                flat_area =  Rect(ivec2(x2-1,z2+1))
                flat_area.end = ivec2(x3+1,z3+1)
                roof = RoofTop(roof_direction,x1-1,x3+1,z1-1,z2+1,flat_area)
            else:
                flat_area =  Rect(ivec2(x2-1,z2+1))
                flat_area.end = ivec2(x1-1,z1-1)
                roof = RoofTop(roof_direction,x2-1,x3+1,z1-1,z3+1,flat_area)
        
        if(orientation == 'SE'):
            x2 = x1 + w1 + 1
            z2 = z1 + w2 + 1
            center = ivec2(x2,z2)
            corners = [ivec2(x2,z2), ivec2(x2,z3), ivec2(x1,z3), ivec2(x1,z1), ivec2(x3,z1), ivec2(x3,z2)]
            floor_corners = [ivec2(x1,z1),ivec2(x1,z3),ivec2(x3,z1)]
            
            area_center = ivec2(x2+2,z2+2)
            area_corners = [ivec2(x1-2,z1-2),ivec2(x1-2,z3+2),ivec2(x3+2,z1-2)]

            if(roof_direction == 0):
                flat_area =  Rect(ivec2(x2+1,z2+1))
                flat_area.end = ivec2(x1-1,z3+1)
                roof = RoofTop(roof_direction,x1-1,x3+1,z1-1,z2+1,flat_area)
            else:
                flat_area =  Rect(ivec2(x2+1,z2+1))
                flat_area.end = ivec2(x3+1,z1-1)
                roof = RoofTop(roof_direction,x1-1,x2+1,z1-1,z3+1,flat_area)
            
        floors = []
        for corner in floor_corners:
            floor = Rect(center)
            floor.end = corner
            floors.append(floor)
        
        areas = []
        for corner in area_corners:
            area = Rect(area_center)
            area.end = corner
            areas.append(area)

        print("End creating blue print of the house")
        return House(orientation, center, ivec2(x1,z1), ivec2(x3,z3), corners, floors, areas, height, roof)

def fill_3d(editor,starting_point,types,diretions = ALL_DIRECTIONS, restricted =False, remove=False):
    buildArea = editor.getBuildArea()
    buildRect = buildArea.toRect()
    visited = [starting_point]
    count = 1
    i=0
    while(i < count):
        loc = visited[i]
        if(remove):
            editor.placeBlock(loc,Block("air"))
        for dir in diretions:
            new_loc = loc + dir
            if(restricted and not buildRect.contains(dropY(new_loc))):
                continue
            if(new_loc not in visited):
                block = editor.getBlock(new_loc)
                if(block.id in types):
                    count +=1
                    visited.append(new_loc)
        
                
        i += 1
    return visited


def prepare_area(editor, X1, Z1, height, areas, floors, corners):
    buildArea = editor.getBuildArea()
    buildRect = buildArea.toRect()
    worldSlice = editor.loadWorldSlice(buildRect)
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    log_types = {}
    print("Preparing block pallet")
    for area in areas:
        for x in range(area.begin.x, area.end.x + ( 1 if area.end.x > area.begin.x else -1), 1 if area.end.x > area.begin.x else -1):
            for z in range(area.begin.y, area.end.y + ( 1 if area.end.y > area.begin.y else -1), 1 if area.end.y > area.begin.y else -1):
                xx = x - X1
                zz = z - Z1
                block = editor.getBlock(ivec3(x,heightmap[xx,zz]-1,z))
                if(block.id in lookup.LOGS):
                    wood_type = block.id.replace('minecraft:','').replace('_log','')
                    if(wood_type in log_types):
                        log_types[wood_type] +=1
                    else:
                        log_types[wood_type] = 1
                
    if(len(log_types) >0):
        wood_type = max(log_types, key=log_types.get)
        block_pallet = BlockPallet(wood_type)
    else:
        block_pallet = BlockPallet()
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING"]
    print("Start removing trees")
    for area in areas:
        for x in range(area.begin.x, area.end.x + ( 1 if area.end.x > area.begin.x else -1), 1 if area.end.x > area.begin.x else -1):
            for z in range(area.begin.y, area.end.y + ( 1 if area.end.y > area.begin.y else -1), 1 if area.end.y > area.begin.y else -1):
                xx = x - X1
                zz = z - Z1
                block = editor.getBlock(ivec3(x,heightmap[xx,zz]-1,z))
                if(block.id in lookup.TREE_BLOCKS):
                    fill_3d(editor,ivec3(x,heightmap[xx,zz]-1,z),lookup.TREE_BLOCKS,diretions = ALL_DIRECTIONS_NO_DIAGS,restricted=True,remove=True)
    print("End removing trees")            
    worldSlice = editor.loadWorldSlice(buildRect)
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    print("Start prepering area")
    for area in areas:
        for x in range(area.begin.x, area.end.x + ( 1 if area.end.x > area.begin.x else -1), 1 if area.end.x > area.begin.x else -1):
            for z in range(area.begin.y, area.end.y + ( 1 if area.end.y > area.begin.y else -1), 1 if area.end.y > area.begin.y else -1):
                xx = x - X1
                zz = z - Z1
                if(heightmap[xx,zz] >= height):
                    block = editor.getBlock(ivec3(x,heightmap[xx,zz]-1,z))
                    if(block.id != 'minecraft:air'):    
                        geometry.placeCuboid(
                            editor,
                            ivec3(x,height,z),
                            ivec3(x,heightmap[xx,zz]-1,z),
                            Block("air")
                        )
                        editor.placeBlock(ivec3(x,height-1,z),block)

    
    worldSlice = editor.loadWorldSlice(buildRect)
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    for area in areas:
        for x in range(area.begin.x, area.end.x + ( 1 if area.end.x > area.begin.x else -1), 1 if area.end.x > area.begin.x else -1):
            for z in range(area.begin.y, area.end.y + ( 1 if area.end.y > area.begin.y else -1), 1 if area.end.y > area.begin.y else -1):
                xx = x - X1
                zz = z - Z1
                if(heightmap[xx,zz] == height):
                    ok = False
                    for dir in DIRECTIONS_2D:
                        if(heightmap[xx + dir.x, zz + dir.y] > height +1):
                            ok = True
                            break
                    
                    if(ok):
                        block = editor.getBlock(ivec3(x,height-1,z))
                        editor.placeBlock(ivec3(x,height,z), block)

    worldSlice = editor.loadWorldSlice(buildRect)
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    for area in floors:
        for x in range(area.begin.x, area.end.x + ( 1 if area.end.x > area.begin.x else -1), 1 if area.end.x > area.begin.x else -1):
            for z in range(area.begin.y, area.end.y + ( 1 if area.end.y > area.begin.y else -1), 1 if area.end.y > area.begin.y else -1):
                xx = x - X1
                zz = z - Z1
                

                if(heightmap[xx,zz] < height):
                    depth = heightmap[xx,zz]
                    for dir in DIRECTIONS_2D:
                        if(xx+dir.x >= 0 and xx+dir.x <= len(heightmap) and zz+dir.y >= 0 and zz+dir.y <= len(heightmap) and heightmap[xx+dir.x,zz+dir.y] < depth):
                            depth = heightmap[xx+dir.x,zz+dir.y]
                    if(ivec2(x,z) in corners):
                        geometry.placeCuboid(editor,ivec3(x,depth,z),ivec3(x,height-1,z), block_pallet.corner_block)
                    else:
                        geometry.placeCuboid(editor,ivec3(x,depth,z),ivec3(x,height-1,z), block_pallet.floor_block)
    print("End prepering area")
    return block_pallet
       


def verify(editor,areas,area_percent):
    print("Start validating location")
    buildArea = editor.getBuildArea()
    buildRect = buildArea.toRect()
    worldSlice = editor.loadWorldSlice(buildRect)
    heightmap_noleaves = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING"]
    ocenfloor = worldSlice.heightmaps["OCEAN_FLOOR"]
    X1,Z1 = buildRect.begin
    X2,Z2 = buildRect.end

    area_heights = {}
    for area in areas:
        for x in range(area.begin.x, area.end.x + ( 1 if area.end.x > area.begin.x else -1), 1 if area.end.x > area.begin.x else -1):
            for z in range(area.begin.y, area.end.y + ( 1 if area.end.y > area.begin.y else -1), 1 if area.end.y > area.begin.y else -1):
                if(not buildRect.contains(ivec2(x,z))):
                    return False,0
                xx = x - X1
                zz = z - Z1
                
                
                if(heightmap[xx,zz] != ocenfloor[xx,zz]):
                    print("Invalid location, there is a body of water/lava in the area")
                    return False,0
                
                height = heightmap_noleaves[xx,zz]-1
                while(editor.getBlock(ivec3(x,height,z)).id in lookup.TREE_BLOCKS or (editor.getBlock(ivec3(x,height,z)).id == "minecraft:air")):
                    height -= 1
                height += 1

                if(height not in area_heights):
                    area_heights[height] = 1
                else:
                    area_heights[height] += 1
                # editor.placeBlock(ivec3(x,height,z), Block("red_concrete"))
    
    most_used_high = max(area_heights, key=area_heights.get)
    
    count = area_heights[most_used_high]
    s = 0
    for height in list(area_heights.values()):
        s += height
    
    if(count/s < area_percent):
        print("Invalid location, no main height")
        return False, 0
    
    for height in list(area_heights.keys()):
        if(np.abs(height - most_used_high) >4):
            print("Invalid location, to much variance of the height")
            return False, 0 


    print("Valid location")
    return True, most_used_high

def generate_house(number_of_tries):
    editor = Editor()
    buildArea = editor.getBuildArea()
    buildRect = buildArea.toRect()
    worldSlice = editor.loadWorldSlice(buildRect)
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    # for point in buildRect.outline:
    #     height = heightmap[tuple(point - buildRect.offset)]

    #     for y in range(height-1, height):
    #         editor.placeBlock(addY(point, y), Block("air"))

    X1,Z1 = buildRect.begin
    X2,Z2 = buildRect.end

    for _ in range(number_of_tries):
        print("try {}-th position".format(_))
        x = np.random.randint(X1,X2+1)
        z = np.random.randint(Z1,Z2+1)
        house = House.create_house(x,z)
    
        valid_building,height = verify(editor,house.areas,0.1)
        if(valid_building):
            block_pallet = prepare_area(editor,X1, Z1, height,house.areas, house.floors, house.corners)    
            house.construct(editor,height-1,block_pallet)
            window_probability = 0.5
            house.add_doors_windows(editor,window_probability)      
            trash_probability = 0.2
            house.create_attic(editor,trash_probability)
            house.populate_inside(editor,4)
            print("Done!")
            break





if __name__ == '__main__':
    try:
        for _ in range(1):
            generate_house(100)    
       
        

    except KeyboardInterrupt: # useful for aborting a run-away program
        print("Pressed Ctrl-C to kill program.")