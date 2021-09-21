# Schelling model

I have also added a csv containing the results from simulations with different combinations of similarity threshold and number of races. 1,000 simulations are run for each combination of the following:
- similarity_threshold: {0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1}
- races: {2, 3, 4, 5}

Parameters consistent across simulations:
- width, height: 15x15
- empty_ratio: 0.2
- update_limit: 50,000

The four columns are:
- similarity_threshold
- races
- updates: total number of updates until all occupants are satisfied or the update limit is reached.
- mean_similarity: mean occupant similarity ratio after the last update.

Note that some of the setups with higher similarity thresholds and number of races reach the update limit. Some of these setups do have at least one 'solution', it is just not reached within the update limit.
