# Large language models possess some ecological knowledge, but how much? 🌿🤖
Code for evaluating large language models (LLMs) such as Gemini and GPT-4 on ecological tasks. This code enables the recreation of the results from our preprint [Large language models possess some ecological knowledge, but how much?](https://www.biorxiv.org/content/10.1101/2025.02.10.637097v1).

## 🌍 Overview
![](images/eco-llm.drawio.png)

We assess LLMs on species presence prediction, range mapping, endangered species listing, threat classification, and trait estimation, benchmarking their performance against expert datasets. While LLMs outperform naive baselines, they struggle with spatial accuracy and threat classification, highlighting the need for domain-specific fine-tuning.

The provided benchmark dataset enables systematic evaluation and improvement of ecological reasoning in future models.

## 🔍 Getting Started
This project includes tasks that rely on specific JSON and CSV files, which are provided along with the code. You can recreate these files using the provided scripts. Notebooks for generating the plots used in the paper are also available.

### Installing Required Packages

1. We recommend using an isolated Python environment to avoid dependency issues. Install the Anaconda Python 3.9 distribution for your operating system from [here](https://www.anaconda.com/download). 

2. Create a new environment and activate it:
```bash
 conda create -y --name eco-llm python==3.9
 conda activate eco-llm
```

3. After activating the environment, install the required packages:
```bash
 pip3 install -r requirements.txt
```

### Requirements:
To query the models, you'll need to include your own `.env` file with API keys for both Gemini and GPT. You can obtain them from the following links:
- [Gemini API Key](https://aistudio.google.com/app/apikey)
- [GPT API Key](https://openai.com/index/openai-api)

Additionally, you need an IUCN API-key. Examples of API usage, and key, can be found [here](https://apiv3.iucnredlist.org/api/v3/docs).

Your `.env` file should look something like this:
```bash
OPENAI_API_KEY=?
GEMINI_API_KEY=?
IUCN_API_KEY=?
```

### Required Files:
You can recreate the following files yourself, with instructions provided in each task’s section. The species used for each task can be found in `SPECIES.md`:
- `queries.json`: Template queries used in the project.
- `data/meta_data/iucn_species_names.json`: Species common and scientific names.
- `data/meta_data/inat_iucn_conversion.json`: Species common and scientific names.

  
#### Task 1:
- `task_data/task1/task1_coordinates.json`: Species and associated coordinates.
- `task_data/task1/task1_countries.json`: Species and associated countries.

#### Task 3:
- `task_data/task3/birds_CR.csv`: Critically endangered birds and the countries they inhabit.

#### Task 4:
- `task_data/task4/iucn_threats.json`: Critically endangered species and the threats they face.

#### Task 5:
- `task_data/task5/task5_bird_traits.csv`: Traits extracted for birds from AVONET.
- `task_data/task5/task5_mammal_traits.csv`: Traits extracted for mammals from COMBINE dataset.


## 🤖 Querying the model:
All tasks rely on the following two scripts.

<ins>Query the model</ins>:
```bash
python interact_w_model.py [--llm {gemini,gpt}] [--task {1a,1b,2,3,4,5a,5b}] [--prompt_version PROMPT_VERSION]
                           [--exp_name EXP_NAME]
```

## 📊 Evaluate the model:

1. Update `EVAL_FILE_PATH` in `eval_responses.py` to point to required responses.
2. ```bash
    python eval_responses.py eval_responses.py [--task {1a,1b,2,3,4,5a,5b}]
    ```

## 🔁 Create required files yourself:
##### `data/meta_data/iucn_species_names.json`
`cd` to data folder and run `inat_names_iucn.py`
you need the file `gt_data/iucn_res_5.json`, which can be downloaded by running:

```bash 
curl -L https://data.caltech.edu/records/b0wyb-tat89/files/data.zip --output data.zip
```
##### `data/meta_data/inat_iucn_conversion.json`
First we need to follow above step to create `iucn_species_names.json`.
```bash 
cd data/task1
python iucn_inat_ids.py
```

##### `task_data/task1/task1_coordinates.json`
```bash 
cd task_data/task1
python dataset_creation_coords.py
```
##### `task_data/task1/task1_countries.json`
```bash 
cd task_data/task1
python countries_extraction.py
python dataset_creation_coords.py
```

##### `task_data/task3/birds_CR.csv`
In order to create this csv file, `common_groups.csv` and `countries_w_species` need to be created. 
```bash 
cd task_data/task3
python countries_w_species.py
python groups_extract.py
python create_birds_CR.py
```

##### `task_data/task4/iucn_threats.json`
```bash 
cd task_data/task4
python threats_extraction.py
```

##### `task_data/task5/task5_bird_traits.csv` and`task_data/task5/task5_mammal_traits.csv`:
Download AVONET and COMBINE datasets from: 
* https://opentraits.org/datasets/avonet.html
* https://esajournals.onlinelibrary.wiley.com/doi/full/10.1002/ecy.3344#support-information-section
```bash 
cd task_data/task5
python create_task5_datasets.py
```

##  🙏 Citation
```
@article{Dorm2025,
  author = {Filip Dorm and Joseph Millard and Drew Purves and Michael Harfoot and Oisin Mac Aodha},
  title = {Large language models possess some ecological knowledge, but how much?},
  journal = {bioRxiv},
  year = {2025},
  doi = {10.1101/2025.02.10.637097},
  url = {https://doi.org/10.1101/2025.02.10.637097},
  publisher = {Cold Spring Harbor Laboratory}
}
```




