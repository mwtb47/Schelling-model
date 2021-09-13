"""Script to run a simulation of the Schelling model.

This script contains a class with methods to simulate and visualise
a version of Thomas Schelling's model of segregation with user specified
parameters. The following files are saved:
    - a GIF file with an animation of the simulation.
    - png files with plots of the initial and final distributions of the
      simulation.
    - a png file with a plot showing the development of the mean 
      similarity ratio and proportion of satisfied occupants.
"""

from copy import deepcopy
from itertools import cycle, islice, product
import random

from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.pyplot as plt
import numpy as np


class Schelling:
    """Class with methods to simulate and visualise segregation model.
    
    Attributes:
        width (int): Width of the city grid.
        height (int): Height of the city grid.
        empty_ratio (float): Set ratio of empty to populated grid 
            squares.
        similarity_threshold (float): An house occupant will only be 
            satisfied if at least this proportion of their neighbours 
            are of the same race as them.
        update_limit (int): An update occurs when an house occupant
            moves house. With some specifications of the model, it is 
            not possible to make all occupants satisfied, therefore a 
            limit is placed on the number of updates to prevent it 
            running indefinitely.
        races (int): Number of races.
    """
    
    def __init__(self, width, height, empty_ratio, similarity_threshold, 
                 update_limit, races) :
        self.width = width
        self.height = height
        self.empty_ratio = empty_ratio
        self.similarity_threshold = similarity_threshold
        self.update_limit = update_limit
        self.races = races
        self.animation_frames = []
        self.colours = {0: "royalblue", 1: "orange", 2: "tomato", 3: "green",
                        4: "blueviolet", 5: "skyblue", 6: "darkslategrey", 
                        7: "pink"}
        
    def populate(self):
        """Randomly populates the city grid with the required number of 
        houses and assigns a race to each occupant.
        
        Returns:
            A dictionary where the keys are the coordinates for the 
            houses and the values represent the race of the occupant.
            e.g.:
            {(1,1): 0, (4,5): 1, (3,6): 0}
        """
        self.grid_squares = list(product(range(self.width), range(self.height)))
        random.shuffle(self.grid_squares)
        n_houses = int(len(self.grid_squares) * (1 - self.empty_ratio))
        houses = self.grid_squares[:n_houses]
        races = list(islice(cycle(range(self.races)), n_houses))
        city = dict(zip(houses, races))
        
        # Add the initial distribution to the animation frame list.
        self.animation_frames.append(deepcopy(city))
        
        return city
    
    def get_neighbours(self, house):
        """Neighbours are defined as those grid squares one step in any 
        direction, including diagonally, from the house. Most houses 
        therefore have eight neighbouring grid squares, however houses 
        at the edge of the city grid will have fewer.
        
        Args:
            house: The coordinates of the house for which a list of 
                neighbours is to be returned.
        
        Returns:
            A list of coordinates for neighbouring grid squares.
        """
        x,y = house
        surrounding = product([x - 1, x, x + 1], [y - 1, y, y + 1])
        neighbours = [i for i in surrounding if i in self.grid_squares]
        neighbours.remove((x,y))
        return neighbours
    
    def is_satisfied(self, city, house):
        """Determine whether an occupant of a house is satisfied with 
        their neighbours. An occupant is satisfied if the ratio of 
        neighbours of the same race to neighbours of a different race is
        greater than or equal to their similarity threshold.
            
        Args:
            city: Dictionary containing all currently occupied houses.
            house: The location of occupant to check satisfied status 
                of.
        
        Returns:
            True if the occupant is satisfied, False if unsatisfied.
        """
        occupant_race = city[house]
        neighbours = self.get_neighbours(house)
        
        same_race = sum(1 for i in neighbours 
                        if i in city and city[i] == occupant_race)
        other_race = sum(1 for i in neighbours 
                         if i in city and city[i] != occupant_race)
        
        # Avoid division by 0. In this case an occupant with no 
        # neighbours is considered satisfied. 
        if same_race + other_race == 0:
            return True
        
        if same_race / (same_race + other_race) < self.similarity_threshold:
            return False
        else :
            return True
        
    def all_satisfied(self, city):
        """
        Args:
            city: Dictionary containing all currently occupied houses.
        
        Returns:
            True if all city inhabitants are satisfied.
        """
        return all(self.is_satisfied(city, house) for house in city)
    
    def update(self, city, house):
        """Move an unsatisfied occupant to a randomly selected
        unoccupied house. The updated city dictionary is added to
        the list of animation frames.
        
        Note: In this setup, an occupant could move to a location they
            are unsatisfied with. The way they move could be set up to 
            avoid this. It could also include other rules such as moving
            to the nearest location.
        
        Args:
            city: Dictionary containing all currently occupied houses.
            house: The location of the occupant to update location of.
        
        Returns:
            Updated dictionary containing all occupied houses.
        """
        empty_house = random.choice(
            [square for square in self.grid_squares if square not in city])
        city[empty_house] = city[house]
        del city[house]
        self.animation_frames.append(deepcopy(city))
        return city
    
    def run(self):
        """Run the model simulation. Call the populate function and then
        run the update function until either all inhabitants are 
        satisfied or the update limit has been reached.
        """
        update_count = 0
        city = self.populate()
        
        while not self.all_satisfied(city) and update_count < self.update_limit:
            occupied_houses = list(city)
            random.shuffle(occupied_houses)
            for house in occupied_houses:
                if not self.is_satisfied(city, house):
                    city = self.update(city, house)
                    update_count += 1
                    break
        
        self.total_updates = len(self.animation_frames) - 1
        
    def mean_similarity(self, city):
        """Calculate the mean similarity ratio of occupants in a given 
        frame of the simulation.
        
        Args:
            city: Dictionary containing all currently occupied houses.

        Returns:
            Mean similarity ratio, rounded to 2 decimal places.
        """
        results = []
        for house in city:
            neighbours = self.get_neighbours(house)

            same_race = sum(1 for i in neighbours 
                            if i in city and city[i] == city[house])
            other_race = sum(1 for i in neighbours 
                             if i in city and city[i] != city[house])

            # If a similarity ratio cannot be calculated, nothing is 
            # appended. Undecided if this is the best.
            if same_race + other_race == 0:
                pass
            else:
                results.append(same_race / (same_race + other_race))

        return round(np.mean(results), 2)
        
    def plot_initial_final(self, filename_label):
        """Save two png files, one conatining the intial distribution of
        inhabitants, the second containing the distribution once the 
        simulation has ended.
        
        Args:
            filename_label: The two png files are saved as 
                'Schelling_initial_{label}.png' and 
                'Schelling_final_{label}.png'.
        """
        frames = [self.animation_frames[0], self.animation_frames[-1]]
        titles = ["Initial Distribution", "Final Distribution"]
        filenames = ["Schelling_initial_{}.png", "Schelling_final_{}.png"]
        
        initial_mean_similarity = self.mean_similarity(frames[0])
        final_mean_similarity = self.mean_similarity(frames[1])
        
        y_coordinates = [.75, .7, .65, .6, .55, .5, .4, .35, .3]
        annotation_texts = [
            "Width - {}".format(self.width),
            "Height - {}".format(self.height),
            "Empty ratio - {}".format(self.empty_ratio),
            "Similarity threshold - {}".format(self.similarity_threshold),
            "Update limit - {}".format(self.update_limit), 
            "Races - {}".format(self.races), 
            "Total updates - {}".format(self.total_updates),
            "Initial mean similarity - {}".format(initial_mean_similarity),
            "Final mean similarity - {}".format(final_mean_similarity),
        ]
        
        for frame, title, filename in zip(frames, titles, filenames):
            x = [x + 0.5 for x,y in frame]
            y = [y + 0.5 for x,y in frame]
            colour_list = [self.colours[frame[i]] for i in frame]
            
            fig = plt.figure(figsize=(15 * self.width / self.height * 1.5, 15))
            plt.axes(xlim=(0, self.width), ylim=(0, self.height))
            plt.xticks([])
            plt.yticks([])
            plt.subplots_adjust(right=0.66)
            
            for yc, anno_text in zip(y_coordinates, annotation_texts):
                plt.text(
                    x=self.width * 1.1, 
                    y=self.height * yc, 
                    s=anno_text, 
                    font=dict(size=30)
                )
            
            plt.text(
                x=0,
                y=self.height + 0.5,
                s=title,
                font=dict(size=40),
                horizontalalignment="left",
            )
        
            # Not sure why this is needed by text is pixelated without 
            # it.
            fig.patch.set_facecolor('white')

            plt.scatter(
                x, y, 
                s=min((0.5 * 15 * 72 / self.width) ** 2, 
                      (0.5 * 15 * 72 / self.height) ** 2), 
                marker='s',
                c=colour_list
            )
            
            plt.savefig(filename.format(filename_label), dpi=72)
            plt.close()
            
    def create_GIF(self, filename_label):
        """Save a GIF to illustrate the simulation. Each frame shows the
        result of one unsatisfied house occupant moving.
        
        Args:
            filename_label: The GIF file is saved as 
                'Schelling_{label}.gif'.
        """
        x = [x for x,y in self.grid_squares]
        y = [y for x,y in self.grid_squares]

        positions = [[(x + 0.5, y + 0.5) for x,y in frame] 
                     for frame in self.animation_frames]
        colour_list = [[self.colours[frame[i]] for i in frame] 
                       for frame in self.animation_frames]
        
        initial_mean_similarity = self.mean_similarity(self.animation_frames[0])
        final_mean_similarity = self.mean_similarity(self.animation_frames[-1])

        # Title text for each frame of the animation.
        text = ["Update {} of {}".format(i, self.total_updates) 
                for i in range(self.total_updates + 1)]

        # Annotations displayed to the right of the plot. Coordinates 
        # are proportion of the y-axis range, i.e. 0.75 plots 75% of the
        # way up the y-axis.
        y_coordinates = [0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.4, 0.35, 0.3]
        annotation_texts = [
            "Width - {}".format(self.width),
            "Height - {}".format(self.height),
            "Empty ratio - {}".format(self.empty_ratio),
            "Similarity threshold - {}".format(self.similarity_threshold),
            "Update limit - {}".format(self.update_limit), 
            "Races - {}".format(self.races), 
            "Total updates - {}".format(self.total_updates),
            "Initial mean similarity - {}".format(initial_mean_similarity),
            "Final mean similarity - {}".format(final_mean_similarity),
        ]
        
        fig = plt.figure(figsize=(15 * self.width / self.height * 1.5, 15))
        plt.axes(xlim=(0, self.width), ylim=(0, self.height))
        
        # Hide axis ticks.
        plt.xticks([])
        plt.yticks([])
        
        # Reserve 33% of the plot on the right for annotations.
        plt.subplots_adjust(right=0.66)
        
        # Not sure why this is needed by text is pixelated without it.
        fig.patch.set_facecolor('white')
        
        for yc, anno_text in zip(y_coordinates, annotation_texts):
            plt.text(
                x=self.width * 1.1, 
                y=self.height * yc, 
                s=anno_text, 
                font=dict(size=30)
            )

        title_text = plt.text(
            x=0,
            y=self.height + 0.5,
            s=text[0],
            font=dict(size=40),
            horizontalalignment="left",
        )

        scat = plt.scatter(
            x, y, 
            s=min((0.5 * 15 * 72 / self.width) ** 2, 
                  (0.5 * 15 * 72 / self.height) ** 2), 
            marker='s',
        )

        def animate(frame, data, points, text, scat):
            """Set the position and colours of the house occupants in 
            a given frame.
            """
            scat.set_offsets(points[frame])
            scat.set_color(data[frame])
            title_text.set_text(text[frame])
            return scat,

        anim = FuncAnimation(
            fig, 
            animate,
            frames=self.total_updates + 1, 
            interval=40,
            fargs=(colour_list, positions, text, scat),
            blit=True,
        )
        anim.save(
            "Schelling_{}.gif".format(filename_label),
            writer='pillow', 
            dpi=72
        )
        plt.close()
        
    def plot_mean_similarity(self, filename_label):
        """Save a png with a two plots showing the development of the 
        mean similarity ratio and the proportion of satisfied occupants 
        after each update during the simulation.
        
        Args:
            filename_label: The png file is saved as 
                'Schelling_mean_similarity_{label}.png'.
        """
        n_occupants = len(self.animation_frames[0])
        mean_similarity = [self.mean_similarity(frame) 
                           for frame in self.animation_frames]
        percent_satisfied = [sum(self.is_satisfied(frame, house) 
                                 for house in frame) / n_occupants 
                             for frame in self.animation_frames]
        
        fig = plt.figure(figsize=(10,6))
        
        subplot_1 = plt.subplot(1,2,1)
        plt.title("Mean Similarity Ratio After Each Update")
        plt.plot(
            range(len(self.animation_frames)),
            mean_similarity,
            c='royalblue',
        )
        plt.axhline(
            self.similarity_threshold, 
            color='grey', 
            linestyle='--'
        )
        plt.text(
            s="Similarity Threshold",
            x=self.total_updates * 0.6, 
            y=self.similarity_threshold + 0.01,
        )
        plt.xlabel("Update Number")
        
        plt.subplot(1,2,2, sharey=subplot_1)
        plt.title("Proportion of Satisfied Occupants\nAfter Each Update")
        plt.plot(
            range(len(self.animation_frames)),
            percent_satisfied,
            c='tomato',
        )
        plt.xlabel("Update Number")
        
        plt.savefig(
            "Schelling_mean_similarity_{}.png".format(filename_label), 
            dpi=200
        )
        plt.close()
        

def main():
    """Ask the user to input the model's parameters and the name of the
    GIF animation to be saved. Initiate the Schelling class and run 
    methods to simulate the model, plot the initial and final 
    distribution, and save a GIF animation.
    """
    width = int(input("City width - "))
    height = int(input("City height - "))
    empty_ratio = float(input("Empty ratio - "))
    similarity_threshold = float(input("Similarity threshold - "))
    update_limit = int(input("Update limit - "))
    races = int(input("Races - "))
    filename_label = input("Filename label (Schelling_{label}.gif) - ")
    
    model = Schelling(width, height, empty_ratio, similarity_threshold, 
                      update_limit, races)
    model.run()
    model.plot_initial_final(filename_label)
    model.create_GIF(filename_label)
    model.plot_mean_similarity(filename_label)
    

if __name__ == "__main__":
    main()