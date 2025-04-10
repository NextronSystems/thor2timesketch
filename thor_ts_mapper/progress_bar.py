from tqdm import tqdm


class ProgressBar:
    def __init__(self, desc: str):
        self.desc = desc
        self.events_count = 0
        self.pbar = tqdm(unit=" event", desc=self.desc, dynamic_ncols=True)

    def update(self, num: int = 1):
        self.events_count += num
        self.pbar.update(num)
        self.pbar.set_postfix({"processed": self.events_count})

    def close(self):
        self.pbar.close()