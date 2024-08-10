This file will explain the porpose of each file(-)/folder(+).
It should be noted that some of the files were overwritten or deprecated over time, and these are be kept as artifacts, and for referencing.

 + corpus
	Folder containing the Maltese corpus text files
 + gabra
	Folder containing the Maltese gabra in 
 - gameTesting.py
	(1st) The initial sample testing was done on this script
 - strategies.py
	(2nd) Calculating more strategies
 - entropy_vs_get_best_freq.py
	(3rd) Calculating both the entropy and frequency trees
 - rl_test.py
	(4th) Script attempting reinforcement learning on wordle
 - get_stats.py
	(5.1) Final script used to calculate different strategies with different weights
 - learning_parameters.py
	(5.2) A variationg to get_stats.py, which saves results to a csv file
 - rl_parameters.py
	(5.3) Parameter tuning with Bayesian Optimization
 - get_all_words.py
	Extracts all the words from the corpus (and maltese dictionary)
 - wordle.py
	Main wordle game used throughout most of the scripts
 - game_utils.py
	pygame utilities for visualisations
 - utility.py
	Main utility function used throughout all the scripts
 - server_run.py
	Python file ran on the laptop server (30hrs fail)

 + extra
	Some more scripts which were used, but not mentioned, or which did not contribute a lot to the solver.
 + parameter logs
	Files that log the parameter tweaking for the final solver.

Created Files from program:
 - frequency.json
 - frequency.pkl
 - tree_parameters.csv
