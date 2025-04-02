# tsp-opt-297

## To use
1. ssh into **any ug machine EXCEPT 135**. `send_recieve.py` interacts with ug135 and it breaks if you also try and run the opt from it.
2. `cd ece297/work/mapper/optimizer/` and `source venv/bin/activate.csh`
3. Run `python3 optimizer.py` on ug xxx
4. Run `python3 bayes_opt.py` on local (order of 3 and 4 is important!)

In `send_recieve.py` (local) and `optimizer.py` (remote), you will have to change the file paths to match those on your account. 
I will make changes soon so that this is easier but for now you have to manually change each file path. 

## Description
### send_recieve.py
Defines very simple "protocols" to communicate with `ug 135`. You can send files (from local to remote) via `send_file(local_path, remote_path)` and retrieve files via `await_file(remote_path, local_path)`. Additionaly there are special functions to send and check for the `continue` signal. 
### optimizer.py
Not a very good name. `run_optimizer(*params)` will write the parameters to run the test with into `external/params.txt` and signal the ug machine to begin the test. Once the test finishes, it will record the results in `results/current/qor_{params}_.txt`
### bayes_opt.py
This is the actual optimizer. `main()` will read the current observations from `current/qor_*.txt` and store them as `train_X` and `train_Y`. The Bayesian optimization will run for however many interations specified and save the resulting plot into `plots/qor_surface.png`. 
