from send_recieve import *
import os
import shutil

m3_testers = [
	# "M3_Public_Func_Path_Cost_Interlaken_Switzerland",
	"M3_Public_Func_Inter_Inter_Simple_Legality_Interlaken_Switzerland",
	"M3_Public_Func_Inter_Inter_Simple_Optimality_Interlaken_Switzerland",
	"M3_Public_Func_Inter_Inter_Legality_Interlaken_Switzerland",
	"M3_Public_Func_Inter_Inter_Optimality_Interlaken_Switzerland",
	# "M3_Public_Func_Path_Cost_Toronto_Canada",
	"M3_Public_Func_Inter_Inter_Simple_Legality_Toronto_Canada",
	"M3_Public_Func_Inter_Inter_Simple_Optimality_Toronto_Canada",
	"M3_Public_Func_Inter_Inter_Legality_Toronto_Canada",
	"M3_Public_Func_Inter_Inter_Optimality_Toronto_Canada",
	# "M3_Public_Func_Path_Cost_London_England",
	"M3_Public_Func_Inter_Inter_Simple_Legality_London_England",
	"M3_Public_Func_Inter_Inter_Simple_Optimality_London_England",
	"M3_Public_Func_Inter_Inter_Legality_London_England",
	"M3_Public_Func_Inter_Inter_Optimality_London_England",
	# "M3_Public_Valgrind",
	# "M3_Public_Perf_Load_Map",
	"M3_Public_Perf_Inter_Inter_Medium_Toronto",
	"M3_Public_Perf_Inter_Inter_Hard_Toronto",
	"M3_Public_Perf_Inter_Inter_Very_Hard_Toronto",
	"M3_Public_Perf_Inter_Inter_Medium_London_England",
	"M3_Public_Perf_Inter_Inter_Hard_London_England",
	"M3_Public_Perf_Inter_Inter_Very_Hard_London_England"
]

# cooling rate [0.8, 1)
# perturbations [5k, 10k]

def clear_dir(dir):
    for item in os.listdir(dir):
        item_path = os.path.join(dir, item)
        if os.path.isfile(item_path):
            os.unlink(item_path)

def run_optimizer(cr, pert):
    remote_path = "/nfs/ug/homes-4/w/wangja58/ece297/work/mapper/optimizer/"
    clear_dir("./results/")

    # with open("./external/params.txt", "w") as file:
    #     file.write(f"alpha={alpha}\n")

    # make sure previous continue is dealt with
    while check_continue():
        pass

    send_continue()

    # write params to send
    with open("./external/params.txt", "w") as file:
        file.write(f"cr={cr}\n")
        file.write(f"pert={pert}\n")
    
    print("Sending params.txt")
    send_file("./external/params.txt", remote_path + "external/params.txt")

    await_file(remote_path + "results/qor.txt", "./results/qor.txt")
    # for m3_tester in m3_testers:
    #     await_file(remote_path + "results/" + m3_tester + ".txt", "./results/" + m3_tester + ".txt")

    print("Moving results to current/")
    shutil.move("./results/qor.txt", f"./current/qor_{cr}_{pert}.txt")

    send_continue()

if __name__ == "__main__":
    run_optimizer(10, 3)
    # remote_path = "/nfs/ug/homes-4/w/wangja58/ece297/work/mapper/optimizer/"
    # await_file(remote_path + "results/qor.txt", "./results/qor.txt")
