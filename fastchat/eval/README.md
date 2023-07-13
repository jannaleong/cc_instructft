# Evaluations

This directory contains end-to-end pipelines for AI-enhanced evaluation. We will introduce the evaluation pipeline and the data format in this document.

## Generate Answers

### Vicuna and others

To generate answers with Vicuna or other models, specify path to the model checkpoint, a desired model ID and run:
```bash
python get_model_answer.py --model-id [MODEL-ID] --model-path /model/path --question-file table/question.jsonl --answer-file table/answer/answer.jsonl --num-gpus [NUM-GPUS]
```
Then the answers to the questions will be saved in `table/answer/answer.jsonl`.
Note: we assume the model can be loaded with a single GPU.

## Evaluate Answers Automatically

### Generete Reviews with GPT-4

Note: Below script requires access to GPT-4 API. If you only have access to GPT-4 on web interface, you can evaluate the answers by manually formatting the prompt. See more details in the **Reviewers** and **Prompts** sections in **Data Format**.
It is critical to follow the prompt templates; otherwise GPT-4 may not give fair reviews. `table/review/*.jsonl` are some review examples generated by GPT-4 or you can view them on our eval [webpage](https://vicuna.lmsys.org/eval/).

To use the script for generating reviews with GPT-4, you need to `export` your OpenAI API key in environment variable. Then run:
```bash
python eval_gpt_review.py -q table/question.jsonl -a /path/to/answer_1.jsonl /path/to/answer_2.jsonl -p table/prompt.jsonl -r table/reviewer.jsonl -o /path/to/review_output.jsonl
```
The GPT-4 reviews will be saved in `/path/to/review_output.jsonl`. Note: we implement some simple parsing code to extract the score pairs from GPT-4's reviews. However, you need to double check whether the parsed score pair are correct. Sometime the parsing logic may fail if GPT-4 doesn't give a structured answer.

## Visualize Results

You can generate the data for the webpage by running:

```bash
python eval/generate_webpage_data_from_table.py
```

Then you can serve a static website in `webpage` to see the results.

## Data Format

If you want to have a deeper understanding of our evaluation pipeline or want to contribute to the evaluation process, you need to learn the data format we used for evaluation.

Our evaluation data are encoded with [JSON Lines](https://jsonlines.org/).

### Random ID Generation

We use the `shortuuid` Python library for generating short random UUIDs.

```python
import shortuuid
shortuuid.uuid() -> str
```

### Models

`model.jsonl` contains model information we used for generating anwsers.

Each row contains a record of a model with the following field:

* `model_id` (str): A unique ID for a model. Models with different IDs is supposed to have different performance. This ID is generated by `{model_name}:{model_version}`.
* `model_name` (str): The name of a model. This is not unique, because a model could be trained and updated continuously, but it is still considered as the same model with different versions.
* `model_version` (str): The version of a model.
* `model_metadata` (Any): Any metadata of a model (descriptions etc). This is optional.

For example:

```json
{
  "model_id": "vicuna-13b:v1",
  "model_name": "vicuna-13b",
  "model_version": "v1",
  "model_metadata": "learning rate 1e-5, 3 epochs, 13b"
}
```

### Prompts

We store prompts in `prompt.jsonl`. Each row contains a record of a prompt with the following field:

* `prompt_id` (int): A unique integer ID for a prompt. Prompts with different IDs are supposed to have different purpose.
* `system_prompt` (str): The system prompt given to a model. This is the prompt that the model sees first.
* `prompt_template` (str): The prompt body. This is the user prompt that the model sees after the system prompt. It is a Python f-string template, so that we can fill in the inputs later.
* `defaults` (dict): A dictionary of default values for the prompt template. It can be empty.
* `description` (str): A description of the functionality of the prompt.

For example:

```json
{
  "prompt_id": 1,
  "system_prompt": "You are a helpful assistant.",
  "prompt_template": "[Question]\n{question}\n\n[Assistant 1]\n{answer_1}\n\n[End of Assistant 1]\n\n[Assistant 2]\n{answer_2}\n\n[End of Assistant 2]\n\n[System]\n{prompt}\n\n",
  "defaults": {"prompt": "Which assistant is more helpful?"},
  "description": "Compare two assistants' answers to a question."
}
```

### Reviewers

`reviewer.jsonl` contains reviewer information we used for reviewing answers generated by different models. Each row contains a record of a reviewer with the following field:

* `reviewer_id` (str): A unique ID for a reviewer. Reviewers with different IDs is supposed to have different reviewing performance.
* `prompt_id` (str): The ID of the prompt given to the reviewer (e.g., an AI assistant). Different prompts could result in different reviewing performance.
* `metadata` (dict): Metadata of a reviewer about its configurations.
* `description` (str): A description of the reviewer.
* `category` (str): The category that the reviewer belongs to.

For example:

```json
{
  "reviewer_id": "gpt-4-0328-default",
  "prompt_id": 1,
  "temperature": 0.2,
  "max_tokens": 8192,
  "description": "GPT-4 for general questions.",
  "category": "general"
}
```

### Questions

`question.jsonl` contains questions we used for evaluation. Each row contains a record of a question with the following field:

* `question_id` (int): A unique integer for a question. Questions with different IDs is supposed to be different.
* `text` (str): The question text.
* `category` (str): The category of the question. Questions with the same category are supposed to be similar or originate from the same source.

### Answers

`answer/xxx.jsonl` contains answers generated by different models. Each row contains a record of an answer with the following field:

* `answer_id` (str): A unique UUID for an answer. Answers with different IDs is supposed to be different.
* `question_id` (int): The ID of the question the answer is generated for.
* `model_id` (str): The ID of the model the answer is generated by.
* `text` (str): The answer text.
* `metadata` (dict): Any metadata of the answer.

Example:

```json
{
  "answer_id": "[short uuid]",
  "question_id": 1,
  "model_id": "vicuna-13b:v1",
  "text": "Here are five tips...",
  "metadata": {}
}
```

### Reviews

`review/xxx.jsonl` contains reviews given by reviewers, comparing peformance between a pair of models. Each row contains a record of a review with the following field:

* `review_id` (str): A unique UUID for a review. Reviews with different IDs is supposed to be different.
* `question_id` (int): The ID of the question the review is given for.
* `answer1_id` (str): The ID of the first answer.
* `answer2_id` (str): The ID of the second answer.
* `text` (str): The review text.
* `score` (list): A list of scores given by the reviewer. The first score is for the first answer, and the second score is for the second answer.
* `reviewer_id` (str): The ID of the reviewer.
* `metadata` (dict): Any metadata of the review.

```json
{
  "review_id": "[short uuid]",
  "question_id": 1,
  "answer1_id": "[answer1_id]",
  "answer2_id": "[answer2_id]",
  "text": "Assistant 2 is better...",
  "score": [9.0, 7.5],
  "reviewer_id": "gpt-4-0328-default",
  "metadata": {}
}
```