import matplotlib.pyplot as plt
import numpy as np


def plotAnimalScoreTimeline(self) -> plt.figure:
    # Define colormap
    cmap = plt.cm.jet(np.linspace(0, 1, len(self.animals)))

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8))
    for idx, label in enumerate(self.animals):
        ax.plot(range(self.animalScoresTimeline.shape[0]),
                self.animalScoresTimeline[:, idx],
                marker='o',
                linestyle='-',
                color=cmap[idx],
                label=label)

    ax.set_xlabel('Time (#Interactions)')
    ax.set_ylabel('Scores')
    ax.set_title('Animal Scores Timeline')
    ax.legend()
    plt.grid(True)

    # Return statement
    return fig

## <Checkpoint>
