COLORS = ["R", "G", "B", "Y"]

WHITE_CARDS_AMOUNT = [18 * 2, 12 * 3, 9 * 4]

BLUE_CARDS_AMOUNT = [7 * 2, 4 * 3, 3 * 4]

MOVEMENT_CARDS_AMOUNT = [24, 16, 12]


WHITE_CARDS = [f"fig{str(i).zfill(2)}" for i in range(1, 19)]
BLUE_CARDS = [f"fige{str(i).zfill(2)}" for i in range(1, 8)]


MOVEMENT_CARDS = [f"mov{str(i).zfill(2)}" for i in range(1, 8)]

MOVEMENT_CARDS_NAMES = {
    "mov01": "Diagonal dos casillas",
    "mov02": "Linea recta dos casillas",
    "mov03": "Linea recta una casilla",
    "mov04": "Diagonal una casilla",
    "mov05": "L invertida",
    "mov06": "L",
    "mov07": "Linea recta hasta el borde",
}

FIGURE_CARDS_NAMES = {
    "fig01": "T alargada",
    "fig02": "Z alargada",
    "fig03": "Z alargada invertida",
    "fig04": "Escalera",
    "fig05": "Linea de 5",
    "fig06": "Esquina",
    "fig07": "L invertida de cuatro casillas",
    "fig08": "L de cuatro casillas",
    "fig09": "T con casilla extra derecha",
    "fig10": "S invertida",
    "fig11": "T con casilla extra izquierda",
    "fig12": "S",
    "fig13": "L invertida de tres casillas con casilla extra abajo",
    "fig14": "L de tres casillas con casilla extra abajo",
    "fig15": "Cuadrado con casilla extra izquierda",
    "fig16": "C",
    "fig17": "Cruz",
    "fig18": "Cuadrado con casilla extra derecha",
    "fige01": "Z invertida",
    "fige02": "Cuadrado",
    "fige03": "Z",
    "fige04": "T",
    "fige05": "L invertida de tres casillas",
    "fige06": "Linea de 4",
    "fige07": "L de tres casillas",
}


FIGURE_CARDS_FORM = {
    "fig01": [[1, 0, 0], [1, 1, 1], [1, 0, 0]],
    "fig02": [[1, 1, 0, 0], [0, 1, 1, 1]],
    "fig03": [[0, 0, 1, 1], [1, 1, 1, 0]],
    "fig04": [[1, 0, 0], [1, 1, 0], [0, 1, 1]],
    "fig05": [[1, 1, 1, 1, 1]],
    "fig06": [[1, 0, 0], [1, 0, 0], [1, 1, 1]],
    "fig07": [[1, 1, 1, 1], [0, 0, 0, 1]],
    "fig08": [[0, 0, 0, 1], [1, 1, 1, 1]],
    "fig09": [[0, 0, 1], [1, 1, 1], [0, 1, 0]],
    "fig10": [[0, 0, 1], [1, 1, 1], [1, 0, 0]],
    "fig11": [[1, 0, 0], [1, 1, 1], [0, 1, 0]],
    "fig12": [[1, 0, 0], [1, 1, 1], [0, 0, 1]],
    "fig13": [[1, 1, 1, 1], [0, 0, 1, 0]],
    "fig14": [[0, 0, 1, 0], [1, 1, 1, 1]],
    "fig15": [[0, 1, 1], [1, 1, 1]],
    "fig16": [[1, 0, 1], [1, 1, 1]],
    "fig17": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
    "fig18": [[1, 1, 1], [0, 1, 1]],
    "fige01": [[0, 1, 1], [1, 1, 0]],
    "fige02": [[1, 1], [1, 1]],
    "fige03": [[1, 1, 0], [0, 1, 1]],
    "fige04": [[0, 1, 0], [1, 1, 1]],
    "fige05": [[1, 1, 1], [0, 0, 1]],
    "fige06": [[1, 1, 1, 1]],
    "fige07": [[0, 0, 1], [1, 1, 1]],
}
