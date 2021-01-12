import matplotlib.pyplot as plt
import random
  
# method_list = ('game theory', 'genetic optimize', 'annealing optimize')
def draw_pic(x_vec, y_vec, x_label='', y_label='', title=''):
    i = random.randint(0,100)
    file_name = 'attribute0' + str(i) + '.png'
    plt.plot(x_vec['game theory'], y_vec['game theory'], 'b-o', 
             x_vec['genetic optimize'], y_vec['genetic optimize'], 'r-s',
             x_vec['annealing optimize'], y_vec['annealing optimize'], 'g-^',
             x_vec['collaborative filter'], y_vec['collaborative filter'], 'b--')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig(file_name)
    plt.close()
