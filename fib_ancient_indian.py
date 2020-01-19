from matplotlib import colors
from matplotlib.patches import Rectangle
import matplotlib
from matplotlib import pyplot as plt


def pingala(m, size=2):

    if m < size:
        return [[0] * m]
    elif m == size:
        return [[0] * size, [1] * size]
    else:
        result = []
        seeds = [[0] * size]
        seeds += [[0] * i + [1] * size for i in range(size)]
        for seed in seeds:
            for item in pingala(m - len(seed), size):
                if not len(seed + item) > m:
                    result.append(seed + item)
        return result


def recursive_fib(n):
    if n < 1 or n == 0:
        return 1
    else:
        return recursive_fib(n - 1) + recursive_fib(n - 2)


#print(all([recursive_fib(i) == len(pingala(i+1, size=2)) for i in range(20)]))
#print(pingala(7, 2))
size = 2
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.patches import Rectangle
from matplotlib import colors
results = (pingala(8, size))
results.sort(key=lambda x: (x[-1] == 1, sum(x)))

fig, ax = plt.subplots(nrows=len(results), ncols=1)
# make a color map of fixed colors
cmap = colors.ListedColormap(['yellow', 'green'])
bounds = [0, .5, 1]
norm = colors.BoundaryNorm(bounds, cmap.N)

for idx, result in enumerate(results):
    ax[idx].imshow([result], cmap=cmap, norm=norm)

    for i in range(len(result)):
        ax[idx].add_patch(
            Rectangle((-0.5 + i, -0.5),
                      1,
                      1,
                      fill=0,
                      edgecolor='grey',
                      linewidth=1))

    count = 0
    while count < len(result):
        if result[count] == 1:
            ax[idx].add_patch(
                Rectangle((count - 0.5, -0.5),
                          size,
                          1,
                          fill=0,
                          edgecolor='red',
                          linewidth=2))
            count += size
        else:
            count += 1

    ax[idx].axis('off')
plt.show()
import os
for result in results:
    print(result)
    for note in result:
        if note==0:
           os.system('play -nq -t alsa synth 0.3 sin 420')
        elif note==1:
           os.system('play -nq -t alsa synth 0.6 sin 420')
