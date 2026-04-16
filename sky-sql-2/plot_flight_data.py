import matplotlib.pyplot as plt

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


# def plot_percentage_of_delayed_flight_per_hour(hours,percentages : list):








def main():
    pass

if __name__ == "__main__":
    main()