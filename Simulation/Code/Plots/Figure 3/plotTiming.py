import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("rankingAnalysis.csv", header=0)
df['Dataset'] = df['Dataset'].str.replace('a=', 'α=')

# Plotting
plt.figure(figsize=(8, 6))

# Vertical lines
plt.axvline(x=600, color='black', alpha=0.35, linestyle='--', linewidth=2)
#plt.axvline(x=400, color='black', alpha=0.35, linestyle='--', linewidth=2)

# Define markers for Optimized Elo and Dual-K Elo
markers = {'200': 'o',
           '400': '^',
           '600': 'D',
           '800': "$G$"}
labelText = {'200': 't=200',
             '400': 't=400',
             '600': 't=600',
             '800': 'Gradual change'}
colors = ['#FC766AFF', '#5B84B1FF']
markerSize = 30

labels = []
for idx, row in df.iterrows():
    yCoord = 20 - row['Dataset ID']
    if row['Event'] in [600, 800]:
        labelOpt = labelText[str(row['Event'])] + ' (Optimized Elo)'
        labelDual = labelText[str(row['Event'])] + ' (Dual-K Elo)'
        if row['Optimized Elo'] != row['Dual-K Elo']:
            if labelOpt not in labels:
                plt.scatter(row['Optimized Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            color=colors[0],
                            label=labelOpt)
                labels.append(labelOpt)
            else:
                plt.scatter(row['Optimized Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            color=colors[0])
        else:
            if labelOpt not in labels:
                plt.scatter(row['Optimized Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            edgecolors=colors[0],
                            facecolors='none',
                            label=labelOpt)
                labels.append(labelOpt)
            else:
                plt.scatter(row['Optimized Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            edgecolors=colors[0],
                            facecolors='none')
        if row['Optimized Elo'] != row['Dual-K Elo']:
            if labelDual not in labels:
                plt.scatter(row['Dual-K Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            color=colors[1],
                            label=labelDual)
                labels.append(labelDual)
            else:
                plt.scatter(row['Dual-K Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            color=colors[1])
        else:
            if labelDual not in labels:
                plt.scatter(row['Dual-K Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            edgecolors='none',
                            facecolors=colors[1],
                            label=labelDual)
                labels.append(labelDual)
            else:
                plt.scatter(row['Dual-K Elo'],
                            yCoord,
                            marker=markers[str(row['Event'])],
                            s=markerSize,
                            edgecolors='none',
                            facecolors=colors[1])

# Set Y-axis ticks and labels
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_linewidth(2.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_yticks(range(len(df['Dataset'].unique())))
ax.set_yticklabels(df['Dataset'].unique()[::-1])

# Axis ticks format
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_fontsize(12)
    tick.set_fontweight('bold')

# Set labels and title
plt.xlabel('Time (t)', fontsize=14, fontweight='bold', labelpad=10, x=0.90)
#plt.ylabel('Simulation Data', fontsize=14, fontweight='bold')

# Set X-axis range
ax.set_xlim(-30, 800) #140, 620

# Add legend
handles, labels = plt.gca().get_legend_handles_labels()
new_order = [handles[0], handles[2], handles[1], handles[3]]
new_labels = [labels[0], labels[2], labels[1], labels[3]]
plt.legend(new_order, new_labels, loc='center left', bbox_to_anchor=(1.001, 0.5), borderaxespad=0., ncol=1, frameon=False)

# Display the plot
plt.tight_layout()
plt.savefig('changePlot2Legend.pdf', format='pdf', dpi=300, bbox_inches='tight')
plt.show()
