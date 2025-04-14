# IDesign
It's an updated version of [*I-Design: Personalized LLM Interior Designer*](https://atcelen.github.io/I-Design/) that can process multiple prompts 🎊**in one run**🎊.

> Following are adapted from the instructions of [I-Design](https://atcelen.github.io/I-Design/).
## Requirements
Install the requirements
```bash
conda create -n idesign python=3.9
conda activate idesign
pip install -r requirements.txt
conda install pytorch==1.12.1 torchvision==0.13.1 torchaudio==0.12.1 cudatoolkit=11.3 -c pytorch
pip install -U git+https://github.com/NVIDIA/MinkowskiEngine
conda install -c dglteam/label/cu113 dgl
```
Create the "OAI_CONFIG_LIST.json" file
```json
[
    {
        "model": "gpt-4",
        "api_key": "YOUR_API_KEY"
    },
    {
        "model": "gpt-4-1106-preview",
        "api_key": "YOUR_API_KEY"
    },
    {
        "model": "gpt-3.5-turbo-1106",
        "api_key": "YOUR_API_KEY",
        "api_version": "2023-03-01-preview"
    }
]
```
## Inference

Complete the retrieval environment building in advance. Retrieve the 3D assets from Objaverse using OpenShape
```
git clone https://huggingface.co/OpenShape/openshape-demo-support
cd openshape-demo-support
pip install -e .
cd ..
```
**Add the prompt you want to run in `prompt.txt` and run `IDesign.sh`!**

## Evaluation
After creating scene renders in Blender, you can use the GPT-V evaluator to generate grades for evaluation. Fill in the necessary variables denoted with TODO and run the script
```bash
python gpt_v_as_evaluator.py
```

## Results
![gallery](imgs/gallery.jpg)

ps: this code will save final blender file in `results`.
