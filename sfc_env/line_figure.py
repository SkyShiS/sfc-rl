import numpy as np
import matplotlib.pyplot as plt


def demo():
    x1 = [20, 33, 51, 79, 101, 121, 132, 145, 162, 182, 203, 219, 232, 243, 256, 270, 287, 310, 325]
    y1 = [49, 48, 48, 48, 48, 87, 106, 123, 155, 191, 233, 261, 278, 284, 297, 307, 341, 319, 341]
    x2 = [31, 52, 73, 92, 101, 112, 126, 140, 153, 175, 186, 196, 215, 230, 240, 270, 288, 300]
    y2 = [48, 48, 48, 48, 49, 89, 162, 237, 302, 378, 443, 472, 522, 597, 628, 661, 690, 702]
    x3 = [30, 50, 70, 90, 105, 114, 128, 137, 147, 159, 170, 180, 190, 200, 210, 230, 243, 259, 284, 297, 311]
    y3 = [48, 48, 48, 48, 66, 173, 351, 472, 586, 712, 804, 899, 994, 1094, 1198, 1360, 1458, 1578, 1734, 1797, 1892]
    l1 = plt.plot(x1, y1, 'r-', label='type1')
    l2 = plt.plot(x2, y2, 'g-', label='type2')
    l3 = plt.plot(x3, y3, 'b-', label='type3')
    # plt.plot(x1, y1, 'ro-', x2, y2, 'g+-', x3, y3, 'b^-')
    plt.title('The Lasers in Three Conditions')
    plt.xlabel('row')
    plt.ylabel('column')
    plt.legend()
    plt.show()


def plot_line_figure(name, y):
    y1, y2, y3, y4 = y[0], y[1], y[2], y[3]
    plt.plot(range(len(y1)), y1, 'r-', label='A')
    plt.plot(range(len(y2)), y2, 'g-', label='B')
    plt.plot(range(len(y3)), y4, 'b-', label='C')
    plt.plot(range(len(y4)), y4, 'y-', label='D')
    plt.title(name)
    plt.ylabel('epoch')
    plt.legend()
    plt.show()
