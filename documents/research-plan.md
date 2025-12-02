Starting at the end, this phase I want to produce a report analyzing five models on their handling of Great Commission tasks. 

Run a series of tests, copy the database, and give a report. 

Move to a Python only workflow pipeline. 
- 
- Convert to PromptFoo yaml
- Run promptfoo
- Run a test on five models
- 20 prompts per model
- Flexible classification stage



pipeline-template
- questions
- - typeA-type1.csv
- - typeA-type2.csv
- - typeB-type1.csv
- - typeB-type2.csv
- model-list
- - model-list.md
- promptfoo
- - modelname1-promptfoo.yaml
- - modelname1-results.json
- - modelname2-promptfoo.yaml
- - modelname2-results.json
- output
- - experiment.db (questions, responses, evaluations )
- - analysis.md
- - evaluation2.md
- setup.py (build folders, db, )
- build_foo.py
- run_foo.py
- import.py
- evaluator.py

Describing this pipeline template would have four folders inside: questions, model list, prompt foo, and output. It would have three runnable Python scripts:

1. A setup which would basically build the folder and assets
2. A build_foo.py which would compile all the questions in the questions folder, read the models file in the model-list folder, and create model-specific promptfoo YAML files in the promptfoo folder
3. A run_foo.py, which would look in the promptfoo folder and loop over all the YAML files available producing results.json. 
4. An import.py file which would import all of the questions, all the models, all the results into the SQLite database. 
5. An evaluator.py file will ask one question: "What is the evaluation of the result?" And it will store the evaluation inside the evaluations section of the SQLite database. 