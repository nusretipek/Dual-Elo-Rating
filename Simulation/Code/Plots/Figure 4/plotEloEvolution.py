import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

eloSimulationSuddenOpt = np.load("dataFull/eloSimulationSudden.npy")
eloSimulationMixtureOpt = np.load("dataFull/eloSimulationMixture.npy")
eloSimulationSuddenDual = np.load("dataFull/eloSimulationSuddenDual.npy")
eloSimulationMixtureDual = np.load("dataFull/eloSimulationMixtureDual.npy")
eloCam10Opt = np.load("dataFull/Cam_10.npy")
with open("dataFull/dualEloK/Cam_10.txt", "r") as file:
    lines = [line.strip()[1:-1] for line in file]  # Strip brackets
    eloCam10Dual = np.loadtxt(lines, delimiter=',', dtype=np.float64)

index = 5
optEloScores = eloCam10Opt #eloSimulationSuddenOpt[index]
DualKEloScores = eloCam10Dual #eloSimulationSuddenDual[index]

# Plot
plt.figure(figsize=(6, 6))

# Select a timestep
step = 5
timestep = np.arange(0, 832, step)

# Colors and line styles
colors = ['black', 'slategray', 'brown', 'darkorange', 'royalblue', 'darkgreen', 'darkviolet', 'crimson']
line_styles = ['-', '--']

# Plot lines
for i in range(4):
    plt.plot(timestep, optEloScores[timestep, i], color=colors[i], linestyle=line_styles[0])
    plt.plot(timestep, DualKEloScores[timestep, i], color=colors[i], linestyle=line_styles[1])

# Legend
legend_lines = [Line2D([0], [0], color=colors[i], linestyle=line_styles[0], linewidth=2) for i in range(7)]
legend_lines += [Line2D([0], [0], color=colors[i], linestyle=line_styles[1], linewidth=2) for i in range(7)]
legend_labels = [f'Animal {i} (Optimized Elo)' for i in range(7)] + [f'Animal {i} (Dual-K Elo)' for i in range(7)]
#plt.legend(handles=legend_lines, labels=legend_labels, loc='center left', bbox_to_anchor=(1.001, 0.5), borderaxespad=0., ncol=1, frameon=False)

# Remove top and right spines
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Customize x-axis ticks
#highlight_ticks = [2, 4, 6]
ax.set_xticks(np.arange(0, 832, 100))  # Set ticks at intervals
#for i, tick in enumerate(ax.get_xticklabels()):
#    if i in highlight_ticks:
#        tick.set_fontweight('bold')

# Axis ticks format
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_fontsize(12)

# Axis labels
#plt.xlabel('Time (t)', fontsize=14, fontweight='bold', labelpad=10, x=0.90)
#plt.ylabel('Elo Score', fontsize=14, fontweight='bold')

# Title
#plt.title('Evolution of Elo scores (Simulation Data 0.1)', fontsize=18, fontweight='bold', pad=25)

# Show the plot
plt.tight_layout()
plt.savefig('Cam10Plotx.pdf', format='pdf', dpi=300, bbox_inches='tight')
plt.show()
