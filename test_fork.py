import multiprocessing as mp

def worker():
    print("child process ran successfully")

if __name__ == "__main__":
    ctx = mp.get_context("forkserver")
    p = ctx.Process(target=worker)
    p.start()
    p.join()
    print("exit code:", p.exitcode)
