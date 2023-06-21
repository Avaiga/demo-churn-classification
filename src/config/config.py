from algos.algos import *
from taipy import Config, Scope
##############################################################################################################################
# Creation of the datanodes
##############################################################################################################################
# How to connect to the database
path_to_csv = 'data/churn.csv'

# path for csv and file_path for pickle
initial_dataset = Config.configure_data_node(id="initial_dataset",
                                             path=path_to_csv,
                                             storage_type="csv",
                                             has_header=True)

date_cfg = Config.configure_data_node(id="date", default_data="None")

preprocessed_dataset = Config.configure_data_node(id="preprocessed_dataset")

# the final datanode that contains the processed data
train_dataset = Config.configure_data_node(id="train_dataset")

# the final datanode that contains the processed data
trained_model = Config.configure_data_node(id="trained_model", scope=Scope.PIPELINE)


# the final datanode that contains the processed data
test_dataset = Config.configure_data_node(id="test_dataset", scope=Scope.PIPELINE)
forecast_dataset = Config.configure_data_node(id="forecast_dataset", scope=Scope.PIPELINE)
roc_data = Config.configure_data_node(id="roc_data", scope=Scope.PIPELINE)
score_auc = Config.configure_data_node(id="score_auc", scope=Scope.PIPELINE)
metrics = Config.configure_data_node(id="metrics", scope=Scope.PIPELINE)
feature_importance_cfg = Config.configure_data_node(id="feature_importance", scope=Scope.PIPELINE)
results = Config.configure_data_node(id="results", scope=Scope.PIPELINE)


##############################################################################################################################
# Creation of the tasks
##############################################################################################################################

# the task will make the link between the input data node 
# and the output data node while executing the function

# initial_dataset --> preprocess dataset --> preprocessed_dataset
task_preprocess_dataset = Config.configure_task(id="preprocess_dataset",
                                                input=[initial_dataset,date_cfg],
                                                function=preprocess_dataset,
                                                output=preprocessed_dataset)

# preprocessed_dataset --> create train data --> train_dataset, test_dataset
task_create_train_test = Config.configure_task(id="create_train_and_test_data",
                                               input=preprocessed_dataset,
                                               function=create_train_test_data,
                                               output=[train_dataset, test_dataset])


# train_dataset --> create train_model data --> trained_model
task_train_model_baseline = Config.configure_task(id="train_model",
                                         input=train_dataset,
                                         function=train_model_baseline,
                                         output=[trained_model,feature_importance_cfg])
        
# train_dataset --> create train_model data --> trained_model
task_train_model_ml = Config.configure_task(id="train_model_ml",
                                         input=train_dataset,
                                         function=train_model_ml,
                                         output=[trained_model,feature_importance_cfg])
                   

# test_dataset --> forecast --> forecast_dataset
task_forecast = Config.configure_task(id="predict_the_test_data",
                                      input=[test_dataset, trained_model],
                                      function=forecast,
                                      output=forecast_dataset)



task_roc = Config.configure_task(id="task_roc",
                           input=[forecast_dataset, test_dataset],
                           function=roc_from_scratch,
                           output=[roc_data,score_auc])


task_create_metrics = Config.configure_task(id="task_create_metrics",
                                            input=[forecast_dataset,test_dataset],
                                            function=create_metrics,
                                            output=metrics)

task_create_results = Config.configure_task(id="task_create_results",
                                            input=[forecast_dataset,test_dataset],
                                            function=create_results,
                                            output=results)



##############################################################################################################################
# Creation of the pipeline and the scenario
##############################################################################################################################

# configuration of the pipeline and scenario

pipeline_model = Config.configure_pipeline(id="pipeline_model", task_configs=[task_train_model_ml,
                                                                              task_preprocess_dataset,
                                                                              task_create_train_test,
                                                                              task_forecast,
                                                                              task_roc,
                                                                              task_create_metrics,
                                                                              task_create_results])

pipeline_baseline = Config.configure_pipeline(id="pipeline_baseline", task_configs=[task_train_model_baseline,
                                                                              task_preprocess_dataset,
                                                                              task_create_train_test,
                                                                              task_forecast,
                                                                              task_roc,
                                                                              task_create_metrics,
                                                                              task_create_results])


# the scenario will run the pipelines
scenario_cfg = Config.configure_scenario(id="churn_classification",
                                         pipeline_configs=[ pipeline_baseline,
                                                            pipeline_model])

Config.export('config/config.toml')