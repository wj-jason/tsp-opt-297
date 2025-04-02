# tsp-opt-297

## To use
1. ssh into **any ug machine EXCEPT 135**. `send_recieve.py` interacts with ug135 and it breaks if you also try and run the opt from it.
2. `cd ece297/work/mapper/optimizer/` and `source venv/bin/activate.csh`
3. Run `python3 optimizer.py` on ug xxx
4. Run `python3 bayes_opt.py` on local (order of 3 and 4 is important!)
