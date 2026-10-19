from rectpack import newPacker, PackingMode, PackingBin, SORT_AREA
from rectpack.guillotine import GuillotineBssfSas

def optimize_2d(pieces, stock, kerf=0.0, allow_rotation=True):
    packer = newPacker(
        mode=PackingMode.Offline,
        bin_algo=PackingBin.Global,
        pack_algo=GuillotineBssfSas, # Fuerza cortes de guillotina (lado a lado)
        sort_algo=SORT_AREA,
        rotation=allow_rotation
    )

    # Añadir tableros (stock)
    for width, height, qty in stock:
        qty = 100 if qty is None else qty # Límite práctico de tableros
        for _ in range(qty):
            packer.add_bin(width, height)

    # Añadir piezas a cortar (sumando el kerf)
    for width, height, qty in pieces:
        for _ in range(qty):
            packer.add_rect(width + kerf, height + kerf)

    packer.pack()

    # Extraer y formatear resultados
    bars = []
    total_waste = 0
    total_area_used = 0

    for abin in packer:
        board_area = abin.width * abin.height
        used_area = 0
        rectangles = []
        
        for rect in abin:
            w_real = rect.width - kerf
            h_real = rect.height - kerf
            used_area += (w_real * h_real)
            rectangles.append({
                "x": rect.x,
                "y": rect.y,
                "width": w_real,
                "height": h_real
            })
            
        bars.append({
            "board_width": abin.width,
            "board_height": abin.height,
            "rectangles": rectangles,
            "utilization": round((used_area / board_area) * 100, 2)
        })

    return bars