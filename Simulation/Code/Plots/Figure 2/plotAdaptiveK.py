import numpy as np
import matplotlib.pyplot as plt

# Load data
suddenOptimizedEloKValuesArr = np.load('suddenOptimizedEloKValuesArr.npy')
suddenOptimizedAdaptiveEloKValuesArr = np.load('suddenOptimizedAdaptiveEloKValuesArr.npy')
gradualOptimizedEloKValuesArr = np.load('gradualOptimizedEloKValuesArr.npy')
gradualOptimizedAdaptiveEloKValuesArr = np.load('gradualOptimizedAdaptiveEloKValuesArr.npy')

# Plot
x_values = np.arange(1, 801)
x_intervals = np.linspace(1, 801, 8)

# Compute the averages for the arrays
OptimizedEloKValuesArr = np.concatenate((suddenOptimizedEloKValuesArr, gradualOptimizedEloKValuesArr))
OptimizedAdaptiveEloKValuesArr = np.concatenate((suddenOptimizedAdaptiveEloKValuesArr, gradualOptimizedAdaptiveEloKValuesArr))
avg1 = np.mean(OptimizedEloKValuesArr)
OptimizedAdaptiveEloKValuesArrAvg = np.mean(OptimizedAdaptiveEloKValuesArr, axis=0)

plt.figure(figsize=(12, 8))
first_plot = True
for value in OptimizedEloKValuesArr:
    if first_plot:
        plt.axhline(y=value, color='black', linestyle='--', alpha=0.15, label='Time-invariant k')
        first_plot = False
    plt.axhline(y=value, color='black', linestyle='--', alpha=0.15)

first_plot = True
for valueArr in OptimizedAdaptiveEloKValuesArr:
    if first_plot:
        plt.plot(x_intervals, valueArr, color='darkred', linestyle='--', alpha=0.15, label='Time-variant k')
        first_plot = False
    plt.plot(x_intervals, valueArr, color='darkred', linestyle='--', alpha=0.15)

# Plot average lines
plt.axhline(y=avg1, color='black', linestyle='-', linewidth=3, label='Time-invariant k (Mean)')

# Plot new averaged lines
plt.plot(x_intervals, OptimizedAdaptiveEloKValuesArrAvg, color='darkred', linestyle='-', linewidth=3, label='Time-variant k (Mean)')

# Set axis limits
plt.ylim(0, 135)
plt.xlim(0, 800)

# Set y-axis ticks in increments of 10
plt.yticks(np.arange(0, 140, 10))

# Formatting the ticks to be boldface
plt.tick_params(axis='both', which='major', labelsize=8)

# Access the current axis
ax = plt.gca()

# Remove the right and top borders
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Set tick labels to bold
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_fontsize(12)
    tick.set_fontweight('bold')

# Adding labels, title, and legend
plt.xlabel('Time (t)', fontsize=16, fontweight='bold', labelpad=10, x=0.97)
plt.ylabel('k', fontsize=16, fontweight='bold')

# Adding title
plt.title('Estimation of Time-invariant and Adaptive k parameters', fontsize=18, fontweight='bold', pad=25)

# Legend
legend = plt.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.25, 1), prop={'weight': 'bold'})
legend.set_frame_on(False)

# Show the plot
plt.tight_layout()
plt.savefig('timeVariantK.png', dpi=300, bbox_inches='tight')

plt.show()
