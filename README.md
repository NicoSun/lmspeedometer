# lmspeedometer
A simple Python tool to benchmark LLMs with LM Studio.
Supports loading speed and token per second.


## Usage
- create a new Python venv with requirements.txt

- start LM Studio and set up your desired runtime and model settings
- activate the venv and run main.py
- select the models you want to bench

### Tips for AMD iGPUs
On Linux, by default the iGPU can use 50% of the RAM (GTT allocation). But you can increase it with kernel parameters.
You have to calculate the number of 4KB memory pages to allocate.

The formula is:
```
[Size in GB] * 1024 * 1024 * 1024 / 4096 = ttm_pages
```


**Example:**
```
38 * 1024 * 1024 * 1024 / 4096 = 9961472
```
Then run the bash commands:

```bash
sudo grubby --update-kernel=ALL --args='ttm.pages_limit=9961472'
sudo grubby --update-kernel=ALL --args='ttm.page_pool_size=9961472'
```

> **Note:** If your boot fails due to a bad value, you can edit or delete the changes in the GRUB menu.