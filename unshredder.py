from PIL import Image
from math import sqrt 

# Some structure
class Slice:
    """ A vertical slice of image from (start, 0) to (end, height)"""
    next = None
    prev = None
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
# Get single pixel as rgba		
def get_pixel(x, y):
    return data[y * width + x]

# Eucledian distance of two points	
def distance(p1, p2):
    ss = 0
    for pp1, pp2 in zip(p1,p2):
        ss += (pp1 - pp2)**2
    return sqrt(ss)

# Distance of two columns of pixels	
def slice_distance(x1, x2):
    d = 0
    for y in range(height):
        d += distance(get_pixel(x1,y), get_pixel(x2,y))
    return d

# Find a slice that is best match for given slices end	
def find_next(a_slice):
    best_slice = None
    min_distance = 100000
    for slice in slices:
        distance = slice_distance(a_slice.end, slice.start)
        if distance < min_distance and slice != a_slice:
            best_slice = slice
            min_distance = distance
    return best_slice			

# Find a slice that is best match for given slices start
def find_prev(a_slice):
    best_slice = None
    min_distance = 100000
    for slice in slices:
        distance = slice_distance(a_slice.start, slice.end)
        if distance < min_distance and slice != a_slice:
            best_slice = slice
            min_distance = distance
    return best_slice	

# Find the slice width that correlates with high distances
def find_slice_width():
    rBest = 0
    wBest = 0
    dm = []
    for x in range(0,width-1):
        dm.append((x,slice_distance(x,x+1)))
    dm = sorted(dm, key=lambda d: d[1], reverse=True)
    for w in range(2,100):
        m = width / w
        p = 0
        for i in range(0, m):
            index = dm[i][0] + 1
            if index % w == 0:
                p=p+1
        r = float(p) / m
        if r > rBest:
            rBest = r
            wBest = w
    return wBest                    

# Load our image and slice it!
image = Image.open('TokyoPanoramaShredded.png')
slice_count = 20
width, height = image.size
data = image.getdata() # This gets pixel data	
slice_width = find_slice_width()

print "Using slice width ",slice_width," to unshred"

slices = []

# We know the borders for now 
left_borders = range(0,width,slice_width)
right_borders = range(slice_width-1,width,slice_width)

for left,right in zip(left_borders, right_borders):
    slices.append(Slice(left,right))
    
# Start finding best matches for the slices
first = None
last = None
for slice in slices:
    next = find_next(slice)
    next_prev = find_prev(next)
    if next_prev == slice:
        slice.next = next		
    else:
        last = slice
    prev = find_prev(slice)
    prev_next = find_next(prev)
    if prev_next == slice:
        slice.prev = prev
    else:
        first = slice
            
# Create a new image of the same size as the original
# and copy a region into the new image
unshredded = Image.new('RGBA', image.size)
curr = first
print "Writing image - first index:",first.start,", last index:",last.end
i = 0
while curr != None:
    x1, y1 = curr.start, 0
    x2, y2 = curr.end+1, height
    source_region = image.crop([x1, y1, x2, y2])
    destination_point = (i*32, 0)
    unshredded.paste(source_region, destination_point)	
    curr = curr.next
    i = i+1
# Output the new image
unshredded.save('unshredded.jpg', 'JPEG')	