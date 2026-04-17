import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import seaborn as sns


def plot_percentage_of_delayed_flights_per_airline(delay_per_airline : dict):
    airlines = list(delay_per_airline.keys())
    delays = list(delay_per_airline.values())
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(airlines,delays)
    ax.set_title("Delay per airline per flight")
    ax.set_xlabel("Airline")
    ax.set_ylabel("Percentage delayed flights")
    ax.set_ylim(0, max(delays) + 5)
    plt.xticks(rotation=45, ha='right',fontsize=10)
    plt.tight_layout()  # make sure they fit
    plt.show()
    return(fig)


def plot_percentage_of_delayed_flight_per_hour(hours,percentages : list):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(hours, percentages)
    ax.set_title("% of delay per hour per day")
    ax.set_xlabel("hours")
    ax.set_ylabel("Percentage delayed flights")
    ax.set_ylim(0, max(percentages) + 5)
    # plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()  # make sure they fit
    plt.show()
    return (fig)

def plot_heatmap_routes(heat_map):
    #   The following code is based upon the use of Seaborn heatmaps, see also the following
    #   excellent Video:
    #   https://www.youtube.com/watch?v=u7ESlujjoBc

    # set the canvas size, return the image to fig
    fig, axs = plt.subplots(figsize=(40, 40))

    # Create the heatmap
    ax=sns.heatmap(heat_map, cmap = 'Blues',  annot = True, annot_kws= {'size' : 10}, cbar=False, linewidths=1, linecolor='white')

    # Set the label for X=axis and Y-axis and the ticklables
    ax.set_xlabel('Origin')
    ax.set_ylabel('Destination')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha='right', fontsize=30)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, ha='right', fontsize=30)

    # Add padding to the X-axis & Y-axis lables

    ax.set_xlabel('Origin', labelpad=10, rotation=0, ha='right', fontsize=80)
    ax.set_ylabel('Destination', labelpad=10, rotation=90, ha='right', fontsize=80)

    # Rotate x-axis and y-axis labels to be horizontal
    # ax.xaxis.set_label_coords((0, 100))




    plt.show()
    fig.savefig("Heat map routes.png")
    return(fig)

def main():
    print("testing plot_heatmap_routes")
    print("========================================")
    my_list=[[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
              [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
              [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
              [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
              [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
              [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
              [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]]
    iatac_1=["cucumber", "tomato", "lettuce", "asparagus", "potato", "wheat", "barley"]
    iatac_2=["Farmer Joe", "Upland Bros.", "Smith Gardening", "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

    # fig=plot_heatmap_routes(my_list,iatac_1,iatac_2)
    plot_heatmap_routes(my_list)
if __name__ == "__main__":
    main()